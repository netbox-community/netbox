from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0025_standardize_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuittermination',
            name='mark_connected',
            field=models.BooleanField(default=False),
        ),
    ]
