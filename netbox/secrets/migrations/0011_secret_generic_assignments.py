from django.db import migrations, models
import django.db.models.deletion


def device_to_generic_assignment(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Device = apps.get_model('dcim', 'Device')
    Secret = apps.get_model('secrets', 'Secret')

    device_ct = ContentType.objects.get_for_model(Device)
    Secret.objects.update(assigned_object_type=device_ct, assigned_object_id=models.F('device_id'))


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('secrets', '0010_custom_field_data'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='secret',
            options={'ordering': ('role', 'name', 'pk')},
        ),

        # Add assigned_object type & ID fields
        migrations.AddField(
            model_name='secret',
            name='assigned_object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='secret',
            name='assigned_object_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype'),
            preserve_default=False,
        ),

        migrations.AlterUniqueTogether(
            name='secret',
            unique_together={('assigned_object_type', 'assigned_object_id', 'role', 'name')},
        ),

        # Copy device assignments and delete device ForeignKey
        migrations.RunPython(
            code=device_to_generic_assignment,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name='secret',
            name='device',
        ),

        # Remove blank/null from assigned_object fields
        migrations.AlterField(
            model_name='secret',
            name='assigned_object_id',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='secret',
            name='assigned_object_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype'),
        ),
    ]
