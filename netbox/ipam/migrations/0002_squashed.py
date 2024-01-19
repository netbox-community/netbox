from django.db import migrations, models
import django.db.models.deletion
import django.db.models.functions.comparison
import ipam.fields
import ipam.lookups
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('virtualization', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0002_squashed'),
        ('dcim', '0003_squashed'),
        ('ipam', '0001_initial'),
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
        ('ipam', '0047_prefix_depth_children'),
        ('ipam', '0048_prefix_populate_depth_children'),
        ('ipam', '0049_prefix_mark_utilized'),
        ('ipam', '0050_iprange'),
        ('ipam', '0051_extend_tag_support'),
        ('ipam', '0052_fhrpgroup'),
        ('ipam', '0053_asn_model'),
        ('ipam', '0054_vlangroup_min_max_vids'),
        ('ipam', '0055_servicetemplate'),
        ('ipam', '0056_standardize_id_fields'),
        ('ipam', '0057_created_datetimefield'),
        ('ipam', '0058_ipaddress_nat_inside_nonunique'),
        ('ipam', '0059_l2vpn'),
        ('ipam', '0060_alter_l2vpn_slug'),
        ('ipam', '0061_fhrpgroup_name'),
        ('ipam', '0062_unique_constraints'),
        ('ipam', '0063_standardize_description_comments'),
        ('ipam', '0064_clear_search_cache'),
        ('ipam', '0065_asnrange'),
        ('ipam', '0066_iprange_mark_utilized'),
        ('ipam', '0067_ipaddress_index_host'),
    ]

    operations = [
        migrations.AddField(
            model_name='vrf',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vrfs', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='vlangroup',
            name='scope_type',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(('model__in', ('region', 'sitegroup', 'site', 'location', 'rack', 'clustergroup', 'cluster'))), null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='vlangroup',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='vlan',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vlans', to='ipam.vlangroup'),
        ),
        migrations.AddField(
            model_name='vlan',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vlans', to='ipam.role'),
        ),
        migrations.AddField(
            model_name='vlan',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vlans', to='dcim.site'),
        ),
        migrations.AddField(
            model_name='vlan',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='vlan',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vlans', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='servicetemplate',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='service',
            name='device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='services', to='dcim.device'),
        ),
        migrations.AddField(
            model_name='service',
            name='ipaddresses',
            field=models.ManyToManyField(blank=True, related_name='services', to='ipam.ipaddress'),
        ),
        migrations.AddField(
            model_name='service',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
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
            model_name='role',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='rir',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
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
            model_name='l2vpntermination',
            name='assigned_object_type',
            field=models.ForeignKey(limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'dcim'), ('model', 'interface')), models.Q(('app_label', 'ipam'), ('model', 'vlan')), models.Q(('app_label', 'virtualization'), ('model', 'vminterface')), _connector='OR')), on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='l2vpntermination',
            name='l2vpn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terminations', to='ipam.l2vpn'),
        ),
        migrations.AddField(
            model_name='l2vpntermination',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='l2vpn',
            name='export_targets',
            field=models.ManyToManyField(blank=True, related_name='exporting_l2vpns', to='ipam.routetarget'),
        ),
        migrations.AddField(
            model_name='l2vpn',
            name='import_targets',
            field=models.ManyToManyField(blank=True, related_name='importing_l2vpns', to='ipam.routetarget'),
        ),
        migrations.AddField(
            model_name='l2vpn',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='l2vpn',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='l2vpns', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='iprange',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ip_ranges', to='ipam.role'),
        ),
        migrations.AddField(
            model_name='iprange',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='iprange',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ip_ranges', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='iprange',
            name='vrf',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ip_ranges', to='ipam.vrf'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='assigned_object_type',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'dcim'), ('model', 'interface')), models.Q(('app_label', 'ipam'), ('model', 'fhrpgroup')), models.Q(('app_label', 'virtualization'), ('model', 'vminterface')), _connector='OR')), null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='nat_inside',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nat_outside', to='ipam.ipaddress'),
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
            model_name='fhrpgroupassignment',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ipam.fhrpgroup'),
        ),
        migrations.AddField(
            model_name='fhrpgroupassignment',
            name='interface_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='fhrpgroup',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='asnrange',
            name='rir',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='asn_ranges', to='ipam.rir'),
        ),
        migrations.AddField(
            model_name='asnrange',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='asnrange',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='asn_ranges', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='asn',
            name='rir',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='asns', to='ipam.rir'),
        ),
        migrations.AddField(
            model_name='asn',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='asn',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='asns', to='tenancy.tenant'),
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
        migrations.AddConstraint(
            model_name='vlangroup',
            constraint=models.UniqueConstraint(fields=('scope_type', 'scope_id', 'name'), name='ipam_vlangroup_unique_scope_name'),
        ),
        migrations.AddConstraint(
            model_name='vlangroup',
            constraint=models.UniqueConstraint(fields=('scope_type', 'scope_id', 'slug'), name='ipam_vlangroup_unique_scope_slug'),
        ),
        migrations.AddConstraint(
            model_name='vlan',
            constraint=models.UniqueConstraint(fields=('group', 'vid'), name='ipam_vlan_unique_group_vid'),
        ),
        migrations.AddConstraint(
            model_name='vlan',
            constraint=models.UniqueConstraint(fields=('group', 'name'), name='ipam_vlan_unique_group_name'),
        ),
        migrations.AddConstraint(
            model_name='l2vpntermination',
            constraint=models.UniqueConstraint(fields=('assigned_object_type', 'assigned_object_id'), name='ipam_l2vpntermination_assigned_object'),
        ),
        migrations.AddIndex(
            model_name='ipaddress',
            index=models.Index(django.db.models.functions.comparison.Cast(ipam.lookups.Host('address'), output_field=ipam.fields.IPAddressField()), name='ipam_ipaddress_host'),
        ),
        migrations.AddConstraint(
            model_name='fhrpgroupassignment',
            constraint=models.UniqueConstraint(fields=('interface_type', 'interface_id', 'group'), name='ipam_fhrpgroupassignment_unique_interface_group'),
        ),
    ]
