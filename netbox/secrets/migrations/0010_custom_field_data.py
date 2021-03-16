import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('secrets', '0009_secretrole_drop_users_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='secret',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
    ]
