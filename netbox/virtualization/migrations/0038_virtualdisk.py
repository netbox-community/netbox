from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.fields
import utilities.json
import utilities.ordering
import utilities.query_functions
import utilities.tracking


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0099_cachedvalue_ordering'),
        ('virtualization', '0037_protect_child_interfaces'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualmachine',
            name='virtual_disk_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='virtual_machine', to_model='virtualization.VirtualDisk'
            ),
        ),
        migrations.CreateModel(
            name='VirtualDisk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('name', models.CharField(max_length=64)),
                (
                    '_name',
                    utilities.fields.NaturalOrderingField(
                        'name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize_interface
                    ),
                ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('size', models.PositiveIntegerField()),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                (
                    'virtual_machine',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='%(class)ss',
                        to='virtualization.virtualmachine',
                    ),
                ),
            ],
            options={
                'verbose_name': 'virtual disk',
                'verbose_name_plural': 'virtual disks',
                'ordering': ('virtual_machine', utilities.query_functions.CollateAsChar('_name')),
                'abstract': False,
            },
            bases=(models.Model, utilities.tracking.TrackingModelMixin),
        ),
        migrations.AddConstraint(
            model_name='virtualdisk',
            constraint=models.UniqueConstraint(
                fields=('virtual_machine', 'name'), name='virtualization_virtualdisk_unique_virtual_machine_name'
            ),
        ),
    ]
