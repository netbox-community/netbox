from django.contrib.contenttypes.models import ContentType

__all__ = (
    'delete_import_records',
)


def delete_import_records(sender, instance, using, **kwargs):
    """
    Delete the import record (and by extension its enrichment and provenance) for an object being deleted. Connected
    to the pre_delete signal of each model for which an importer is registered.
    """
    from .models import ImportRecord

    records = ImportRecord.objects.using(using).filter(
        object_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
    )
    # Delete individually so that each deletion is change-logged
    for record in records:
        record.delete(using=using)
