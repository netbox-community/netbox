from django.db import migrations, models


def set_null_values(apps, schema_editor):
    """
    Replace empty strings with null values.
    """
    Circuit = apps.get_model('circuits', 'Circuit')
    CircuitGroupAssignment = apps.get_model('circuits', 'CircuitGroupAssignment')
    CircuitTermination = apps.get_model('circuits', 'CircuitTermination')
    db_alias = schema_editor.connection.alias

    Circuit.objects.using(db_alias).filter(distance_unit='').update(distance_unit=None)
    CircuitGroupAssignment.objects.using(db_alias).filter(priority='').update(priority=None)
    CircuitTermination.objects.using(db_alias).filter(cable_end='').update(cable_end=None)


class Migration(migrations.Migration):
    dependencies = [
        ('circuits', '0045_circuit_distance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circuit',
            name='distance_unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='circuitgroupassignment',
            name='priority',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.RunPython(code=set_null_values, reverse_code=migrations.RunPython.noop),
    ]
