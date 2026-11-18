import logging

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import router, transaction
from django.utils import timezone
from django.utils.translation import gettext as _

from ndx.choices import ImportRecordSourceChoices
from ndx.client import RATE_LIMITED, error_of, get_client
from utilities.exceptions import AbortRequest, PermissionsViolation

from .base import *
from .utils import UNEXPECTED_ERROR, enforce_object_permission, upsert

__all__ = (
    'ImportAborted',
    'ImportResult',
    'ImportSkipped',
    'Importer',
    'get_importer',
    'get_importers',
    'get_vendor_checksums',
    'import_entries',
    'register_core_importers',
    'register_importer',
)

logger = logging.getLogger('netbox.ndx.importers')

# Enrichment fields populated from each section of the catalog's enrichment data
ENRICHMENT_FIELDS = {
    'thermal': ('tdp_watts', 'airflow_cfm', 'cooling_type'),
    'lifecycle': ('ga_date', 'eol_announced', 'eos_date', 'eosw_date', 'eosec_date', 'last_support_date'),
    'environmental': (
        'max_operating_temp_c', 'min_operating_temp_c', 'max_operating_humidity', 'min_operating_humidity',
        'max_operating_altitude_m', 'ingress_protection', 'mtbf_hours',
    ),
    'operational': ('typical_power_draw_watts', 'max_power_draw_watts', 'noise_level_dba'),
}
ENRICHMENT_FLAGS = ('lifecycle', 'thermal', 'environmental', 'operational', 'platform', 'snmp')


class ImportAborted(Exception):
    """
    Raised when an import cannot proceed (e.g. because the catalog manifest is unavailable).
    """
    def __init__(self, error):
        self.error = error
        super().__init__(error.message)


def register_core_importers():
    """
    Register the importers for NetBox's built-in object types.
    """
    from . import dcim  # noqa: F401


def get_vendor_checksums(client):
    """
    Return a tuple of the per-vendor checksums from the catalog manifest, and the NDXError if it couldn't be retrieved.
    Checksums are needed to detect catalog updates later. A rate-limited manifest is tolerated, as each entry reports
    its own outcome (an entry imported without a checksum is flagged for update only once it can be compared).
    """
    manifest = client.get_manifest()
    error = error_of(manifest)
    if error is not None and error.kind != RATE_LIMITED:
        return {}, error
    return manifest.get('vendor_checksums') or {}, None


def import_entries(ndx_ids, user, client=None, callback=None, checksums=None):
    """
    Import the given catalog entries (identified as "<vendor_slug>/<slug>") on behalf of a user. Returns a list of
    ImportResults, passing each to `callback` (if given) as it completes. Unless vendor checksums are provided, they
    are retrieved from the catalog manifest; ImportAborted is raised if it cannot be retrieved.
    """
    client = client or get_client()
    if checksums is None:
        checksums, error = get_vendor_checksums(client)
        if error is not None:
            raise ImportAborted(error)

    results = []
    for ndx_id in ndx_ids:
        results.append(result := import_entry(ndx_id, user, client, checksums))
        if callback is not None:
            callback(result)
    return results


def import_entry(ndx_id, user, client, checksums):
    """
    Import a single catalog entry and return an ImportResult.
    """
    result = ImportResult(ndx_id=ndx_id)

    vendor_slug, _sep, slug = ndx_id.partition('/')
    if not vendor_slug or not slug or '/' in slug:
        result.errors.append(_("Invalid NDX ID"))
        return result

    entry = client.get_entry(vendor_slug, slug)
    if error := error_of(entry):
        result.errors.append(str(error.message))
        return result

    # The catalog treats an entry with no type as a device type
    result.entry_type = entry.get('type') or 'device-type'
    importer = get_importer(result.entry_type)
    if importer is None:
        result.errors.append(_("Unsupported entry type: {type}").format(type=result.entry_type))
        return result
    result.name = importer.get_name(entry)

    # Prefer the object already tracked for this entry, which may have been modified locally
    instance = get_tracked_object(importer, ndx_id) or importer.find_existing(entry)
    if instance is not None and (other := get_other_record(instance, ndx_id)):
        result.skipped = True
        result.message = _("Skipped: {object} is already tracked by catalog entry {ndx_id}.").format(
            object=instance, ndx_id=other.ndx_id
        )
        return result
    if not user.has_perms(importer.get_required_permissions(entry, instance)):
        result.errors.append(_("Permission denied"))
        return result

    model = importer.model
    try:
        with transaction.atomic(using=router.db_for_write(model)):
            obj = importer.import_entry(entry, instance, user, result)

            # Enforce object-level permissions
            enforce_object_permission(obj, user, 'change' if instance else 'add')

            record = update_import_record(obj, ndx_id, entry, checksums, result)
            update_enrichment(record, entry, result)

    except ImportSkipped as e:
        result.skipped = True
        result.message = _("Skipped: {reason}").format(reason=e)
        return result
    except PermissionsViolation:
        result.errors.append(_("Permission denied"))
        return result
    except (AbortRequest, ValidationError) as e:
        result.errors.extend(getattr(e, 'messages', None) or [str(e)])
        return result
    except Exception:
        # Details of an unexpected error are logged, but not reported
        logger.exception(f"Failed to import {ndx_id}")
        result.errors.append(UNEXPECTED_ERROR)
        return result

    result.success = True
    result.created = instance is None
    result.object = obj
    result.message = (_("Created {name}") if result.created else _("Updated {name}")).format(name=result.name)

    # Remote fetches (e.g. images) happen after the object has been committed, so a failure is reported but does not
    # undo the import
    try:
        importer.post_import(obj, entry, client, result)
    except Exception:
        logger.exception(f"Post-import processing failed for {ndx_id}")
        result.warnings.append(_("Post-import processing failed. {error}").format(error=UNEXPECTED_ERROR))

    return result


