import django.contrib.postgres.fields
import django.core.serializers.json
from django.db import migrations, models

import utilities.json


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_remove_redundant_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='log_entries',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.JSONField(
                    decoder=utilities.json.JobLogDecoder,
                    encoder=django.core.serializers.json.DjangoJSONEncoder
                ),
                blank=True,
                default=list,
                size=None
            ),
        ),
    ]
