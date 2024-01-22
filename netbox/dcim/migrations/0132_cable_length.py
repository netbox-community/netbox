from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0131_consoleport_speed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cable',
            name='length',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
    ]
