import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0246_interfacetemplate_channels'),
    ]

    operations = [
        migrations.AddField(
            model_name='interface',
            name='channel_id',
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(1024),
                ],
            ),
        ),
        migrations.AddField(
            model_name='interface',
            name='channels',
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(1024),
                ],
            ),
        ),
        migrations.AddConstraint(
            model_name='interface',
            constraint=models.UniqueConstraint(
                fields=('parent', 'channel_id'),
                name='dcim_interface_unique_parent_channel_id',
            ),
        ),
    ]
