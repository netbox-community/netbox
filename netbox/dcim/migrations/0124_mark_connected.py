from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0123_standardize_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='consoleport',
            name='mark_connected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='mark_connected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='frontport',
            name='mark_connected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='interface',
            name='mark_connected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='mark_connected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='mark_connected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='powerport',
            name='mark_connected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rearport',
            name='mark_connected',
            field=models.BooleanField(default=False),
        ),
    ]
