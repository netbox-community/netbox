import django.core.serializers.json
from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0035_provider_asns'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuit',
            name='termination_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
    ]
