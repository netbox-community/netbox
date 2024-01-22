from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0145_site_remove_deprecated_fields'),
        ('wireless', '0001_wireless'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wirelesslan',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='wirelesslangroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='wirelesslink',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
    ]
