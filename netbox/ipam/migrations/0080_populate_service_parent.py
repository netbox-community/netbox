from django.contrib.contenttypes.models import ContentType
from django.db import migrations
from django.db.models import F


def populate_service_parent_gfk(apps, schema_editor):
    Service = apps.get_model('ipam', 'Service')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Device = apps.get_model('dcim', 'device')
    VirtualMachine = apps.get_model('virtualization', 'virtualmachine')
    db_alias = schema_editor.connection.alias

    Service.objects.using(db_alias).filter(device_id__isnull=False).update(
        parent_object_type=ContentType.objects.get_for_model(Device),
        parent_object_id=F('device_id'),
    )

    Service.objects.using(db_alias).filter(virtual_machine_id__isnull=False).update(
        parent_object_type=ContentType.objects.get_for_model(VirtualMachine),
        parent_object_id=F('virtual_machine_id'),
    )


def repopulate_device_and_virtualmachine_relations(apps, schema_editor):
    Service = apps.get_model('ipam', 'Service')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Device = apps.get_model('dcim', 'device')
    VirtualMachine = apps.get_model('virtualization', 'virtualmachine')
    db_alias = schema_editor.connection.alias

    Service.objects.using(db_alias).filter(
        parent_object_type=ContentType.objects.get_for_model(Device),
    ).update(
        device_id=F('parent_object_id')
    )

    Service.objects.using(db_alias).filter(
        parent_object_type=ContentType.objects.get_for_model(VirtualMachine),
    ).update(
        virtual_machine_id=F('parent_object_id')
    )


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0202_location_comments_region_comments_sitegroup_comments'),
        ('ipam', '0079_add_service_fhrp_group_parent_gfk'),
        ('virtualization', '0048_populate_mac_addresses'),
    ]

    operations = [
            migrations.RunPython(
                populate_service_parent_gfk,
                reverse_code=repopulate_device_and_virtualmachine_relations,
            )
    ]


def oc_service_parent(objectchange, reverting):
    device_ct = ContentType.objects.get_by_natural_key('dcim', 'device').pk
    virtual_machine_ct = ContentType.objects.get_by_natural_key('virtualization', 'virtualmachine').pk
    for data in (objectchange.prechange_data, objectchange.postchange_data):
        if data is None:
            continue
        if device_id := data.get('device'):
            data.update({
                'parent_object_type': device_ct,
                'parent_object_id': device_id,
            })
        elif virtual_machine_id := data.get('virtual_machine'):
            data.update({
                'parent_object_type': virtual_machine_ct,
                'parent_object_id': virtual_machine_id,
            })


objectchange_migrators = {
    'ipam.service': oc_service_parent,
}
