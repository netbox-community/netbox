from django.db import migrations, models


def set_null_values(apps, schema_editor):
    """
    Replace empty strings with null values.
    """
    CustomFieldChoiceSet = apps.get_model('extras', 'CustomFieldChoiceSet')

    CustomFieldChoiceSet.objects.filter(base_choices='').update(base_choices=None)


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0121_customfield_related_object_filter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfieldchoiceset',
            name='base_choices',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.RunPython(
            code=set_null_values,
            reverse_code=migrations.RunPython.noop
        ),
    ]
