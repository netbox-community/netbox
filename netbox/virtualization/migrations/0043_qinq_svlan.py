import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ipam', '0075_vlan_qinq'),
        ('virtualization', '0042_vminterface_vlan_translation_policy'),
    ]

    operations = [
        migrations.AddField(
            model_name='vminterface',
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
            model_name='vminterface',
            name='tagged_vlans',
            field=models.ManyToManyField(blank=True, related_name='%(class)ss_as_tagged', to='ipam.vlan'),
        ),
        migrations.AlterField(
            model_name='vminterface',
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
