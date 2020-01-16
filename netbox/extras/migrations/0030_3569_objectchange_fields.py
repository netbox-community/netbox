from django.db import migrations, models


OBJECTCHANGE_ACTION_CHOICES = (
    (1, 'create'),
    (2, 'update'),
    (3, 'delete'),
)


def objectchange_action_to_slug(apps, schema_editor):
    ObjectChange = apps.get_model('extras', 'ObjectChange')
    for id, slug in OBJECTCHANGE_ACTION_CHOICES:
        ObjectChange.objects.filter(action=str(id)).update(action=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('extras', '0029_3569_customfield_fields'),
    ]

    operations = [

        # ObjectChange.action
        migrations.AlterField(
            model_name='objectchange',
            name='action',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=objectchange_action_to_slug
        ),

    ]
