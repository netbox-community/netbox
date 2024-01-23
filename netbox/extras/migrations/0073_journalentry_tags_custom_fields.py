from utilities.json import CustomFieldJSONEncoder
from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0072_created_datetimefield'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalentry',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=CustomFieldJSONEncoder),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
    ]
