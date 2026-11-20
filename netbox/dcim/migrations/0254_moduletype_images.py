from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0253_macblock'),
    ]

    operations = [
        migrations.AddField(
            model_name='moduletype',
            name='front_image',
            field=models.ImageField(blank=True, upload_to='moduletype-images'),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='rear_image',
            field=models.ImageField(blank=True, upload_to='moduletype-images'),
        ),
    ]
