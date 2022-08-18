import sys

from django.db import migrations


def cache_related_objects(termination):
    """
    Replicate caching logic from CableTermination.cache_related_objects()
    """
    attrs = {}

    # Device components
    if getattr(termination, 'device', None):
        attrs['_device'] = termination.device
        attrs['_rack'] = termination.device.rack
        attrs['_location'] = termination.device.location
        attrs['_site'] = termination.device.site

    # Power feeds
    elif getattr(termination, 'rack', None):
        attrs['_rack'] = termination.rack
        attrs['_location'] = termination.rack.location
        attrs['_site'] = termination.rack.site

    # Circuit terminations
    elif getattr(termination, 'site', None):
        attrs['_site'] = termination.site

    return attrs


def populate_cable_terminations(apps, schema_editor):
    """
    Replicate terminations from the Cable model into CableTermination instances.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Cable = apps.get_model('dcim', 'Cable')
    CableTermination = apps.get_model('dcim', 'CableTermination')

    # Retrieve the necessary data from Cable objects
    cables = Cable.objects.values(
        'id', 'termination_a_type', 'termination_a_id', 'termination_b_type', 'termination_b_id'
    )

    # Queue CableTerminations to be created
    cable_terminations = []
    cable_count = cables.count()
    for i, cable in enumerate(cables, start=1):
        for cable_end in ('a', 'b'):
            # We must manually instantiate the termination object, because GFK fields are not
            # supported within migrations.
            termination_ct = ContentType.objects.get(pk=cable[f'termination_{cable_end}_type'])
            termination_model = apps.get_model(termination_ct.app_label, termination_ct.model)
            termination = termination_model.objects.get(pk=cable[f'termination_{cable_end}_id'])

            cable_terminations.append(CableTermination(
                cable_id=cable['id'],
                cable_end=cable_end.upper(),
                termination_type_id=cable[f'termination_{cable_end}_type'],
                termination_id=cable[f'termination_{cable_end}_id'],
                **cache_related_objects(termination)
            ))

        # Output progress occasionally
        if 'test' not in sys.argv and not i % 100:
            progress = float(i) * 100 / cable_count
            if i == 100:
                print('')
            sys.stdout.write(f"\r    Updated {i}/{cable_count} cables ({progress:.2f}%)")
            sys.stdout.flush()

    # Bulk create the termination objects
    CableTermination.objects.bulk_create(cable_terminations, batch_size=100)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0157_new_cabling_models'),
    ]

    operations = [
        migrations.RunPython(
            code=populate_cable_terminations,
            reverse_code=migrations.RunPython.noop
        ),
    ]
