import django.contrib.postgres.fields
from django.db import migrations, models

from extras.choices import CustomFieldTypeChoices


def create_choice_sets(apps, schema_editor):
    """
    Create a CustomFieldChoiceSet for each CustomField with choices defined.
    """
    CustomField = apps.get_model('extras', 'CustomField')
    CustomFieldChoiceSet = apps.get_model('extras', 'CustomFieldChoiceSet')

    # Create custom field choice sets
    choice_fields = CustomField.objects.filter(
        type__in=(CustomFieldTypeChoices.TYPE_SELECT, CustomFieldTypeChoices.TYPE_MULTISELECT),
        choices__len__gt=0
    )
    for cf in choice_fields:
        choiceset = CustomFieldChoiceSet.objects.create(
            name=f'{cf.name} Choices',
            extra_choices=tuple(zip(cf.choices, cf.choices))  # Convert list to tuple of two-tuples
        )
        cf.choice_set = choiceset

    # Update custom fields to point to new choice sets
    CustomField.objects.bulk_update(choice_fields, ['choice_set'])


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0095_bookmarks'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomFieldChoiceSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('base_choices', models.CharField(blank=True, max_length=50)),
                ('extra_choices', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), size=2), blank=True, null=True, size=None)),
                ('order_alphabetically', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='customfield',
            name='choice_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='choices_for', to='extras.customfieldchoiceset'),
        ),
        migrations.RunPython(
            code=create_choice_sets,
            reverse_code=migrations.RunPython.noop
        ),
    ]
