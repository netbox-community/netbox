from django.db import migrations
from django.db.models import CharField, F, Func

BATCH_SIZE = 5000


def populate_prefix_classification(apps, schema_editor):
    """
    Classify existing prefixes in batches, skipping rows whose stored value is already correct.
    """
    Prefix = apps.get_model('ipam', 'Prefix')
    prefixes = Prefix.objects.using(schema_editor.connection.alias)
    classification = Func(F('prefix'), function='ipam_prefix_classification', output_field=CharField())
    pending = prefixes.exclude(_classification=classification).order_by('pk')

    # Primary keys may be zero or negative, so the first batch has no lower bound
    batch = pending
    while pks := list(batch.values_list('pk', flat=True)[:BATCH_SIZE]):
        prefixes.filter(pk__in=pks).update(_classification=classification)
        batch = pending.filter(pk__gt=pks[-1])


class Migration(migrations.Migration):
    # Kept apart from 0098, so that its ALTER TABLE lock is released before the backfill runs
    atomic = False

    dependencies = [
        ('ipam', '0098_prefix_classification'),
    ]

    operations = [
        migrations.RunPython(code=populate_prefix_classification, reverse_code=migrations.RunPython.noop),
    ]
