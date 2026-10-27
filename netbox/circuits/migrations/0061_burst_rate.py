from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0060_denormalization_triggers'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuit',
            name='burst_rate',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='virtualcircuit',
            name='burst_rate',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
