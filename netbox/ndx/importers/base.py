import re
from dataclasses import dataclass, field

from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import pre_delete

from netbox.registry import registry

__all__ = (
    'ImportResult',
    'ImportSkipped',
    'Importer',
    'get_importer',
    'get_importers',
    'register_importer',
)

ENTRY_TYPE_RE = re.compile(r'^[a-z][a-z0-9_.-]*$')


class ImportSkipped(Exception):
    """
    Raised by an Importer to skip a catalog entry without treating it as a failure.
    """


@dataclass
class ImportResult:
    """
    The outcome of importing a single catalog entry.
    """
    ndx_id: str
    entry_type: str = ''
    name: str = ''
    success: bool = False
    created: bool = False
    skipped: bool = False
    object: object = None
    message: str = ''
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    component_errors: list = field(default_factory=list)
    image_errors: list = field(default_factory=list)
    # Additional enrichment field values derived by the importer
    enrichment_fields: dict = field(default_factory=dict)

    @property
    def status(self):
        if self.success:
            return 'created' if self.created else 'updated'
        return 'skipped' if self.skipped else 'failed'

    def serialize(self):
        """
        Return a JSON-serializable representation of the result.
        """
        obj = self.object
        return {
            'ndx_id': self.ndx_id,
            'entry_type': self.entry_type,
            'name': self.name,
            'status': self.status,
            'object_type': f'{obj._meta.app_label}.{obj._meta.model_name}' if obj else None,
            'object_id': obj.pk if obj else None,
            'message': self.message,
            'errors': self.errors,
            'warnings': self.warnings,
            'component_errors': self.component_errors,
            'image_errors': self.image_errors,
        }


class Importer:
    """
    Base class for importing a type of NDX catalog entry as a NetBox object. Subclasses must define entry_type
    (the catalog's `type` value), model, and label, and implement find_existing() and import_entry().
    """
    entry_type = None
    model = None
    label = None

    def get_name(self, entry):
        """
        Return a human-friendly name for the catalog entry.
        """
        return ' '.join(filter(None, (entry.get('manufacturer'), entry.get('model'))))

    def find_existing(self, entry):
        """
        Return the existing object which corresponds to the catalog entry, if any. Must not write to the database.
        """
        raise NotImplementedError

    def get_required_permissions(self, entry, instance):
        """
        Return the permissions a user needs to import the entry. `instance` is the existing object, if any.
        """
        app_label, model_name = self.model._meta.app_label, self.model._meta.model_name
        action = 'change' if instance else 'add'
        return {f'{app_label}.{action}_{model_name}'}

    def import_entry(self, entry, instance, user, result):
        """
        Create or update the object for a catalog entry and return it. Called within a database transaction.
        Raise ImportSkipped to skip the entry, or ValidationError if it cannot be imported.
        """
        raise NotImplementedError

    def post_import(self, obj, entry, client, result):
        """
        Perform any work which follows a successful import, outside the database transaction (e.g. fetching images).
        """
        pass


def register_importer(cls):
    """
    Register an Importer subclass. Can be used as a decorator.
    """
    if not issubclass(cls, Importer):
        raise ImproperlyConfigured(f"{cls.__name__} must be a subclass of ndx.importers.Importer.")
    instance = cls()
    for attr in ('entry_type', 'model', 'label'):
        if not getattr(instance, attr):
            raise ImproperlyConfigured(f"{cls.__name__} must define a '{attr}' attribute.")
    if not ENTRY_TYPE_RE.fullmatch(instance.entry_type):
        raise ImproperlyConfigured(
            f"Invalid entry type {instance.entry_type!r}: must be lowercase, start with a letter, and use only "
            f"letters, digits, hyphens, underscores, and periods."
        )
    if instance.entry_type in registry['ndx_importers']:
        raise ImproperlyConfigured(f"An importer for {instance.entry_type} has already been registered!")
    registry['ndx_importers'][instance.entry_type] = instance

    # Delete import records along with the objects they track
    from ndx.signals import delete_import_records
    pre_delete.connect(
        delete_import_records,
        sender=instance.model,
        dispatch_uid=f'ndx_delete_import_records_{instance.model._meta.label_lower}',
    )

    return cls


def get_importer(entry_type):
    """
    Return the registered Importer for a catalog entry type, or None.
    """
    return registry['ndx_importers'].get(entry_type)


def get_importers():
    """
    Return all registered Importers, keyed by entry type.
    """
    return dict(registry['ndx_importers'])
