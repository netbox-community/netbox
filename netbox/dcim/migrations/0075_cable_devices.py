from django.db import migrations, models
import django.db.models.deletion


def cache_cable_devices(apps, schema_editor):
    Cable = apps.get_model('dcim', 'Cable')

    # Cache A/B termination devices on all existing Cables. Note that the custom save() method on Cable is not
    # available during a migration, so we replicate its logic here.
    for cable in Cable.objects.all():

        termination_a_model = apps.get_model(cable.termination_a_type.app_label, cable.termination_a_type.model)
        if hasattr(termination_a_model, 'device'):
            termination_a = termination_a_model.objects.get(pk=cable.termination_a_id)
            cable._termination_a_device = termination_a.device

        termination_b_model = apps.get_model(cable.termination_b_type.app_label, cable.termination_b_type.model)
        if hasattr(termination_b_model, 'device'):
            termination_b = termination_b_model.objects.get(pk=cable.termination_b_id)
            cable._termination_b_device = termination_b.device

        cable.save()


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0074_increase_field_length_platform_name_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='cable',
            name='_termination_a_device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.Device'),
        ),
        migrations.AddField(
            model_name='cable',
            name='_termination_b_device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.Device'),
        ),
        migrations.RunPython(
            code=cache_cable_devices,
            reverse_code=migrations.RunPython.noop
        ),
    ]
