from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0167_module_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='cabletermination',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='cabletermination',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
