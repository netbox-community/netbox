from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0125_exporttemplate_file_name'),
        ('ipam', '0079_populate_service_parent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='device',
        ),
        migrations.RemoveField(
            model_name='service',
            name='virtual_machine',
        ),
        migrations.AddIndex(
            model_name='service',
            index=models.Index(
                fields=['parent_object_type', 'parent_object_id'], name='ipam_servic_parent__563d2b_idx'
            ),
        ),
    ]
