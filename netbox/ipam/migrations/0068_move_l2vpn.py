from django.db import migrations


def update_content_types(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Delete the new ContentTypes effected by the new models in the vpn app
    ContentType.objects.filter(app_label='vpn', model='l2vpn').delete()
    ContentType.objects.filter(app_label='vpn', model='l2vpntermination').delete()

    # Update the app labels of the original ContentTypes for ipam.L2VPN and ipam.L2VPNTermination to ensure
    # that any foreign key references are preserved
    ContentType.objects.filter(app_label='ipam', model='l2vpn').update(app_label='vpn')
    ContentType.objects.filter(app_label='ipam', model='l2vpntermination').update(app_label='vpn')


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
        migrations.RunPython(
            code=update_content_types,
            reverse_code=migrations.RunPython.noop
        ),
    ]
