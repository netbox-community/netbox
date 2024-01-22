from django.db import migrations

OLD_VALUE = '128gfc-sfp28'
NEW_VALUE = '128gfc-qsfp28'


def correct_type(apps, schema_editor):
    """
    Correct TYPE_128GFC_QSFP28 interface type.
    """
    Interface = apps.get_model('dcim', 'Interface')
    InterfaceTemplate = apps.get_model('dcim', 'InterfaceTemplate')

    for model in (Interface, InterfaceTemplate):
        model.objects.filter(type=OLD_VALUE).update(type=NEW_VALUE)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0141_asn_model'),
    ]

    operations = [
        migrations.RunPython(
            code=correct_type,
            reverse_code=migrations.RunPython.noop
        ),
    ]
