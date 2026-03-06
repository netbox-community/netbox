from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('ipam', '0086_gfk_indexes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vlangroup',
            old_name='_total_vlan_ids',
            new_name='total_vlan_ids',
        ),
    ]
