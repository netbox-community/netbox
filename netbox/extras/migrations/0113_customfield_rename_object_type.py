from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0112_tag_update_object_types'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customfield',
            old_name='object_type',
            new_name='related_object_type',
        ),
    ]
