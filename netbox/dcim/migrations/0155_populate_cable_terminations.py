from django.db import migrations


def populate_cable_terminations(apps, schema_editor):
    """
    Replicate terminations from the Cable model into CableTermination instances.
    """
    Cable = apps.get_model('dcim', 'Cable')
    CableTermination = apps.get_model('dcim', 'CableTermination')

    # Retrieve the necessary data from Cable objects
    cables = Cable.objects.values(
        'id', 'termination_a_type', 'termination_a_id', 'termination_b_type', 'termination_b_id'
    )

    # Queue CableTerminations to be created
    cable_terminations = []
    for i, cable in enumerate(cables, start=1):
        cable_terminations.append(
            CableTermination(
                cable_id=cable['id'],
                cable_end='A',
                termination_type_id=cable['termination_a_type'],
                termination_id=cable['termination_a_id']
            )
        )
        cable_terminations.append(
            CableTermination(
                cable_id=cable['id'],
                cable_end='B',
                termination_type_id=cable['termination_b_type'],
                termination_id=cable['termination_b_id']
            )
        )

    # Bulk create the termination objects
    CableTermination.objects.bulk_create(cable_terminations, batch_size=100)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0154_cabletermination'),
    ]

    operations = [
        migrations.RunPython(
            code=populate_cable_terminations,
            reverse_code=migrations.RunPython.noop
        ),
    ]
