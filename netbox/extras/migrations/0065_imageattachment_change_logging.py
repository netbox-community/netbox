from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0064_configrevision'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageattachment',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
