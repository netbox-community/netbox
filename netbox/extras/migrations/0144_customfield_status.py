from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0143_event_rule_action_registry'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='status',
            field=models.CharField(default='active', editable=False, max_length=50),
        ),
    ]
