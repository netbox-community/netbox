from decimal import Decimal

import django.core.validators
import django.db.models.deletion
import django.db.models.functions.text
import taggit.managers
from django.db import migrations, models

import netbox.models.deletion
import utilities.fields
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ('virtualization', '0053_virtualmachine_standalone_device_assignment'),
    ]

    operations = [
        migrations.CreateModel(
            name='VirtualMachineType',
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
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                (
                    'default_vcpus',
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=6,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal('0.01'))],
                    ),
                ),
                ('default_memory', models.PositiveIntegerField(blank=True, null=True)),
                (
                    'virtual_machine_count',
                    utilities.fields.CounterCacheField(
                        default=0,
                        editable=False,
                        to_field='virtual_machine_type',
                        to_model='virtualization.VirtualMachine',
                    ),
                ),
                (
                    'default_platform',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='+',
                        to='dcim.platform',
                    ),
                ),
                (
                    'owner',
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'virtual machine type',
                'verbose_name_plural': 'virtual machine types',
                'ordering': ('name',),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='virtual_machine_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='instances',
                to='virtualization.virtualmachinetype',
            ),
        ),
        migrations.AddConstraint(
            model_name='virtualmachinetype',
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower('name'),
                name='virtualization_virtualmachinetype_unique_name',
                violation_error_message='Virtual machine type name must be unique.',
            ),
        ),
    ]
