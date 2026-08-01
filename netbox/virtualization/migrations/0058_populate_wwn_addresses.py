import django.db.models.deletion
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models


def populate_wwn_addresses(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    VMInterface = apps.get_model('virtualization', 'VMInterface')
    WWNAddress = apps.get_model('dcim', 'WWNAddress')
    db_alias = schema_editor.connection.alias
    vminterface_ct = ContentType.objects.get_for_model(VMInterface)

    wwn_addresses = [
        WWNAddress(
            wwn_address=vminterface.wwn,
            assigned_object_type=vminterface_ct,
            assigned_object_id=vminterface.pk
        )
        for vminterface in VMInterface.objects.using(db_alias).filter(wwn__isnull=False)
    ]
    WWNAddress.objects.using(db_alias).bulk_create(wwn_addresses, batch_size=100)

    # TODO: Optimize interface updates
    for wwn_address in wwn_addresses:
        VMInterface.objects.using(db_alias).filter(pk=wwn_address.assigned_object_id).update(
            primary_wwn_address=wwn_address
        )


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0243_populate_wwn_addresses'),
        ('virtualization', '0057_alter_cluster__region_alter_cluster__site_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='vminterface',
            name='primary_wwn_address',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='dcim.wwnaddress',
            ),
        ),
        migrations.RunPython(code=populate_wwn_addresses, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='vminterface',
            name='wwn',
        ),
    ]


# See peer migrator in dcim.0243_populate_wwn_addresses before making changes
def oc_vminterface_primary_wwn_address(objectchange, reverting):
    WWNAddress = apps.get_model('dcim', 'WWNAddress')
    vminterface_ct = ContentType.objects.get_by_natural_key('virtualization', 'vminterface')

    # Swap data order if the change is being reverted
    if not reverting:
        before, after = objectchange.prechange_data, objectchange.postchange_data
    else:
        before, after = objectchange.postchange_data, objectchange.prechange_data

    if after.get('wwn') != before.get('wwn'):
        # Create & assign the new WWNAddress (if any)
        if after.get('wwn'):
            wwn = WWNAddress.objects.create(
                wwn_address=after['wwn'],
                assigned_object_type=vminterface_ct,
                assigned_object_id=objectchange.changed_object_id,
            )
            after['primary_wwn_address'] = wwn.pk
        else:
            after['primary_wwn_address'] = None
        # Delete the old WWNAddress (if any)
        if before.get('wwn'):
            WWNAddress.objects.filter(
                wwn_address=before['wwn'],
                assigned_object_type=vminterface_ct,
                assigned_object_id=objectchange.changed_object_id,
            ).delete()
        before['primary_wwn_address'] = None

    before.pop('wwn', None)
    after.pop('wwn', None)


objectchange_migrators = {
    'virtualization.vminterface': oc_vminterface_primary_wwn_address,
}
