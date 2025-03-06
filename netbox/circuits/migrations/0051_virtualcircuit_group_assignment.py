import django.db.models.deletion
from django.db import migrations, models


def set_member_type(apps, schema_editor):
    """
    Set member_type on any existing CircuitGroupAssignments to the content type for Circuit.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Circuit = apps.get_model('circuits', 'Circuit')
    CircuitGroupAssignment = apps.get_model('circuits', 'CircuitGroupAssignment')

    CircuitGroupAssignment.objects.update(
        member_type=ContentType.objects.get_for_model(Circuit)
    )


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0050_virtual_circuits'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0122_charfield_null_choices'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='circuitgroupassignment',
            name='circuits_circuitgroupassignment_unique_circuit_group',
        ),
        migrations.AlterModelOptions(
            name='circuitgroupassignment',
            options={'ordering': ('group', 'member_type', 'member_id', 'priority', 'pk')},
        ),

        # Change member_id to an integer field for the member GFK
        migrations.RenameField(
            model_name='circuitgroupassignment',
            old_name='circuit',
            new_name='member_id',
        ),
        migrations.AlterField(
            model_name='circuitgroupassignment',
            name='member_id',
            field=models.PositiveBigIntegerField(),
        ),

        # Add content type pointer for the member GFK
        migrations.AddField(
            model_name='circuitgroupassignment',
            name='member_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                limit_choices_to=models.Q(('app_label', 'circuits'), ('model__in', ['circuit', 'virtualcircuit'])),
                related_name='+',
                to='contenttypes.contenttype',
                blank=True,
                null=True
            ),
            preserve_default=False,
        ),

        # Populate member_type for any existing assignments
        migrations.RunPython(code=set_member_type, reverse_code=migrations.RunPython.noop),

        # Disallow null values for member_type
        migrations.AlterField(
            model_name='circuitgroupassignment',
            name='member_type',
            field=models.ForeignKey(
                limit_choices_to=models.Q(('app_label', 'circuits'), ('model__in', ['circuit', 'virtualcircuit'])),
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='contenttypes.contenttype'
            ),
        ),

        migrations.AddConstraint(
            model_name='circuitgroupassignment',
            constraint=models.UniqueConstraint(
                fields=('member_type', 'member_id', 'group'),
                name='circuits_circuitgroupassignment_unique_member_group'
            ),
        ),
    ]
