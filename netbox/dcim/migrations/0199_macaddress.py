import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import dcim.fields
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0198_natural_ordering'),
        ('extras', '0122_charfield_null_choices'),
    ]

    operations = [
        migrations.CreateModel(
            name='MACAddress',
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
                ('mac_address', dcim.fields.MACAddressField()),
                ('assigned_object_id', models.PositiveBigIntegerField(blank=True, null=True)),
                (
                    'assigned_object_type',
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to=models.Q(
                            models.Q(
                                models.Q(('app_label', 'dcim'), ('model', 'interface')),
                                models.Q(('app_label', 'virtualization'), ('model', 'vminterface')),
                                _connector='OR',
                            )
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='contenttypes.contenttype',
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={'abstract': False, 'ordering': ('mac_address',)},
        ),
    ]
