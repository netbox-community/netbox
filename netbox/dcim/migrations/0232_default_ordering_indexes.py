from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0231_interface_rf_channel_frequency_precision'),
        ('extras', '0136_customfield_validation_schema'),
        ('ipam', '0088_rename_vlangroup_total_vlan_ids'),
        ('tenancy', '0023_add_mptt_tree_indexes'),
        ('users', '0015_owner'),
        ('virtualization', '0054_virtualmachinetype'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='consoleporttemplate',
            index=models.Index(fields=['device_type', 'module_type', 'name'], name='dcim_consol_device__101ed5_idx'),
        ),
        migrations.AddIndex(
            model_name='consoleserverporttemplate',
            index=models.Index(fields=['device_type', 'module_type', 'name'], name='dcim_consol_device__a901e6_idx'),
        ),
        migrations.AddIndex(
            model_name='device',
            index=models.Index(fields=['name', 'id'], name='dcim_device_name_c27913_idx'),
        ),
        migrations.AddIndex(
            model_name='frontporttemplate',
            index=models.Index(fields=['device_type', 'module_type', 'name'], name='dcim_frontp_device__ec2ffb_idx'),
        ),
        migrations.AddIndex(
            model_name='interfacetemplate',
            index=models.Index(fields=['device_type', 'module_type', 'name'], name='dcim_interf_device__601012_idx'),
        ),
        migrations.AddIndex(
            model_name='macaddress',
            index=models.Index(fields=['mac_address', 'id'], name='dcim_macadd_mac_add_f2662a_idx'),
        ),
        migrations.AddIndex(
            model_name='modulebaytemplate',
            index=models.Index(fields=['device_type', 'module_type', 'name'], name='dcim_module_device__9eabad_idx'),
        ),
        migrations.AddIndex(
            model_name='moduletype',
            index=models.Index(fields=['profile', 'manufacturer', 'model'], name='dcim_module_profile_868277_idx'),
        ),
        migrations.AddIndex(
            model_name='poweroutlettemplate',
            index=models.Index(fields=['device_type', 'module_type', 'name'], name='dcim_powero_device__b83a8f_idx'),
        ),
        migrations.AddIndex(
            model_name='powerporttemplate',
            index=models.Index(fields=['device_type', 'module_type', 'name'], name='dcim_powerp_device__6c25da_idx'),
        ),
        migrations.AddIndex(
            model_name='rack',
            index=models.Index(fields=['site', 'location', 'name', 'id'], name='dcim_rack_site_id_715040_idx'),
        ),
        migrations.AddIndex(
            model_name='rackreservation',
            index=models.Index(fields=['created', 'id'], name='dcim_rackre_created_84f02e_idx'),
        ),
        migrations.AddIndex(
            model_name='rearporttemplate',
            index=models.Index(fields=['device_type', 'module_type', 'name'], name='dcim_rearpo_device__27f194_idx'),
        ),
        migrations.AddIndex(
            model_name='virtualchassis',
            index=models.Index(fields=['name'], name='dcim_virtua_name_2dc5cd_idx'),
        ),
        migrations.AddIndex(
            model_name='virtualdevicecontext',
            index=models.Index(fields=['name'], name='dcim_virtua_name_079d4d_idx'),
        ),
    ]
