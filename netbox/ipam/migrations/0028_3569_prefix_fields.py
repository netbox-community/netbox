from django.db import migrations, models


PREFIX_STATUS_CHOICES = (
    (0, 'container'),
    (1, 'active'),
    (2, 'reserved'),
    (3, 'deprecated'),
)


def prefix_status_to_slug(apps, schema_editor):
    Prefix = apps.get_model('ipam', 'Prefix')
    for id, slug in PREFIX_STATUS_CHOICES:
        Prefix.objects.filter(status=str(id)).update(status=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('ipam', '0027_ipaddress_add_dns_name'),
    ]

    operations = [

        # Prefix.status
        migrations.AlterField(
            model_name='prefix',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=prefix_status_to_slug
        ),

    ]
