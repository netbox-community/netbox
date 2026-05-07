from django.db import migrations, models

import utilities.jsonschema


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0135_configtemplate_debug'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='validation_schema',
            field=models.JSONField(
                blank=True,
                help_text='A JSON schema definition for validating the custom field value',
                null=True,
                validators=[utilities.jsonschema.validate_schema],
                verbose_name='validation schema',
            ),
        ),
    ]
