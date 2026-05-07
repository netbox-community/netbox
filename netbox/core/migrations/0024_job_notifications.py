from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_datasource_sync_permission'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='notifications',
            field=models.CharField(default='always', max_length=30),
        ),
    ]
