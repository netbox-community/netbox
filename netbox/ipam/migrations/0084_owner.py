import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ipam', '0083_vlangroup_populate_total_vlan_ids'),
        ('users', '0015_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='aggregate',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='asn',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='asnrange',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='fhrpgroup',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='iprange',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='prefix',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='rir',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='role',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='routetarget',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='service',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='servicetemplate',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='vlan',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='vlangroup',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='vlantranslationpolicy',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='vrf',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
    ]
