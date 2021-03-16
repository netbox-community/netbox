from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0051_migrate_customfields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='CustomField',
            name='default',
        ),
        migrations.RenameField(
            model_name='CustomField',
            old_name='default2',
            new_name='default'
        ),
        migrations.DeleteModel(
            name='CustomFieldChoice',
        ),
        migrations.DeleteModel(
            name='CustomFieldValue',
        ),
    ]