def get_tracked_object(importer, ndx_id):
    """
    Return the existing object tracked by the import record for a catalog entry, if any.
    """
    from ndx.models import ImportRecord

    record = ImportRecord.objects.filter(
        ndx_id=ndx_id,
        object_type=ContentType.objects.get_for_model(importer.model),
    ).first()
    if record is None:
        return None
    return importer.model.objects.filter(pk=record.object_id).first()


def get_other_record(obj, ndx_id):
    """
    Return the import record of a different catalog entry which tracks the given object, if any.
    """
    from ndx.models import ImportRecord

    return ImportRecord.objects.filter(
        object_type=ContentType.objects.get_for_model(obj),
        object_id=obj.pk,
    ).exclude(ndx_id=ndx_id).first()


def update_import_record(obj, ndx_id, entry, checksums, result):
    """
    Create or update the ImportRecord tracking an imported object.
    """
    from ndx.models import ImportRecord

    vendor_slug = ndx_id.partition('/')[0]
    source = entry.get('source', '')
    if source not in ImportRecordSourceChoices.values():
        source = ''
    record, _created = upsert(
        ImportRecord,
        {'ndx_id': ndx_id},
        {
            'object_type': ContentType.objects.get_for_model(obj),
            'object_id': obj.pk,
            'entry_type': result.entry_type,
            'vendor_slug': vendor_slug,
            'source': source,
            'checksum': checksums.get(vendor_slug, ''),
            'update_available': False,
            'last_imported': timezone.now(),
        },
        warnings=result.warnings,
    )
    return record


def update_enrichment(record, entry, result):
    """
    Create or update the Enrichment (and its Provenance) for an import record from the catalog's enrichment data,
    which is present only for tokens entitled to it.
    """
    from ndx.models import Enrichment

    data = entry.get('enrichment') or {}
    if not data and not result.enrichment_fields:
        return None

    values = {}
    if data:
        for section, fields in ENRICHMENT_FIELDS.items():
            section_data = data.get(section) or {}
            values.update({name: section_data.get(name) for name in fields})
        extensions = data.get('extensions') or {}
        platform = extensions.get('platform') or {}
        snmp = extensions.get('snmp') or {}
        flags = entry.get('enrichment_flags') or {}
        values.update({
            'nos': platform.get('nos'),
            'nos_family': platform.get('nos_family'),
            'api_types': platform.get('api_types') or [],
            'snmp_sys_object_id': snmp.get('sys_object_id'),
            'snmp_vendor_oid_prefix': snmp.get('vendor_oid_prefix'),
            'extensions': extensions,
            **{f'has_{flag}': bool(flags.get(flag)) for flag in ENRICHMENT_FLAGS},
        })
    values.update(result.enrichment_fields)

    enrichment, _created = upsert(Enrichment, {'import_record': record}, values, warnings=result.warnings)
    if data.get('provenance'):
        update_provenance(enrichment, data['provenance'], result)
    return enrichment


def update_provenance(enrichment, provenance, result):
    """
    Reconcile an enrichment's provenance entries with the catalog's. Entries are identified by field path.
    """
    from ndx.models import Provenance

    max_length = Provenance._meta.get_field('field').max_length
    fields = set()
    for item in provenance:
        if not isinstance(item, dict):
            continue
        field = str(item.get('field') or '')
        if len(field) > max_length:
            msg = f"{Provenance._meta.verbose_name}: rejected field {field!r} (exceeds maximum length of {max_length})"
            logger.warning(msg)
            result.warnings.append(msg)
            continue
        fields.add(field)
        upsert(
            Provenance,
            {'enrichment': enrichment, 'field': field},
            {
                'source': item.get('source'),
                'type': item.get('type'),
                'confidence': item.get('confidence'),
                'retrieved': item.get('retrieved'),
                'note': item.get('note'),
            },
            warnings=result.warnings,
        )

    # Delete individually so that each deletion is change-logged
    for stale in Provenance.objects.filter(enrichment=enrichment).exclude(field__in=fields):
        stale.delete()
