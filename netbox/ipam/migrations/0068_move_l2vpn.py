from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0067_ipaddress_index_host'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='l2vpntermination',
            name='ipam_l2vpntermination_assigned_object',
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='l2vpntermination',
                    name='assigned_object_type',
                ),
                migrations.RemoveField(
                    model_name='l2vpntermination',
                    name='l2vpn',
                ),
                migrations.RemoveField(
                    model_name='l2vpntermination',
                    name='tags',
                ),
                migrations.DeleteModel(
                    name='L2VPN',
                ),
                migrations.DeleteModel(
                    name='L2VPNTermination',
                ),
            ],
            database_operations=[
                migrations.AlterModelTable(
                    name='L2VPN',
                    table='vpn_l2vpn',
                ),
                migrations.AlterModelTable(
                    name='L2VPNTermination',
                    table='vpn_l2vpntermination',
                ),
            ],
        ),
    ]
