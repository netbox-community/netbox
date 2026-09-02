import django.contrib.postgres.fields
import django.contrib.postgres.indexes
from django.db import migrations, models

POPULATE_PORT_MAPPINGS_SQL = """
    UPDATE {table} SET port_mappings = ARRAY(
        SELECT protocol || '/' || port
        FROM (
            -- Dedupe while preserving first-seen order: the legacy ports array wasn't guaranteed unique
            -- (the REST API accepted any list), and a duplicated port would otherwise produce a duplicate
            -- mapping that fails validation on the object's next save. NULL elements — only reachable via
            -- raw DB writes — are dropped rather than concatenated into a 'tcp/' mapping.
            SELECT port, MIN(ordinality) AS ordinality
            FROM unnest(ports) WITH ORDINALITY AS unnested(port, ordinality)
            WHERE port IS NOT NULL
            GROUP BY port
        ) AS deduped
        ORDER BY deduped.ordinality
    )
    WHERE cardinality(ports) > 0 AND protocol <> ''
"""


def populate_port_mappings(apps, schema_editor):
    """
    Build the new ``port_mappings`` array (e.g. ['tcp/80', 'tcp/443']) from the legacy protocol/ports
    fields on each Service/ServiceTemplate. Done as a single set-based UPDATE per table rather than a
    row-by-row rewrite, so the maintenance window stays bounded on large installs (this runs over every
    service and service template in the database).

    The ports column is an integer array, so every mapping this produces is already in the canonical form
    validate_port_mappings() enforces — no leading zeros to strip, and the protocol was constrained to
    ServiceProtocolChoices.

    Rows which cannot be converted — an empty ``ports`` array, or ports that are all NULL, both
    technically invalid under the old schema but possible via direct DB writes — are left with
    ``port_mappings=[]``, which the new model rejects on the next save. Nothing is discarded that the old
    schema considered valid. Operators can find any such records post-migration with, e.g.:
        SELECT id, name FROM ipam_service WHERE port_mappings = '{}';
        SELECT id, name FROM ipam_servicetemplate WHERE port_mappings = '{}';
    """
    for model_name in ('Service', 'ServiceTemplate'):
        # Table names come from the historical model state, not from user input
        table = apps.get_model('ipam', model_name)._meta.db_table
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(POPULATE_PORT_MAPPINGS_SQL.format(table=table))


class Migration(migrations.Migration):

    dependencies = [
        ("ipam", "0095_denormalization_triggers"),
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
        # Migrate existing protocol/ports data into port_mappings before dropping the old fields.
        migrations.RunPython(populate_port_mappings),
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
        # GIN indexes supporting exact protocol/port lookups (port_mappings && ['tcp/80']).
        # Protocol-only and range lookups are served by a correlated scan (GIN array_ops supports
        # only =, &&, @> and <@, so no array index can answer them) — see ipam.utils.PortMappingMatch.
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
