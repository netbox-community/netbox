import django.contrib.postgres.fields
import django.contrib.postgres.indexes
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0017_objectchange_message'),
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
                    'public',
                    models.BooleanField(
                        default=False
                    )
                ),
                (
                    'features',
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=50),
                        default=list,
                        size=None
                    )
                ),
            ],
            options={
                'verbose_name': 'object type',
                'verbose_name_plural': 'object types',
                'ordering': ('app_label', 'model'),
                'indexes': [
                    django.contrib.postgres.indexes.GinIndex(
                        fields=['features'],
                        name='core_object_feature_aec4de_gin'
                    ),
                ]
            },
            bases=('contenttypes.contenttype',),
            managers=[],
        ),
    ]
