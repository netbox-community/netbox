import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0217_poweroutlettemplate_color'),
        ('users', '0015_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='cable',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='devicerole',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='frontport',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='interface',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='inventoryitemrole',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='location',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='macaddress',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='module',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='modulebay',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='moduletypeprofile',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='platform',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='powerpanel',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='powerport',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='rack',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='rackreservation',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='rackrole',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='racktype',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='rearport',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='region',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='site',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='sitegroup',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='virtualchassis',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
        migrations.AddField(
            model_name='virtualdevicecontext',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
    ]
