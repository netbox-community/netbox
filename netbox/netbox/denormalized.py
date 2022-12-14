import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from netbox.registry import registry


logger = logging.getLogger('netbox.denormalized')


def register(model, field_name, mappings):
    """
    Register a denormalized model field to ensure that it is kept up-to-date with the related object.

    Args:
        model: The class being updated
        field_name: The name of the field related to the triggering instance
        mappings: Dictionary mapping of local to remote fields
    """
    logger.debug(f'Registering denormalized field {model}.{field_name}')

    field = model._meta.get_field(field_name)
    rel_model = field.related_model

    registry['denormalized_fields'][rel_model].append(
        (model, field_name, mappings)
    )


@receiver(post_save)
def update_denormalized_fields(sender, instance, created, raw, **kwargs):
    """
    Check if the sender has denormalized fields registered, and update them as necessary.
    """
    def _get_field_value(instance, field_name):
        field = instance._meta.get_field(field_name)
        return field.value_from_object(instance)

    # Skip for new objects or those being populated from raw data
    if created or raw:
        return

    # Look up any denormalized fields referencing this model from the application registry
    for model, field_name, mappings in registry['denormalized_fields'].get(sender, []):
        logger.debug(f'Updating denormalized values for {model}.{field_name}')
        filter_params = {
            field_name: instance.pk,
        }
        update_params = {
            # Map the denormalized field names to the instance's values
            denorm: _get_field_value(instance, origin) for denorm, origin in mappings.items()
        }

        # TODO: Improve efficiency here by placing conditions on the query?
        # Update all the denormalized fields with the triggering object's new values
        count = model.objects.filter(**filter_params).update(**update_params)
        logger.debug(f'Updated {count} rows')
