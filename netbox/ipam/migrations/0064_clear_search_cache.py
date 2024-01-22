from django.db import migrations


def clear_cache(apps, schema_editor):
    """
    Clear existing CachedValues referencing IPAddressFields or IPNetworkFields. (#11658
    introduced new cache record types for these.)
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    CachedValue = apps.get_model('extras', 'CachedValue')

    for model_name in ('Aggregate', 'IPAddress', 'IPRange', 'Prefix'):
        try:
            content_type = ContentType.objects.get(app_label='ipam', model=model_name.lower())
            CachedValue.objects.filter(object_type=content_type).delete()
        except ContentType.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0063_standardize_description_comments'),
    ]

    operations = [
        migrations.RunPython(
            code=clear_cache,
            reverse_code=migrations.RunPython.noop
        ),
    ]
