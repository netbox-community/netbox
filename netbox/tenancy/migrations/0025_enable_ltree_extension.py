from django.contrib.postgres.operations import CreateExtension
from django.db import migrations


class Migration(migrations.Migration):
    """
    Enable the PostgreSQL ltree extension. Idempotent across apps; only one
    CreateExtension('ltree') needs to succeed during a single migrate run.
    """

    dependencies = [
        ('tenancy', '0024_default_ordering_indexes'),
    ]

    operations = [
        CreateExtension('ltree'),
    ]
