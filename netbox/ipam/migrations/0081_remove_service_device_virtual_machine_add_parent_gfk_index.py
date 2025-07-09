from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0126_exporttemplate_file_name'),
        ('ipam', '0080_populate_service_parent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='device',
        ),
        migrations.RemoveField(
            model_name='service',
            name='virtual_machine',
        ),
        migrations.AlterField(
            model_name='service',
            name='parent_object_id',
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name='service',
            name='parent_object_type',
            field=models.ForeignKey(
                on_delete=models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype'
            ),
        ),
        migrations.AddIndex(
            model_name='service',
            index=models.Index(
                fields=['parent_object_type', 'parent_object_id'], name='ipam_servic_parent__563d2b_idx'
            ),
        ),
    ]


def oc_service_remove_fields(objectchange, reverting):
    for data in (objectchange.prechange_data, objectchange.postchange_data):
        if data is not None:
            data.pop('device', None)
            data.pop('virtual_machine', None)


objectchange_migrators = {
    'ipam.service': oc_service_remove_fields,
}
