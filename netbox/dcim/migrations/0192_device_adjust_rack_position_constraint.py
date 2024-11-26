from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0191_module_bay_rebuild'),
        ('extras', '0121_customfield_related_object_filter'),
        ('ipam', '0070_vlangroup_vlan_id_ranges'),
        ('tenancy', '0015_contactassignment_rename_content_type'),
        ('virtualization', '0040_convert_disk_size'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='device',
            name='dcim_device_unique_rack_position_face',
        ),
        migrations.AddConstraint(
            model_name='device',
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ('position__isnull', False),
                    ('rack__isnull', False)
                ),
                fields=('rack', 'position', 'face'),
                name='dcim_device_unique_rack_position_face'
            ),
        ),
    ]
