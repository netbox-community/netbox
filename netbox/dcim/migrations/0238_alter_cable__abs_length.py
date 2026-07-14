from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0237_module_remove_local_context_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cable',
            name='_abs_length',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=14, null=True),
        ),
    ]
