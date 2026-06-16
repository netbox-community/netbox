import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_default_ordering_indexes'),
        ('vpn', '0012_default_ordering_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ikepolicy',
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
            model_name='ikeproposal',
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
            model_name='ipsecpolicy',
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
            model_name='ipsecprofile',
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
            model_name='ipsecproposal',
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
            model_name='l2vpn',
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
            model_name='tunnel',
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
            model_name='tunnelgroup',
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
