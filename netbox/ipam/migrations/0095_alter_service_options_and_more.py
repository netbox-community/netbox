import django.contrib.postgres.fields
import django.contrib.postgres.indexes
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


def populate_port_mappings(apps, schema_editor):
    """
    Build the new ``port_mappings`` array (e.g. ['tcp/80', 'tcp/443']) from the legacy protocol/ports
    fields on each Service/ServiceTemplate. Processed in batches to bound memory on large installs.

    Services/templates that had an empty ``ports`` array (technically invalid under the old schema, but
    possible via direct DB writes) are left with ``port_mappings=[]``, which the new model rejects on the
    next save. Operators can find any such records post-migration with, e.g.:
        SELECT id, name FROM ipam_service WHERE port_mappings = '{}';
        SELECT id, name FROM ipam_servicetemplate WHERE port_mappings = '{}';
    """
    for model_name in ('Service', 'ServiceTemplate'):
        model = apps.get_model('ipam', model_name)
        batch = []
        for obj in model.objects.filter(ports__len__gt=0).iterator(chunk_size=1000):
            # dict.fromkeys dedupes while preserving order (legacy ports weren't guaranteed unique),
            # so a duplicated port doesn't produce a duplicate mapping that later fails validation.
            obj.port_mappings = list(dict.fromkeys(f'{obj.protocol}/{port}' for port in obj.ports))
            batch.append(obj)
            if len(batch) >= 1000:
                model.objects.bulk_update(batch, ['port_mappings'])
                batch = []
        if batch:
            model.objects.bulk_update(batch, ['port_mappings'])


def restore_legacy_fields(apps, schema_editor):
    """
    Reverse of ``populate_port_mappings``: rebuild the legacy protocol/ports/_ports_lowest columns from
    ``port_mappings`` so the migration can be rolled back on a populated database.

    The legacy schema stores a *single* protocol per service, whereas ``port_mappings`` can hold several.
    A service that predates the upgrade only ever has one protocol, so this reconstruction is lossless
    for it. A service that used the new multi-protocol capability keeps only the **first** mapping's
    protocol (and every port belonging to it) on rollback; mappings for any other protocol cannot be
    represented by the old schema and are dropped. This is the expected, documented cost of downgrading.

    Runs before the AlterField operations restore NOT NULL on protocol/ports (see the operation order
    below), so every row is populated before the constraints are re-applied. Records with an empty
    ``port_mappings`` become protocol='' / ports=[] (an empty array is still non-NULL).
    """
    for model_name in ('Service', 'ServiceTemplate'):
        model = apps.get_model('ipam', model_name)
        batch = []
        for obj in model.objects.iterator(chunk_size=1000):
            protocol = ''
            ports = []
            for entry in obj.port_mappings:
                entry_protocol, _, entry_port = entry.partition('/')
                if not protocol:
                    protocol = entry_protocol
                # Keep only the first protocol's ports; the legacy schema can't hold more than one.
                if entry_protocol == protocol and entry_port.isdigit():
                    port = int(entry_port)
                    if port not in ports:
                        ports.append(port)
            obj.protocol = protocol
            obj.ports = ports
            obj._ports_lowest = min(ports) if ports else None
            batch.append(obj)
            if len(batch) >= 1000:
                model.objects.bulk_update(batch, ['protocol', 'ports', '_ports_lowest'])
                batch = []
        if batch:
            model.objects.bulk_update(batch, ['protocol', 'ports', '_ports_lowest'])


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0141_custom_field_nulls_first"),
        ("ipam", "0094_denormalization_triggers"),
        ("users", "0016_default_ordering_indexes"),
    ]

    operations = [
        # Add the new field to both models first
        migrations.AddField(
            model_name="service",
            name="port_mappings",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=63), blank=True, default=list
            ),
        ),
        migrations.AddField(
            model_name="servicetemplate",
            name="port_mappings",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=63), blank=True, default=list
            ),
        ),
        # Relax NOT NULL on the legacy protocol/ports columns before migrating the data. This makes the
        # migration reversible on a populated database: on reverse, the RemoveField operations below
        # re-add these columns as nullable (so ADD COLUMN succeeds without a default), restore_legacy_fields
        # then backfills them from port_mappings, and finally these AlterField operations restore NOT NULL
        # (running last on reverse, once every row has a value). Placed before the RunPython so their
        # reverse executes after the data backfill.
        migrations.AlterField(
            model_name="service",
            name="protocol",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="service",
            name="ports",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.PositiveIntegerField(
                    validators=[MinValueValidator(1), MaxValueValidator(65535)]
                ),
                null=True,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="servicetemplate",
            name="protocol",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="servicetemplate",
            name="ports",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.PositiveIntegerField(
                    validators=[MinValueValidator(1), MaxValueValidator(65535)]
                ),
                null=True,
                size=None,
            ),
        ),
        # Migrate existing protocol/ports data into port_mappings before dropping the old fields. The
        # reverse (restore_legacy_fields) reconstructs the legacy columns from port_mappings, keeping only
        # the first protocol's ports (the legacy schema holds a single protocol) — see its docstring.
        migrations.RunPython(populate_port_mappings, restore_legacy_fields),
        migrations.AlterModelOptions(
            name="service",
            options={"ordering": ("name", "id")},
        ),
        migrations.RemoveIndex(
            model_name="service",
            name="ipam_servic_protoco_e2901d_idx",
        ),
        migrations.AddIndex(
            model_name="service",
            index=models.Index(
                fields=["name", "id"], name="ipam_servic_name_b3260b_idx"
            ),
        ),
        migrations.RemoveField(
            model_name="servicetemplate",
            name="_ports_lowest",
        ),
        migrations.RemoveField(
            model_name="servicetemplate",
            name="ports",
        ),
        migrations.RemoveField(
            model_name="servicetemplate",
            name="protocol",
        ),
        migrations.RemoveField(
            model_name="service",
            name="_ports_lowest",
        ),
        migrations.RemoveField(
            model_name="service",
            name="ports",
        ),
        migrations.RemoveField(
            model_name="service",
            name="protocol",
        ),
        # GIN indexes supporting exact protocol/port containment lookups (port_mappings @> ['tcp/80'])
        migrations.AddIndex(
            model_name="service",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["port_mappings"], name="ipam_servic_port_ma_a3d51d_gin"
            ),
        ),
        migrations.AddIndex(
            model_name="servicetemplate",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["port_mappings"], name="ipam_servic_port_ma_39e070_gin"
            ),
        ),
    ]
