import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


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
        # Rename obj_type to content_types
        migrations.RenameField(
            model_name='customfield',
            old_name='obj_type',
            new_name='content_types',
        ),
    ]
