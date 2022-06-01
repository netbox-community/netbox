from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0035_provider_asns'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuittermination',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
    ]
