import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0078_unique_constraints'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobresult',
            name='scheduled',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='jobresult',
            name='interval',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='jobresult',
            name='started',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterModelOptions(
            name='jobresult',
            options={'ordering': ['-created']},
        ),
    ]
