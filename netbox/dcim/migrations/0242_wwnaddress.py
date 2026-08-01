import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import dcim.fields
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0241_nullify_empty_cable_end'),
    ]

    operations = [
        migrations.CreateModel(
            name='WWNAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('wwn_address', dcim.fields.WWNAddressField()),
                ('assigned_object_id', models.PositiveBigIntegerField(blank=True, null=True)),
                (
                    'assigned_object_type',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='contenttypes.contenttype',
                    ),
                ),
                ('owner', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner')
                 ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'abstract': False,
                'ordering': ('wwn_address', 'pk'),
                'verbose_name': 'WWN address',
                'verbose_name_plural': 'WWN addresses'
            },
        ),
    ]
