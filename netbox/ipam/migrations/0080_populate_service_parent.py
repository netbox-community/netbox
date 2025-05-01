from django.db import migrations
from django.db.models import F


def populate_service_parent_gfk(apps, schema_config):
    Service = apps.get_model('ipam', 'Service')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Device = apps.get_model('dcim', 'device')
    VirtualMachine = apps.get_model('virtualization', 'virtualmachine')

    Service.objects.filter(device_id__isnull=False).update(
        parent_object_type=ContentType.objects.get_for_model(Device),
        parent_object_id=F('device_id'),
    )

    Service.objects.filter(virtual_machine_id__isnull=False).update(
        parent_object_type=ContentType.objects.get_for_model(VirtualMachine),
        parent_object_id=F('virtual_machine_id'),
    )


def repopulate_device_and_virtualmachine_relations(apps, schemaconfig):
    Service = apps.get_model('ipam', 'Service')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Device = apps.get_model('dcim', 'device')
    VirtualMachine = apps.get_model('virtualization', 'virtualmachine')

    Service.objects.filter(
        parent_object_type=ContentType.objects.get_for_model(Device),
    ).update(
        device_id=F('parent_object_id')
    )

    Service.objects.filter(
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
