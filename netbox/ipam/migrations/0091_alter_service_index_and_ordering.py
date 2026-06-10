from django.db import migrations, models


def populate__ports_lowest(apps, schema_editor):
    Service = apps.get_model('ipam', 'Service')
    ServiceTemplate = apps.get_model('ipam', 'ServiceTemplate')
    CHUNK_SIZE = 500

    for model in (Service, ServiceTemplate):
        chunk = []
        qs = model.objects.filter(_ports_lowest__isnull=True).only('id', 'ports', '_ports_lowest')
        for obj in qs.iterator(chunk_size=CHUNK_SIZE):
            if obj.ports:
                obj._ports_lowest = min(service.ports)
                chunk.append(obj)
            if len(chunk) >= CHUNK_SIZE:
                model.objects.bulk_update(chunk, ['_ports_lowest'])
                chunk = []
        if chunk:
            model.objects.bulk_update(chunk, ['_ports_lowest'])


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
