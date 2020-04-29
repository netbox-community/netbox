from django.db import migrations


def ipaddress_status_dhcp_to_slug(apps, schema_editor):
    IPAddress = apps.get_model('ipam', 'IPAddress')
    IPAddress.objects.filter(status='5').update(status='dhcp')


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0033_deterministic_ordering'),
    ]

    operations = [
        # Fixes a missed integer substitution from #3569; see bug #4027. The original migration has also been fixed.
        migrations.RunPython(
            code=ipaddress_status_dhcp_to_slug
        ),
    ]
