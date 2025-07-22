import django.contrib.postgres.fields
import django.db.models.deletion
from django.db import migrations, models

import core.models.contenttypes


def populate_object_types(apps, schema_editor):
    """
    Create an ObjectType record for each valid ContentType.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ObjectType = apps.get_model('core', 'ObjectType')

    for ct in ContentType.objects.all():
        try:
            # Validate ContentType
            apps.get_model(ct.app_label, ct.model)
        except LookupError:
            continue
        ObjectType(pk=ct.pk).save_base(raw=True)


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0015_remove_redundant_indexes'),
    ]

    operations = [
        # Delete the proxy model from the migration state
        migrations.DeleteModel(
            name='ObjectType',
        ),
        # Create the new concrete model
        migrations.CreateModel(
            name='ObjectType',
            fields=[
                (
                    'contenttype_ptr',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to='contenttypes.contenttype',
                        related_name='object_type'
                    )
                ),
                (
                    'features',
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=50),
                        blank=True,
                        null=True,
                        size=None
                    )
                ),
            ],
            options={
                'verbose_name': 'object type',
                'verbose_name_plural': 'object types',
            },
            bases=('contenttypes.contenttype',),
            managers=[
                ('objects', core.models.contenttypes.ObjectTypeManager()),
            ],
        ),
        # Create an ObjectType record for each ContentType
        migrations.RunPython(
            code=populate_object_types,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
