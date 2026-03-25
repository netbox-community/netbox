from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0228_cable_bundle'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicebay',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='devicebaytemplate',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='modulebay',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='modulebaytemplate',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
    ]
