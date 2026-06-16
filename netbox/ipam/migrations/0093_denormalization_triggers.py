"""
Maintain Prefix's denormalized site/region/site-group columns via PostgreSQL triggers instead of the
Python `post_save` handler formerly registered in netbox.denormalized (and dcim.signals.sync_cached_scope_fields).
"""
from django.db import migrations

from utilities.migration import cached_scope_triggers


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0092_iprange_host_indexes'),
        # Source tables (dcim_site, dcim_location) must already exist.
        ('dcim', '0238_ltree_paths'),
    ]

    operations = cached_scope_triggers('ipam_prefix')
