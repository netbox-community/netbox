from django.db import migrations, models


POWERFEED_STATUS_CHOICES = (
    (0, 'offline'),
    (1, 'active'),
    (2, 'planned'),
    (4, 'failed'),
)

POWERFEED_TYPE_CHOICES = (
    (1, 'primary'),
    (2, 'redundant'),
)

POWERFEED_SUPPLY_CHOICES = (
    (1, 'ac'),
    (2, 'dc'),
)

POWERFEED_PHASE_CHOICES = (
    (1, 'single-phase'),
    (3, 'three-phase'),
)


def powerfeed_status_to_slug(apps, schema_editor):
    PowerFeed = apps.get_model('dcim', 'PowerFeed')
    for id, slug in POWERFEED_STATUS_CHOICES:
        PowerFeed.objects.filter(status=id).update(status=slug)


def powerfeed_type_to_slug(apps, schema_editor):
    PowerFeed = apps.get_model('dcim', 'PowerFeed')
    for id, slug in POWERFEED_TYPE_CHOICES:
        PowerFeed.objects.filter(type=id).update(type=slug)


def powerfeed_supply_to_slug(apps, schema_editor):
    PowerFeed = apps.get_model('dcim', 'PowerFeed')
    for id, slug in POWERFEED_SUPPLY_CHOICES:
        PowerFeed.objects.filter(supply=id).update(supply=slug)


def powerfeed_phase_to_slug(apps, schema_editor):
    PowerFeed = apps.get_model('dcim', 'PowerFeed')
    for id, slug in POWERFEED_PHASE_CHOICES:
        PowerFeed.objects.filter(phase=id).update(phase=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0083_3569_cable_fields'),
    ]

    operations = [

        # PowerFeed.status
        migrations.AlterField(
            model_name='powerfeed',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=powerfeed_status_to_slug
        ),

        # PowerFeed.type
        migrations.AlterField(
            model_name='powerfeed',
            name='type',
            field=models.CharField(default='primary', max_length=50),
        ),
        migrations.RunPython(
            code=powerfeed_type_to_slug
        ),

        # PowerFeed.supply
        migrations.AlterField(
            model_name='powerfeed',
            name='supply',
            field=models.CharField(default='ac', max_length=50),
        ),
        migrations.RunPython(
            code=powerfeed_supply_to_slug
        ),

        # PowerFeed.phase
        migrations.AlterField(
            model_name='powerfeed',
            name='phase',
            field=models.CharField(default='single-phase', max_length=50),
        ),
        migrations.RunPython(
            code=powerfeed_phase_to_slug
        ),

    ]
