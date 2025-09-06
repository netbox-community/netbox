from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0132_configcontextprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfield',
            name='validation_maximum',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=16, null=True),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='validation_minimum',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=16, null=True),
        ),
    ]
