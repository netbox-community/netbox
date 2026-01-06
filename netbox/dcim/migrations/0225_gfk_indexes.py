from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0224_add_comments_to_organizationalmodel'),
        ('extras', '0134_owner'),
        ('users', '0015_owner'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='macaddress',
            index=models.Index(
                fields=['assigned_object_type', 'assigned_object_id'], name='dcim_macadd_assigne_54115d_idx'
            ),
        ),
    ]
