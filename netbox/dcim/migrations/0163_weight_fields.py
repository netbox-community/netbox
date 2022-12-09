from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0162_unique_constraints'),
    ]

    operations = [

        # Device types
        migrations.AddField(
            model_name='devicetype',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='weight_unit',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='_abs_weight',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),

        # Module types
        migrations.AddField(
            model_name='moduletype',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='weight_unit',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='_abs_weight',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),

        # Racks
        migrations.AddField(
            model_name='rack',
            name='weight',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='rack',
            name='max_weight',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rack',
            name='weight_unit',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='rack',
            name='_abs_weight',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rack',
            name='_abs_max_weight',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]
