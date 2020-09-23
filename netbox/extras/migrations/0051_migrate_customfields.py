from django.db import migrations

from extras.choices import CustomFieldTypeChoices


def deserialize_value(field, value):
    """
    Convert serialized values to JSON equivalents.
    """
    if field.type in (CustomFieldTypeChoices.TYPE_INTEGER):
        return int(value)
    if field.type == CustomFieldTypeChoices.TYPE_BOOLEAN:
        return bool(int(value))
    if field.type == CustomFieldTypeChoices.TYPE_SELECT:
        return field._choices.get(pk=int(value)).value
    return value


def migrate_customfieldchoices(apps, schema_editor):
    """
    Collect all CustomFieldChoices for each applicable CustomField, and save them locally as an array on
    the CustomField instance.
    """
    CustomField = apps.get_model('extras', 'CustomField')
    CustomFieldChoice = apps.get_model('extras', 'CustomFieldChoice')

    for cf in CustomField.objects.filter(type='select'):
        cf.choices = [
            cfc.value for cfc in CustomFieldChoice.objects.filter(field=cf).order_by('weight', 'value')
        ]
        cf.save()


def migrate_customfieldvalues(apps, schema_editor):
    """
    Copy data from CustomFieldValues into the custom_field_data JSON field on each model instance.
    """
    CustomFieldValue = apps.get_model('extras', 'CustomFieldValue')

    for cfv in CustomFieldValue.objects.prefetch_related('field').exclude(serialized_value=''):
        model = apps.get_model(cfv.obj_type.app_label, cfv.obj_type.model)

        # Read and update custom field value for each instance
        # TODO: This can be done more efficiently once .update() is supported for JSON fields
        cf_data = model.objects.filter(pk=cfv.obj_id).values('custom_field_data').first()
        try:
            cf_data['custom_field_data'][cfv.field.name] = deserialize_value(cfv.field, cfv.serialized_value)
        except ValueError as e:
            print(f'{cfv.field.name} ({cfv.field.type}): {cfv.serialized_value} ({cfv.pk})')
            raise e
        model.objects.filter(pk=cfv.obj_id).update(**cf_data)


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0020_custom_field_data'),
        ('dcim', '0117_custom_field_data'),
        ('extras', '0050_customfield_add_choices'),
        ('ipam', '0038_custom_field_data'),
        ('secrets', '0010_custom_field_data'),
        ('tenancy', '0010_custom_field_data'),
        ('virtualization', '0018_custom_field_data'),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_customfieldchoices
        ),
        migrations.RunPython(
            code=migrate_customfieldvalues
        ),
    ]
