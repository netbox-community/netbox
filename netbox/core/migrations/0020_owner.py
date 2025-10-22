import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0019_configrevision_active'),
        ('users', '0015_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasource',
            name='owner',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner'
            ),
        ),
    ]
