from utilities.json import CustomFieldJSONEncoder
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.fields
import utilities.ordering


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0066_customfield_name_validation'),
        ('dcim', '0145_site_remove_deprecated_fields'),
    ]

    operations = [
        # Rename any indexes left over from the old Module model (now InventoryItem) (#8656)
        migrations.RunSQL(
            """
            DO $$
            DECLARE
                idx record;
            BEGIN
                FOR idx IN
                    SELECT indexname AS old_name,
                           replace(indexname, 'module', 'inventoryitem') AS new_name
                    FROM pg_indexes
                    WHERE schemaname = 'public' AND
                          tablename = 'dcim_inventoryitem' AND
                          indexname LIKE 'dcim_module_%'
                LOOP
                    EXECUTE format(
                        'ALTER INDEX %I RENAME TO %I;',
                        idx.old_name,
                        idx.new_name
                    );
                END LOOP;
            END$$;
            """
        ),

        migrations.AlterModelOptions(
            name='consoleporttemplate',
            options={'ordering': ('device_type', 'module_type', '_name')},
        ),
        migrations.AlterModelOptions(
            name='consoleserverporttemplate',
            options={'ordering': ('device_type', 'module_type', '_name')},
        ),
        migrations.AlterModelOptions(
            name='frontporttemplate',
            options={'ordering': ('device_type', 'module_type', '_name')},
        ),
        migrations.AlterModelOptions(
            name='interfacetemplate',
            options={'ordering': ('device_type', 'module_type', '_name')},
        ),
        migrations.AlterModelOptions(
            name='poweroutlettemplate',
            options={'ordering': ('device_type', 'module_type', '_name')},
        ),
        migrations.AlterModelOptions(
            name='powerporttemplate',
            options={'ordering': ('device_type', 'module_type', '_name')},
        ),
        migrations.AlterModelOptions(
            name='rearporttemplate',
            options={'ordering': ('device_type', 'module_type', '_name')},
        ),
        migrations.AlterField(
            model_name='consoleporttemplate',
            name='device_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'),
        ),
        migrations.AlterField(
            model_name='consoleserverporttemplate',
            name='device_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'),
        ),
        migrations.AlterField(
            model_name='frontporttemplate',
            name='device_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='device_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='device_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='device_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'),
        ),
        migrations.AlterField(
            model_name='rearporttemplate',
            name='device_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'),
        ),
        migrations.CreateModel(
            name='ModuleType',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=CustomFieldJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('model', models.CharField(max_length=100)),
                ('part_number', models.CharField(blank=True, max_length=50)),
                ('comments', models.TextField(blank=True)),
                ('manufacturer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='module_types', to='dcim.manufacturer')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('manufacturer', 'model'),
                'unique_together': {('manufacturer', 'model')},
            },
        ),
        migrations.CreateModel(
            name='ModuleBay',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=CustomFieldJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('_name', utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize)),
                ('label', models.CharField(blank=True, max_length=64)),
                ('position', models.CharField(blank=True, max_length=30)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.device')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('device', '_name'),
                'unique_together': {('device', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=CustomFieldJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('local_context_data', models.JSONField(blank=True, null=True)),
                ('serial', models.CharField(blank=True, max_length=50)),
                ('asset_tag', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('comments', models.TextField(blank=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='dcim.device')),
                ('module_bay', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='installed_module', to='dcim.modulebay')),
                ('module_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='instances', to='dcim.moduletype')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('module_bay',),
            },
        ),
        migrations.AddField(
            model_name='consoleport',
            name='module',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.module'),
        ),
        migrations.AddField(
            model_name='consoleporttemplate',
            name='module_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.moduletype'),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='module',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.module'),
        ),
        migrations.AddField(
            model_name='consoleserverporttemplate',
            name='module_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.moduletype'),
        ),
        migrations.AddField(
            model_name='frontport',
            name='module',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.module'),
        ),
        migrations.AddField(
            model_name='frontporttemplate',
            name='module_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.moduletype'),
        ),
        migrations.AddField(
            model_name='interface',
            name='module',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.module'),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
            name='module_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.moduletype'),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='module',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.module'),
        ),
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='module_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.moduletype'),
        ),
        migrations.AddField(
            model_name='powerport',
            name='module',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.module'),
        ),
        migrations.AddField(
            model_name='powerporttemplate',
            name='module_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.moduletype'),
        ),
        migrations.AddField(
            model_name='rearport',
            name='module',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.module'),
        ),
        migrations.AddField(
            model_name='rearporttemplate',
            name='module_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.moduletype'),
        ),
        migrations.AlterUniqueTogether(
            name='consoleporttemplate',
            unique_together={('device_type', 'name'), ('module_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='consoleserverporttemplate',
            unique_together={('device_type', 'name'), ('module_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='frontporttemplate',
            unique_together={('device_type', 'name'), ('rear_port', 'rear_port_position'), ('module_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='interfacetemplate',
            unique_together={('device_type', 'name'), ('module_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='poweroutlettemplate',
            unique_together={('device_type', 'name'), ('module_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='powerporttemplate',
            unique_together={('device_type', 'name'), ('module_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='rearporttemplate',
            unique_together={('device_type', 'name'), ('module_type', 'name')},
        ),
        migrations.CreateModel(
            name='ModuleBayTemplate',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('_name', utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize)),
                ('label', models.CharField(blank=True, max_length=64)),
                ('position', models.CharField(blank=True, max_length=30)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('device_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype')),
            ],
            options={
                'ordering': ('device_type', '_name'),
                'unique_together': {('device_type', 'name')},
            },
        ),
    ]
