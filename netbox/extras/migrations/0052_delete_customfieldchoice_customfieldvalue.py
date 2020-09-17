from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0051_migrate_customfields'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomFieldChoice',
        ),
        migrations.DeleteModel(
            name='CustomFieldValue',
        ),
    ]
