import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0195_interface_vlan_translation_policy'),
        ('ipam', '0075_vlan_qinq'),
    ]

    operations = [
        migrations.AddField(
            model_name='interface',
            name='qinq_svlan',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='%(class)ss_svlan',
                to='ipam.vlan',
            ),
        ),
        migrations.AlterField(
            model_name='interface',
            name='tagged_vlans',
            field=models.ManyToManyField(blank=True, related_name='%(class)ss_as_tagged', to='ipam.vlan'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='untagged_vlan',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='%(class)ss_as_untagged',
                to='ipam.vlan',
            ),
        ),
    ]
