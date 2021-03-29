from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0124_mark_connected'),
    ]

    operations = [
        migrations.AddField(
            model_name='consoleport',
            name='speed',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='speed',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
