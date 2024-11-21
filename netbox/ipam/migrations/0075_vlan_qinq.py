import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ipam', '0074_vlantranslationpolicy_vlantranslationrule'),
    ]

    operations = [
        migrations.AddField(
            model_name='vlan',
            name='qinq_role',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='vlan',
            name='qinq_svlan',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='qinq_cvlans',
                to='ipam.vlan',
            ),
        ),
        migrations.AddConstraint(
            model_name='vlan',
            constraint=models.UniqueConstraint(fields=('qinq_svlan', 'vid'), name='ipam_vlan_unique_qinq_svlan_vid'),
        ),
        migrations.AddConstraint(
            model_name='vlan',
            constraint=models.UniqueConstraint(fields=('qinq_svlan', 'name'), name='ipam_vlan_unique_qinq_svlan_name'),
        ),
    ]
