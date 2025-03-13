from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0201_add_power_outlet_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='region',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='sitegroup',
            name='comments',
            field=models.TextField(blank=True),
        ),
    ]
