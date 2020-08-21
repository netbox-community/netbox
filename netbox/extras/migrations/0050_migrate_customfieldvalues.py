from django.db import migrations

from extras.choices import CustomFieldTypeChoices


def deserialize_value(field_type, value):
    """
    Convert serialized values to JSON equivalents.
    """
    if field_type in (CustomFieldTypeChoices.TYPE_INTEGER, CustomFieldTypeChoices.TYPE_SELECT):
        return int(value)
    if field_type == CustomFieldTypeChoices.TYPE_BOOLEAN:
        return bool(int(value))
    return value


def migrate_customfieldvalues(apps, schema_editor):
    CustomFieldValue = apps.get_model('extras', 'CustomFieldValue')

    for cfv in CustomFieldValue.objects.prefetch_related('field').exclude(serialized_value=''):
        model = apps.get_model(cfv.obj_type.app_label, cfv.obj_type.model)

        # Read and update custom field value for each instance
        # TODO: This can be done more efficiently once .update() is supported for JSON fields
        cf_data = model.objects.filter(pk=cfv.obj_id).values('custom_field_data').first()
        try:
            cf_data['custom_field_data'][cfv.field.name] = deserialize_value(cfv.field.type, cfv.serialized_value)
        except ValueError as e:
            print(f'{cfv.field.name} ({cfv.field.type}): {cfv.serialized_value} ({cfv.pk})')
            raise e
        model.objects.filter(pk=cfv.obj_id).update(**cf_data)


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0020_custom_field_data'),
        ('dcim', '0115_custom_field_data'),
        ('extras', '0049_remove_graph'),
        ('ipam', '0038_custom_field_data'),
        ('secrets', '0010_custom_field_data'),
        ('tenancy', '0010_custom_field_data'),
        ('virtualization', '0018_custom_field_data'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_customfieldvalues
        ),
    ]
