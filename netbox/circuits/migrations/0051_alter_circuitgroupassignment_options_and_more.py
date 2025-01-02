from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0050_virtual_circuits'),
        ('extras', '0122_charfield_null_choices'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='circuitgroupassignment',
            options={'ordering': ('group', 'member', 'priority', 'pk')},
        ),
        migrations.RemoveConstraint(
            model_name='circuitgroupassignment',
            name='circuits_circuitgroupassignment_unique_circuit_group',
        ),
        migrations.RenameField(
            model_name='circuitgroupassignment',
            old_name='circuit',
            new_name='member',
        ),
        migrations.AddConstraint(
            model_name='circuitgroupassignment',
            constraint=models.UniqueConstraint(
                fields=('member', 'group'),
                name='circuits_circuitgroupassignment_unique_member_group'
            ),
        ),
    ]
