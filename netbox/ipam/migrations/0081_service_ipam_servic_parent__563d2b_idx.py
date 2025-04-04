from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0125_exporttemplate_file_name'),
        ('ipam', '0080_remove_service_device_remove_service_virtual_machine'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='service',
            index=models.Index(
                fields=['parent_object_type', 'parent_object_id'], name='ipam_servic_parent__563d2b_idx'
            ),
        ),
    ]
