import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dummy_plugin', '0001_initial'),
        ('extras', '0122_charfield_null_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='dummymodel',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='dummymodel',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
        ),
        migrations.AddField(
            model_name='dummymodel',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='dummymodel',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
    ]
