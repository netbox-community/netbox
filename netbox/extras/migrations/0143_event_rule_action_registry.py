import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0142_webhook_timeout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventrule',
            name='action_object_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='eventrule_actions',
                to='contenttypes.contenttype',
            ),
        ),
        migrations.AlterField(
            model_name='eventrule',
            name='action_type',
            field=models.CharField(default='webhook', max_length=100),
        ),
    ]
