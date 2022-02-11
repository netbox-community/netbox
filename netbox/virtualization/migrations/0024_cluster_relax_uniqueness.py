from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0136_device_airflow'),
        ('virtualization', '0023_virtualmachine_natural_ordering'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='cluster',
            unique_together={('site', 'name'), ('group', 'name')},
        ),
    ]
