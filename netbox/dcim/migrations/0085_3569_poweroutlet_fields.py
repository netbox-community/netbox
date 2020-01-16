from django.db import migrations, models


POWEROUTLET_FEED_LEG_CHOICES_CHOICES = (
    (1, 'A'),
    (2, 'B'),
    (3, 'C'),
)


def poweroutlettemplate_feed_leg_to_slug(apps, schema_editor):
    PowerOutletTemplate = apps.get_model('dcim', 'PowerOutletTemplate')
    for id, slug in POWEROUTLET_FEED_LEG_CHOICES_CHOICES:
        PowerOutletTemplate.objects.filter(feed_leg=id).update(feed_leg=slug)


def poweroutlet_feed_leg_to_slug(apps, schema_editor):
    PowerOutlet = apps.get_model('dcim', 'PowerOutlet')
    for id, slug in POWEROUTLET_FEED_LEG_CHOICES_CHOICES:
        PowerOutlet.objects.filter(feed_leg=id).update(feed_leg=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0084_3569_powerfeed_fields'),
    ]

    operations = [

        # PowerOutletTemplate.feed_leg
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='feed_leg',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=poweroutlettemplate_feed_leg_to_slug
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='feed_leg',
            field=models.CharField(blank=True, max_length=50),
        ),

        # PowerOutlet.feed_leg
        migrations.AlterField(
            model_name='poweroutlet',
            name='feed_leg',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=poweroutlet_feed_leg_to_slug
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='feed_leg',
            field=models.CharField(blank=True, max_length=50),
        ),

    ]
