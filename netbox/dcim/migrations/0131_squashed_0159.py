import dcim.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import taggit.managers
import utilities.fields
import utilities.json
import utilities.ordering


class Migration(migrations.Migration):
    replaces = [
        ('dcim', '0131_consoleport_speed'),
        ('dcim', '0132_cable_length'),
        ('dcim', '0133_port_colors'),
        ('dcim', '0134_interface_wwn_bridge'),
        ('dcim', '0135_tenancy_extensions'),
        ('dcim', '0136_device_airflow'),
        ('dcim', '0137_relax_uniqueness_constraints'),
        ('dcim', '0138_extend_tag_support'),
        ('dcim', '0139_rename_cable_peer'),
        ('dcim', '0140_wireless'),
        ('dcim', '0141_asn_model'),
        ('dcim', '0142_rename_128gfc_qsfp28'),
        ('dcim', '0143_remove_primary_for_related_name'),
        ('dcim', '0144_fix_cable_abs_length'),
        ('dcim', '0145_site_remove_deprecated_fields'),
        ('dcim', '0146_modules'),
        ('dcim', '0147_inventoryitemrole'),
        ('dcim', '0148_inventoryitem_component'),
        ('dcim', '0149_inventoryitem_templates'),
        ('dcim', '0150_interface_vrf'),
        ('dcim', '0151_interface_speed_duplex'),
        ('dcim', '0152_standardize_id_fields'),
        ('dcim', '0153_created_datetimefield'),
        ('dcim', '0154_half_height_rack_units'),
        ('dcim', '0155_interface_poe_mode_type'),
        ('dcim', '0156_location_status'),
        ('dcim', '0157_new_cabling_models'),
        ('dcim', '0158_populate_cable_terminations'),
        ('dcim', '0159_populate_cable_paths'),
    ]

    dependencies = [
        ('tenancy', '0012_standardize_models'),
        ('extras', '0002_squashed_0059'),
        ('dcim', '0130_sitegroup'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('ipam', '0053_asn_model'),
        ('wireless', '0001_wireless'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consoleport',
            name='speed',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='speed',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cable',
            name='length',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='frontport',
            name='color',
            field=utilities.fields.ColorField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='frontporttemplate',
            name='color',
            field=utilities.fields.ColorField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='rearport',
            name='color',
            field=utilities.fields.ColorField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='rearporttemplate',
            name='color',
            field=utilities.fields.ColorField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='interface',
            name='wwn',
            field=dcim.fields.WWNField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='bridge',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='bridge_interfaces',
                to='dcim.interface',
            ),
        ),
        migrations.AddField(
            model_name='location',
            name='tenant',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='locations',
                to='tenancy.tenant',
            ),
        ),
        migrations.AddField(
            model_name='cable',
            name='tenant',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='cables',
                to='tenancy.tenant',
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='airflow',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='device',
            name='airflow',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='region',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='region',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
        migrations.AlterField(
            model_name='sitegroup',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='sitegroup',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='location',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(fields=('site', 'parent', 'name'), name='dcim_location_parent_name'),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(
                condition=models.Q(('parent', None)), fields=('site', 'name'), name='dcim_location_name'
            ),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(fields=('site', 'parent', 'slug'), name='dcim_location_parent_slug'),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(
                condition=models.Q(('parent', None)), fields=('site', 'slug'), name='dcim_location_slug'
            ),
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(fields=('parent', 'name'), name='dcim_region_parent_name'),
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(
                condition=models.Q(('parent', None)), fields=('name',), name='dcim_region_name'
            ),
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(fields=('parent', 'slug'), name='dcim_region_parent_slug'),
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(
                condition=models.Q(('parent', None)), fields=('slug',), name='dcim_region_slug'
            ),
        ),
        migrations.AddConstraint(
            model_name='sitegroup',
            constraint=models.UniqueConstraint(fields=('parent', 'name'), name='dcim_sitegroup_parent_name'),
        ),
        migrations.AddConstraint(
            model_name='sitegroup',
            constraint=models.UniqueConstraint(
                condition=models.Q(('parent', None)), fields=('name',), name='dcim_sitegroup_name'
            ),
        ),
        migrations.AddConstraint(
            model_name='sitegroup',
            constraint=models.UniqueConstraint(fields=('parent', 'slug'), name='dcim_sitegroup_parent_slug'),
        ),
        migrations.AddConstraint(
            model_name='sitegroup',
            constraint=models.UniqueConstraint(
                condition=models.Q(('parent', None)), fields=('slug',), name='dcim_sitegroup_slug'
            ),
        ),
        migrations.AddField(
            model_name='devicerole',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='location',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='platform',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='rackrole',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='region',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='sitegroup',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.RenameField(
            model_name='consoleport',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='consoleport',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='consoleserverport',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='consoleserverport',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='frontport',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='frontport',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='interface',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='interface',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='powerfeed',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='powerfeed',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='poweroutlet',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='poweroutlet',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='powerport',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='powerport',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='rearport',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='rearport',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.AddField(
            model_name='interface',
            name='rf_role',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='interface',
            name='rf_channel',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='interface',
            name='rf_channel_frequency',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='rf_channel_width',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=7, null=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='tx_power',
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, validators=[django.core.validators.MaxValueValidator(127)]
            ),
        ),
        migrations.AddField(
            model_name='interface',
            name='wireless_lans',
            field=models.ManyToManyField(blank=True, related_name='interfaces', to='wireless.wirelesslan'),
        ),
        migrations.AddField(
            model_name='interface',
            name='wireless_link',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='wireless.wirelesslink',
            ),
        ),
        migrations.AddField(
            model_name='site',
            name='asns',
            field=models.ManyToManyField(blank=True, related_name='sites', to='ipam.asn'),
        ),
        migrations.AlterField(
            model_name='device',
            name='primary_ip4',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='ipam.ipaddress',
            ),
        ),
        migrations.AlterField(
            model_name='device',
            name='primary_ip6',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='ipam.ipaddress',
            ),
        ),
        migrations.RemoveField(
            model_name='site',
            name='asn',
        ),
        migrations.RemoveField(
            model_name='site',
            name='contact_email',
        ),
        migrations.RemoveField(
            model_name='site',
            name='contact_name',
        ),
        migrations.RemoveField(
            model_name='site',
            name='contact_phone',
        ),
        migrations.RunSQL(
            sql="""DO $$
            DECLARE idx record;
            BEGIN
                FOR idx IN
                    SELECT indexname AS old_name, replace(indexname, 'module', 'inventoryitem') AS new_name
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
            END$$;""",
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
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.devicetype',
            ),
        ),
        migrations.AlterField(
            model_name='consoleserverporttemplate',
            name='device_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.devicetype',
            ),
        ),
        migrations.AlterField(
            model_name='frontporttemplate',
            name='device_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.devicetype',
            ),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='device_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.devicetype',
            ),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='device_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.devicetype',
            ),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='device_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.devicetype',
            ),
        ),
        migrations.AlterField(
            model_name='rearporttemplate',
            name='device_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.devicetype',
            ),
        ),
        migrations.CreateModel(
            name='ModuleType',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('model', models.CharField(max_length=100)),
                ('part_number', models.CharField(blank=True, max_length=50)),
                ('comments', models.TextField(blank=True)),
                (
                    'manufacturer',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name='module_types', to='dcim.manufacturer'
                    ),
                ),
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
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                (
                    '_name',
                    utilities.fields.NaturalOrderingField(
                        'name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize
                    ),
                ),
                ('label', models.CharField(blank=True, max_length=64)),
                ('position', models.CharField(blank=True, max_length=30)),
                ('description', models.CharField(blank=True, max_length=200)),
                (
                    'device',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.device'
                    ),
                ),
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
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('local_context_data', models.JSONField(blank=True, null=True)),
                ('serial', models.CharField(blank=True, max_length=50)),
                ('asset_tag', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('comments', models.TextField(blank=True)),
                (
                    'device',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='dcim.device'
                    ),
                ),
                (
                    'module_bay',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='installed_module',
                        to='dcim.modulebay',
                    ),
                ),
                (
                    'module_type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name='instances', to='dcim.moduletype'
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('module_bay',),
            },
        ),
        migrations.AddField(
            model_name='consoleport',
            name='module',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.module',
            ),
        ),
        migrations.AddField(
            model_name='consoleporttemplate',
            name='module_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.moduletype',
            ),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='module',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.module',
            ),
        ),
        migrations.AddField(
            model_name='consoleserverporttemplate',
            name='module_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.moduletype',
            ),
        ),
        migrations.AddField(
            model_name='frontport',
            name='module',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.module',
            ),
        ),
        migrations.AddField(
            model_name='frontporttemplate',
            name='module_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.moduletype',
            ),
        ),
        migrations.AddField(
            model_name='interface',
            name='module',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.module',
            ),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
            name='module_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.moduletype',
            ),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='module',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.module',
            ),
        ),
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='module_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.moduletype',
            ),
        ),
        migrations.AddField(
            model_name='powerport',
            name='module',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.module',
            ),
        ),
        migrations.AddField(
            model_name='powerporttemplate',
            name='module_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.moduletype',
            ),
        ),
        migrations.AddField(
            model_name='rearport',
            name='module',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.module',
            ),
        ),
        migrations.AddField(
            model_name='rearporttemplate',
            name='module_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(class)ss',
                to='dcim.moduletype',
            ),
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
            unique_together={('rear_port', 'rear_port_position'), ('device_type', 'name'), ('module_type', 'name')},
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
            name='InventoryItemRole',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('color', utilities.fields.ColorField(default='9e9e9e', max_length=6)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='role',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='inventory_items',
                to='dcim.inventoryitemrole',
            ),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='component_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='component_type',
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(
                    ('app_label', 'dcim'),
                    (
                        'model__in',
                        (
                            'consoleport',
                            'consoleserverport',
                            'frontport',
                            'interface',
                            'poweroutlet',
                            'powerport',
                            'rearport',
                        ),
                    ),
                ),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='contenttypes.contenttype',
            ),
        ),
        migrations.AddField(
            model_name='interface',
            name='vrf',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='interfaces',
                to='ipam.vrf',
            ),
        ),
        migrations.AddField(
            model_name='interface',
            name='duplex',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='speed',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cable',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='cablepath',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='consoleporttemplate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='consoleserverporttemplate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='device',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='devicebay',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='devicebaytemplate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='devicerole',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='frontport',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='frontporttemplate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='interface',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='location',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='manufacturer',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='platform',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='powerfeed',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='powerpanel',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='rack',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='rackreservation',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='rackrole',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='rearport',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='rearporttemplate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='region',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='site',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='sitegroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='virtualchassis',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='cable',
            name='termination_a_id',
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name='cable',
            name='termination_b_id',
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name='cablepath',
            name='destination_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cablepath',
            name='origin_id',
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='_link_peer_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='_link_peer_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='frontport',
            name='_link_peer_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='_link_peer_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='powerfeed',
            name='_link_peer_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='_link_peer_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='_link_peer_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='rearport',
            name='_link_peer_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cable',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='consoleporttemplate',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='consoleserverporttemplate',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='devicebay',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='devicebaytemplate',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='devicerole',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='frontport',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='frontporttemplate',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='interface',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.CreateModel(
            name='InventoryItemTemplate',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                (
                    '_name',
                    utilities.fields.NaturalOrderingField(
                        'name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize
                    ),
                ),
                ('label', models.CharField(blank=True, max_length=64)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('component_id', models.PositiveBigIntegerField(blank=True, null=True)),
                ('part_id', models.CharField(blank=True, max_length=50)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                (
                    'component_type',
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to=models.Q(
                            ('app_label', 'dcim'),
                            (
                                'model__in',
                                (
                                    'consoleporttemplate',
                                    'consoleserverporttemplate',
                                    'frontporttemplate',
                                    'interfacetemplate',
                                    'poweroutlettemplate',
                                    'powerporttemplate',
                                    'rearporttemplate',
                                ),
                            ),
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='contenttypes.contenttype',
                    ),
                ),
                (
                    'device_type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'
                    ),
                ),
                (
                    'manufacturer',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='inventory_item_templates',
                        to='dcim.manufacturer',
                    ),
                ),
                (
                    'parent',
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='child_items',
                        to='dcim.inventoryitemtemplate',
                    ),
                ),
                (
                    'role',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='inventory_item_templates',
                        to='dcim.inventoryitemrole',
                    ),
                ),
            ],
            options={
                'ordering': ('device_type__id', 'parent__id', '_name'),
                'unique_together': {('device_type', 'parent', 'name')},
            },
        ),
        migrations.AlterField(
            model_name='location',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='manufacturer',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.CreateModel(
            name='ModuleBayTemplate',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                (
                    '_name',
                    utilities.fields.NaturalOrderingField(
                        'name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize
                    ),
                ),
                ('label', models.CharField(blank=True, max_length=64)),
                ('position', models.CharField(blank=True, max_length=30)),
                ('description', models.CharField(blank=True, max_length=200)),
                (
                    'device_type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='dcim.devicetype'
                    ),
                ),
            ],
            options={
                'ordering': ('device_type', '_name'),
                'unique_together': {('device_type', 'name')},
            },
        ),
        migrations.AlterField(
            model_name='platform',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='powerfeed',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='powerpanel',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='rack',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='rackreservation',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='rackrole',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='rearport',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='rearporttemplate',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='region',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='sitegroup',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='virtualchassis',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='u_height',
            field=models.DecimalField(decimal_places=1, default=1.0, max_digits=4),
        ),
        migrations.AlterField(
            model_name='device',
            name='position',
            field=models.DecimalField(
                blank=True,
                decimal_places=1,
                max_digits=4,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(100.5),
                ],
            ),
        ),
        migrations.AddField(
            model_name='interface',
            name='poe_mode',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='interface',
            name='poe_type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
            name='poe_mode',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
            name='poe_type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='location',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.CreateModel(
            name='CableTermination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('cable_end', models.CharField(max_length=1)),
                ('termination_id', models.PositiveBigIntegerField()),
                (
                    'cable',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='terminations', to='dcim.cable'
                    ),
                ),
                (
                    'termination_type',
                    models.ForeignKey(
                        limit_choices_to=models.Q(
                            models.Q(
                                models.Q(('app_label', 'circuits'), ('model__in', ('circuittermination',))),
                                models.Q(
                                    ('app_label', 'dcim'),
                                    (
                                        'model__in',
                                        (
                                            'consoleport',
                                            'consoleserverport',
                                            'frontport',
                                            'interface',
                                            'powerfeed',
                                            'poweroutlet',
                                            'powerport',
                                            'rearport',
                                        ),
                                    ),
                                ),
                                _connector='OR',
                            )
                        ),
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='contenttypes.contenttype',
                    ),
                ),
                (
                    '_device',
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dcim.device'
                    ),
                ),
                (
                    '_rack',
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dcim.rack'
                    ),
                ),
                (
                    '_location',
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dcim.location'
                    ),
                ),
                (
                    '_site',
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dcim.site'
                    ),
                ),
            ],
            options={
                'ordering': ('cable', 'cable_end', 'pk'),
            },
        ),
        migrations.AddConstraint(
            model_name='cabletermination',
            constraint=models.UniqueConstraint(
                fields=('termination_type', 'termination_id'), name='dcim_cable_termination_unique_termination'
            ),
        ),
        migrations.RenameField(
            model_name='cablepath',
            old_name='path',
            new_name='_nodes',
        ),
        migrations.AddField(
            model_name='cablepath',
            name='path',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='cablepath',
            name='is_complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='frontport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='interface',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='powerport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='rearport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
    ]
