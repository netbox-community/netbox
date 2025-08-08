from django.contrib.postgres.indexes import GistIndex
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0210_macaddress_ordering'),
        ('extras', '0129_fix_script_paths'),
        ('ipam', '0081_remove_service_device_virtual_machine_add_parent_gfk_index'),
        ('tenancy', '0020_remove_contactgroupmembership'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='prefix',
            index=GistIndex(fields=['prefix'], name='ipam_prefix_gist_idx', opclasses=['inet_ops']),
        ),
    ]
