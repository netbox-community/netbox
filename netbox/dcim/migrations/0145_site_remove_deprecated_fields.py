import os

from django.db import migrations
from django.db.utils import DataError


def check_legacy_data(apps, schema_editor):
    """
    Abort the migration if any legacy site fields still contain data.
    """
    Site = apps.get_model('dcim', 'Site')

    site_count = Site.objects.exclude(asn__isnull=True).count()
    if site_count and 'NETBOX_DELETE_LEGACY_DATA' not in os.environ:
        raise DataError(
            f"Unable to proceed with deleting asn field from Site model: Found {site_count} sites with "
            f"legacy ASN data. Please ensure all legacy site ASN data has been migrated to ASN objects "
            f"before proceeding. Or, set the NETBOX_DELETE_LEGACY_DATA environment variable to bypass "
            f"this safeguard and delete all legacy site ASN data."
        )

    site_count = Site.objects.exclude(contact_name='', contact_phone='', contact_email='').count()
    if site_count and 'NETBOX_DELETE_LEGACY_DATA' not in os.environ:
        raise DataError(
            f"Unable to proceed with deleting contact fields from Site model: Found {site_count} sites "
            f"with legacy contact data. Please ensure all legacy site contact data has been migrated to "
            f"contact objects before proceeding. Or, set the NETBOX_DELETE_LEGACY_DATA environment "
            f"variable to bypass this safeguard and delete all legacy site contact data."
        )


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0144_fix_cable_abs_length'),
    ]

    operations = [
        migrations.RunPython(
            code=check_legacy_data,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name='site',
            name='asn',
        ),
        migrations.RemoveField(
            model_name='site',
            name='contact_email',
        ),
        migrations.RemoveField(
            model_name='site',
            name='contact_name',
        ),
        migrations.RemoveField(
            model_name='site',
            name='contact_phone',
        ),
    ]
