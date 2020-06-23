from django.db import migrations, models
import django.db.models.deletion


def set_assigned_object_type(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    IPAddress = apps.get_model('ipam', 'IPAddress')

    device_ct = ContentType.objects.get(app_label='dcim', model='interface').pk
    IPAddress.objects.update(assigned_object_type=device_ct)


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ipam', '0036_standardize_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ipaddress',
            old_name='interface',
            new_name='assigned_object_id',
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='assigned_object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='assigned_object_type',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'dcim'), ('model', 'interface')), models.Q(('app_label', 'virtualization'), ('model', 'vminterface')), _connector='OR')), null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.RunPython(
            code=set_assigned_object_type
        ),
    ]
