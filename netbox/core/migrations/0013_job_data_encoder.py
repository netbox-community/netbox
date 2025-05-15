import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_job_object_type_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='data',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True),
        ),
    ]
