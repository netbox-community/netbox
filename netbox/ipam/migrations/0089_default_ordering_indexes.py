from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0232_default_ordering_indexes'),
        ('extras', '0137_default_ordering_indexes'),
        ('ipam', '0088_rename_vlangroup_total_vlan_ids'),
        ('tenancy', '0023_add_mptt_tree_indexes'),
        ('users', '0015_owner'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='aggregate',
            index=models.Index(fields=['prefix', 'id'], name='ipam_aggreg_prefix_89dd71_idx'),
        ),
        migrations.AddIndex(
            model_name='fhrpgroup',
            index=models.Index(fields=['protocol', 'group_id', 'id'], name='ipam_fhrpgr_protoco_0445ae_idx'),
        ),
        migrations.AddIndex(
            model_name='fhrpgroupassignment',
            index=models.Index(fields=['-priority', 'id'], name='ipam_fhrpgr_priorit_b76335_idx'),
        ),
        migrations.AddIndex(
            model_name='ipaddress',
            index=models.Index(fields=['address', 'id'], name='ipam_ipaddr_address_3ddeea_idx'),
        ),
        migrations.AddIndex(
            model_name='role',
            index=models.Index(fields=['weight', 'name'], name='ipam_role_weight_01396b_idx'),
        ),
        migrations.AddIndex(
            model_name='service',
            index=models.Index(fields=['protocol', 'ports', 'id'], name='ipam_servic_protoco_687d13_idx'),
        ),
        migrations.AddIndex(
            model_name='vlangroup',
            index=models.Index(fields=['name', 'id'], name='ipam_vlangr_name_ffa83e_idx'),
        ),
        migrations.AddIndex(
            model_name='vlan',
            index=models.Index(fields=['site', 'group', 'vid', 'id'], name='ipam_vlan_site_id_985573_idx'),
        ),
        migrations.AddIndex(
            model_name='vrf',
            index=models.Index(fields=['name', 'rd', 'id'], name='ipam_vrf_name_ec911d_idx'),
        ),
    ]
