from django.contrib.postgres.fields import ArrayField
from django.db import migrations
from django.db.models import ExpressionWrapper, F


def copy_termination_ids(apps, schema_editor):
    """
    Copy original A & B termination ID values to new array fields.
    """
    Cable = apps.get_model('dcim', 'Cable')

    # TODO: Optimize data migration using F expressions
    # Cable.objects.update(
    #     termination_a_ids=ExpressionWrapper(F('termination_a_id'), output_field=ArrayField),
    #     termination_b_ids=ExpressionWrapper(F('termination_b_id'), output_field=ArrayField)
    # )

    for cable in Cable.objects.all():
        Cable.objects.filter(pk=cable.pk).update(
            termination_a_ids=[cable.termination_a_id],
            termination_b_ids=[cable.termination_b_id]
        )


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0154_cable_add_termination_id_arrays'),
    ]

    operations = [
        migrations.RunPython(
            code=copy_termination_ids,
            reverse_code=migrations.RunPython.noop
        ),
    ]
