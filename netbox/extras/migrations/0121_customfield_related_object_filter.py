from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0120_eventrule_event_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='related_object_filter',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
