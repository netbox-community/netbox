from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('circuits', '0056_gfk_indexes'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0231_interface_rf_channel_frequency_precision'),
        ('extras', '0136_customfield_validation_schema'),
        ('tenancy', '0023_add_mptt_tree_indexes'),
        ('users', '0015_owner'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='circuit',
            index=models.Index(fields=['provider', 'provider_account', 'cid'], name='circuits_ci_provide_a0c42c_idx'),
        ),
        migrations.AddIndex(
            model_name='circuitgroupassignment',
            index=models.Index(
                fields=['group', 'member_type', 'member_id', 'priority', 'id'], name='circuits_ci_group_i_2f8327_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='virtualcircuit',
            index=models.Index(
                fields=['provider_network', 'provider_account', 'cid'], name='circuits_vi_provide_989efa_idx'
            ),
        ),
        migrations.AddIndex(
            model_name='virtualcircuittermination',
            index=models.Index(fields=['virtual_circuit', 'role', 'id'], name='circuits_vi_virtual_4b5c0c_idx'),
        ),
    ]
