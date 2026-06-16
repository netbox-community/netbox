import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_default_ordering_indexes'),
        ('wireless', '0021_denormalization_triggers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wirelesslan',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='users.owner',
            ),
        ),
        migrations.AlterField(
            model_name='wirelesslangroup',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='users.owner',
            ),
        ),
        migrations.AlterField(
            model_name='wirelesslink',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='users.owner',
            ),
        ),
    ]
