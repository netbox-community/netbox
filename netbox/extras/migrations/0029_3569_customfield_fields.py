from django.db import migrations, models
import django.db.models.deletion


CUSTOMFIELD_TYPE_CHOICES = (
    (100, 'text'),
    (200, 'integer'),
    (300, 'boolean'),
    (400, 'date'),
    (500, 'url'),
    (600, 'select')
)

CUSTOMFIELD_FILTER_LOGIC_CHOICES = (
    (0, 'disabled'),
    (1, 'integer'),
    (2, 'exact'),
)


def customfield_type_to_slug(apps, schema_editor):
    CustomField = apps.get_model('extras', 'CustomField')
    for id, slug in CUSTOMFIELD_TYPE_CHOICES:
        CustomField.objects.filter(type=str(id)).update(type=slug)


def customfield_filter_logic_to_slug(apps, schema_editor):
    CustomField = apps.get_model('extras', 'CustomField')
    for id, slug in CUSTOMFIELD_FILTER_LOGIC_CHOICES:
        CustomField.objects.filter(filter_logic=str(id)).update(filter_logic=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('extras', '0028_remove_topology_maps'),
    ]

    operations = [

        # CustomField.type
        migrations.AlterField(
            model_name='customfield',
            name='type',
            field=models.CharField(default='text', max_length=50),
        ),
        migrations.RunPython(
            code=customfield_type_to_slug
        ),

        # Update CustomFieldChoice.field.limit_choices_to
        migrations.AlterField(
            model_name='customfieldchoice',
            name='field',
            field=models.ForeignKey(limit_choices_to={'type': 'select'}, on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='extras.CustomField'),
        ),

        # CustomField.filter_logic
        migrations.AlterField(
            model_name='customfield',
            name='filter_logic',
            field=models.CharField(default='loose', max_length=50),
        ),
        migrations.RunPython(
            code=customfield_filter_logic_to_slug
        ),

    ]
