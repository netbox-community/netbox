from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0003_auto_20160628_1721'),
        ('virtualization', '0001_virtualization'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('ipam', '0001_initial'),
        ('extras', '0002_custom_fields'),
        ('tenancy', '0001_initial'),
    ]

    replaces = [
        ('ipam', '0002_vrf_add_enforce_unique'),
        ('ipam', '0003_ipam_add_vlangroups'),
        ('ipam', '0004_ipam_vlangroup_uniqueness'),
        ('ipam', '0005_auto_20160725_1842'),
        ('ipam', '0006_vrf_vlan_add_tenant'),
        ('ipam', '0007_prefix_ipaddress_add_tenant'),
        ('ipam', '0008_prefix_change_order'),
        ('ipam', '0009_ipaddress_add_status'),
        ('ipam', '0010_ipaddress_help_texts'),
        ('ipam', '0011_rir_add_is_private'),
        ('ipam', '0012_services'),
        ('ipam', '0013_prefix_add_is_pool'),
        ('ipam', '0014_ipaddress_status_add_deprecated'),
        ('ipam', '0015_global_vlans'),
        ('ipam', '0016_unicode_literals'),
        ('ipam', '0017_ipaddress_roles'),
        ('ipam', '0018_remove_service_uniqueness_constraint'),
        ('ipam', '0019_virtualization'),
        ('ipam', '0020_ipaddress_add_role_carp'),
        ('ipam', '0021_vrf_ordering'),
        ('ipam', '0022_tags'),
        ('ipam', '0023_change_logging'),
        ('ipam', '0024_vrf_allow_null_rd'),
        ('ipam', '0025_custom_tag_models'),
        ('ipam', '0026_prefix_ordering_vrf_nulls_first'),
        ('ipam', '0027_ipaddress_add_dns_name'),
        ('ipam', '0028_3569_prefix_fields'),
        ('ipam', '0029_3569_ipaddress_fields'),
        ('ipam', '0030_3569_vlan_fields'),
        ('ipam', '0031_3569_service_fields'),
        ('ipam', '0032_role_description'),
        ('ipam', '0033_deterministic_ordering'),
        ('ipam', '0034_fix_ipaddress_status_dhcp'),
        ('ipam', '0035_drop_ip_family'),
        ('ipam', '0036_standardize_description'),
        ('ipam', '0037_ipaddress_assignment'),
        ('ipam', '0038_custom_field_data'),
        ('ipam', '0039_service_ports_array'),
        ('ipam', '0040_service_drop_port'),
        ('ipam', '0041_routetarget'),
        ('ipam', '0042_standardize_name_length'),
        ('ipam', '0043_add_tenancy_to_aggregates'),
        ('ipam', '0044_standardize_models'),
        ('ipam', '0045_vlangroup_scope'),
        ('ipam', '0046_set_vlangroup_scope_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='virtual_machine',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='services', to='virtualization.virtualmachine'),
        ),
        migrations.AddField(
            model_name='routetarget',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='routetarget',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='route_targets', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prefixes', to='ipam.role'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='dcim.site'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='vlan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='ipam.vlan'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='vrf',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='ipam.vrf'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='assigned_object_type',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'dcim'), ('model', 'interface')), models.Q(('app_label', 'virtualization'), ('model', 'vminterface')), _connector='OR')), null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='nat_inside',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nat_outside', to='ipam.ipaddress'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ip_addresses', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='vrf',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ip_addresses', to='ipam.vrf'),
        ),
        migrations.AddField(
            model_name='aggregate',
            name='rir',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='aggregates', to='ipam.rir'),
        ),
        migrations.AddField(
            model_name='aggregate',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='aggregate',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='aggregates', to='tenancy.tenant'),
        ),
        migrations.AlterUniqueTogether(
            name='vlangroup',
            unique_together={('scope_type', 'scope_id', 'name'), ('scope_type', 'scope_id', 'slug')},
        ),
        migrations.AlterUniqueTogether(
            name='vlan',
            unique_together={('group', 'vid'), ('group', 'name')},
        ),
    ]
