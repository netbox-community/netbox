from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0228_cable_bundle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='rf_channel_frequency',
            field=models.DecimalField(
                blank=True,
                decimal_places=3,
                help_text='Populated by selected channel (if set)',
                max_digits=8,
                null=True,
                verbose_name='channel frequency (MHz)',
            ),
        ),
    ]
