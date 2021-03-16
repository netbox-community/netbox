import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models

import utilities.validators


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0049_remove_graph'),
    ]

    operations = [
        # Rename reverse relation on CustomFieldChoice
        migrations.AlterField(
            model_name='customfieldchoice',
            name='field',
            field=models.ForeignKey(
                limit_choices_to={'type': 'select'},
                on_delete=django.db.models.deletion.CASCADE,
                related_name='_choices',
                to='extras.customfield'
            ),
        ),
        # Add choices field to CustomField
        migrations.AddField(
            model_name='customfield',
            name='choices',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=100),
                blank=True,
                null=True,
                size=None
            ),
        ),
        # Introduce new default field (to be renamed later)
        migrations.AddField(
            model_name='customfield',
            name='default2',
            field=models.JSONField(blank=True, null=True),
        ),
        # Rename obj_type to content_types
        migrations.RenameField(
            model_name='customfield',
            old_name='obj_type',
            new_name='content_types',
        ),
        # Add validation fields
        migrations.AddField(
            model_name='customfield',
            name='validation_maximum',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customfield',
            name='validation_minimum',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customfield',
            name='validation_regex',
            field=models.CharField(blank=True, max_length=500, validators=[utilities.validators.validate_regex]),
        ),
    ]
