from django.db import migrations, models


def populate__ports_lowest(apps, schema_editor):
    # Populate Service
    Service = apps.get_model('ipam', 'Service')
    CHUNK_SIZE = 500
    chunk = []
    service_objects = Service.objects.filter(_ports_lowest__isnull=True).only('id', 'ports', '_ports_lowest')
    for service in service_objects.iterator(chunk_size=CHUNK_SIZE):
        if service.ports:
            service._ports_lowest = min(service.ports)
            chunk.append(service)

        if len(chunk) >= CHUNK_SIZE:
            Service.objects.bulk_update(chunk, ['_ports_lowest'])
            chunk = []
    if chunk:
        Service.objects.bulk_update(chunk, ['_ports_lowest'])

    # Populate ServiceTemplate
    ServiceTemplate = apps.get_model('ipam', 'ServiceTemplate')
    chunk = []
    template_objects = ServiceTemplate.objects.filter(_ports_lowest__isnull=True).only('id', 'ports', '_ports_lowest')
    for template in template_objects.iterator(chunk_size=CHUNK_SIZE):
        if template.ports:
            template._ports_lowest = min(template.ports)
            chunk.append(template)

        if len(chunk) >= CHUNK_SIZE:
            ServiceTemplate.objects.bulk_update(chunk, ['_ports_lowest'])
            chunk = []
    if chunk:
        ServiceTemplate.objects.bulk_update(chunk, ['_ports_lowest'])


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0090_vlangroup_recompute_total_vlan_ids'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='service',
            name='ipam_servic_protoco_687d13_idx',
        ),
        migrations.AddField(
            model_name='service',
            name='_ports_lowest',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='servicetemplate',
            name='_ports_lowest',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(populate__ports_lowest, migrations.RunPython.noop),
        migrations.AddIndex(
            model_name='service',
            index=models.Index(
                fields=['protocol', '_ports_lowest', 'id'],
                name='ipam_servic_protoco_e2901d_idx'
            ),
        ),
        migrations.AlterModelOptions(
            name='service',
            options={
                'ordering': ('protocol', '_ports_lowest', 'id')
            },
        ),
    ]
