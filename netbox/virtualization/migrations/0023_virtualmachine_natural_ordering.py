from django.db import migrations
import utilities.fields
import utilities.ordering


def naturalize_virtualmachines(apps, schema_editor):
    VirtualMachine = apps.get_model('virtualization', 'VirtualMachine')
    for name in VirtualMachine.objects.values_list('name', flat=True).order_by('name').distinct():
        VirtualMachine.objects.filter(name=name).update(_name=utilities.ordering.naturalize(name, max_length=100))


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0022_vminterface_parent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='virtualmachine',
            options={'ordering': ('_name', 'pk')},
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='_name',
            field=utilities.fields.NaturalOrderingField('name', max_length=100, blank=True, naturalize_function=utilities.ordering.naturalize),
        ),
        migrations.RunPython(
            code=naturalize_virtualmachines,
            reverse_code=migrations.RunPython.noop
        ),
    ]
