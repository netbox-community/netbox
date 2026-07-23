import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0245_modulebaytype'),
    ]

    operations = [
        migrations.AddField(
            model_name='interfacetemplate',
            name='parent',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.RESTRICT,
                related_name='child_interfaces',
                to='dcim.interfacetemplate',
            ),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
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
            model_name='interfacetemplate',
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
            model_name='interfacetemplate',
            constraint=models.UniqueConstraint(
                fields=('parent', 'channel_id'),
                name='dcim_interfacetemplate_unique_parent_channel_id',
            ),
        ),
    ]
