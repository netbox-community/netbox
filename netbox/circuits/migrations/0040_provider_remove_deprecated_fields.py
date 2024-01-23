import os

from django.db import migrations
from django.db.utils import DataError


def check_legacy_data(apps, schema_editor):
    """
    Abort the migration if any legacy provider fields still contain data.
    """
    Provider = apps.get_model('circuits', 'Provider')

    provider_count = Provider.objects.exclude(asn__isnull=True).count()
    if provider_count and 'NETBOX_DELETE_LEGACY_DATA' not in os.environ:
        raise DataError(
            f"Unable to proceed with deleting asn field from Provider model: Found {provider_count} "
            f"providers with legacy ASN data. Please ensure all legacy provider ASN data has been "
            f"migrated to ASN objects before proceeding. Or, set the NETBOX_DELETE_LEGACY_DATA "
            f"environment variable to bypass this safeguard and delete all legacy provider ASN data."
        )

    provider_count = Provider.objects.exclude(admin_contact='', noc_contact='', portal_url='').count()
    if provider_count and 'NETBOX_DELETE_LEGACY_DATA' not in os.environ:
        raise DataError(
            f"Unable to proceed with deleting contact fields from Provider model: Found {provider_count} "
            f"providers with legacy contact data. Please ensure all legacy provider contact data has been "
            f"migrated to contact objects before proceeding. Or, set the NETBOX_DELETE_LEGACY_DATA "
            f"environment variable to bypass this safeguard and delete all legacy provider contact data."
        )


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0039_unique_constraints'),
    ]

    operations = [
        migrations.RunPython(
            code=check_legacy_data,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name='provider',
            name='admin_contact',
        ),
        migrations.RemoveField(
            model_name='provider',
            name='asn',
        ),
        migrations.RemoveField(
            model_name='provider',
            name='noc_contact',
        ),
        migrations.RemoveField(
            model_name='provider',
            name='portal_url',
        ),
    ]
