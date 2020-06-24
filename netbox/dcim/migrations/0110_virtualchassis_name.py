from django.db import migrations, models
import django.db.models.deletion


def copy_master_name(apps, schema_editor):
    """
    Copy the master device's name to the VirtualChassis.
    """
    VirtualChassis = apps.get_model('dcim', 'VirtualChassis')

    for vc in VirtualChassis.objects.prefetch_related('master'):
        name = vc.master.name if vc.master.name else f'Unnamed VC #{vc.pk}'
        VirtualChassis.objects.filter(pk=vc.pk).update(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0109_interface_remove_vm'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='virtualchassis',
            options={'ordering': ['name'], 'verbose_name_plural': 'virtual chassis'},
        ),
        migrations.AddField(
            model_name='virtualchassis',
            name='name',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='virtualchassis',
            name='master',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vc_master_for', to='dcim.Device'),
        ),
        migrations.RunPython(
            code=copy_master_name,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name='virtualchassis',
            name='name',
            field=models.CharField(max_length=64),
        ),
    ]
