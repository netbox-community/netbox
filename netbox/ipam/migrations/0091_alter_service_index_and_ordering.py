from django.db import migrations, models


def populate__min_ports(apps, schema_editor):
    Service = apps.get_model('ipam', 'Service')
    CHUNK_SIZE = 500
    chunk = []
    service_objects = Service.objects.filter(_min_port__isnull=True).only('id', 'ports', '_min_port')
    for service in service_objects.iterator(chunk_size=CHUNK_SIZE):
        if service.ports:
            service._min_port = min(service.ports)
            chunk.append(service)

        if len(chunk) >= CHUNK_SIZE:
            Service.objects.bulk_update(chunk, ['_min_port'])
            chunk = []
    if chunk:
        Service.objects.bulk_update(chunk, ['_min_port'])


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
            name='_min_port',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(populate__min_ports, migrations.RunPython.noop),
        migrations.AddIndex(
            model_name='service',
            index=models.Index(
                fields=['name', 'protocol', '_min_port', 'id'],
                name='ipam_servic_name_ef1f28_idx'
            ),
        ),
        migrations.AlterModelOptions(
            name='service',
            options={
                'ordering': ('name', 'protocol', '_min_port', 'id')
            },
        ),
    ]
