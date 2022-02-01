from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import utilities.fields
import utilities.ordering


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0148_inventoryitem_component'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryItemTemplate',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('_name', utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize)),
                ('label', models.CharField(blank=True, max_length=64)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('component_id', models.PositiveBigIntegerField(blank=True, null=True)),
                ('part_id', models.CharField(blank=True, max_length=50)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('component_type', models.ForeignKey(blank=True, limit_choices_to=models.Q(('app_label', 'dcim'), ('model__in', ('consoleporttemplate', 'consoleserverporttemplate', 'frontporttemplate', 'interfacetemplate', 'poweroutlettemplate', 'powerporttemplate', 'rearporttemplate'))), null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype')),
                ('device_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype')),
                ('manufacturer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inventory_item_templates', to='dcim.manufacturer')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_items', to='dcim.inventoryitemtemplate')),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inventory_item_templates', to='dcim.inventoryitemrole')),
            ],
            options={
                'ordering': ('device_type__id', 'parent__id', '_name'),
                'unique_together': {('device_type', 'parent', 'name')},
            },
        ),
    ]
