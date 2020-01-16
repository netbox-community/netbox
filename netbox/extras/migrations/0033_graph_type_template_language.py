from django.db import migrations, models
import django.db.models.deletion


GRAPH_TYPE_CHOICES = (
    (100, 'dcim', 'interface'),
    (150, 'dcim', 'device'),
    (200, 'circuits', 'provider'),
    (300, 'dcim', 'site'),
)


def graph_type_to_fk(apps, schema_editor):
    Graph = apps.get_model('extras', 'Graph')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # On a new installation (and during tests) content types might not yet exist. So, we only perform the bulk
    # updates if a Graph has been created, which implies that we're working with a populated database.
    if Graph.objects.exists():
        for id, app_label, model in GRAPH_TYPE_CHOICES:
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            Graph.objects.filter(type=id).update(type=content_type.pk)


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0032_3569_webhook_fields'),
    ]

    operations = [
        # We have to swap the legacy IDs to ContentType PKs *before* we alter the field, to avoid triggering an
        # IntegrityError on the ForeignKey.
        migrations.RunPython(
            code=graph_type_to_fk
        ),
        migrations.AlterField(
            model_name='graph',
            name='type',
            field=models.ForeignKey(
                limit_choices_to={'model__in': ['provider', 'device', 'interface', 'site']},
                on_delete=django.db.models.deletion.CASCADE,
                to='contenttypes.ContentType'
            ),
        ),

        # Add the template_language field with an initial default of Django to preserve current behavior. Then,
        # alter the field to set the default for any *new* Graphs to Jinja2.
        migrations.AddField(
            model_name='graph',
            name='template_language',
            field=models.CharField(default='django', max_length=50),
        ),
        migrations.AlterField(
            model_name='graph',
            name='template_language',
            field=models.CharField(default='jinja2', max_length=50),
        ),
    ]
