import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_job_notifications'),
        ('users', '0016_default_ordering_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasource',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='users.owner',
            ),
        ),
    ]
