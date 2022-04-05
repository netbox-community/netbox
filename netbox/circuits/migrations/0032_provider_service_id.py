from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0004_rename_cable_peer'),
        ('dcim', '0145_site_remove_deprecated_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='providernetwork',
            name='service_id',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
