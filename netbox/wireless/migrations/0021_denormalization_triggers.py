"""
Maintain WirelessLAN's denormalized scope columns (CachedScopeMixin: _site/_location/_region/
_site_group) via PostgreSQL triggers instead of the Python `dcim.signals.sync_cached_scope_fields`
handler.
"""
from django.db import migrations

from utilities.migration import cached_scope_triggers


class Migration(migrations.Migration):

    dependencies = [
        ('wireless', '0020_ltree_paths'),
        # Source tables (dcim_site, dcim_location) must already exist.
        ('dcim', '0238_ltree_paths'),
    ]

    operations = cached_scope_triggers('wireless_wirelesslan')
