from django.apps import AppConfig
from django.db.models.signals import pre_delete


def _clear_circuit_termination_pointer(sender, **kwargs):
    from .models import CircuitTermination
    from .signals import clear_circuit_termination_pointer

    if sender is CircuitTermination:
        clear_circuit_termination_pointer(**kwargs)


# This module is imported in populate() phase 1, ahead of the models phase which connects
# core.signals.handle_deleted_object. Connecting here records the Circuit pointer clear before the
# termination's own DELETE; branch revert replays newest-first and needs the termination restored
# before the pointer referencing it. (#23134)
pre_delete.connect(_clear_circuit_termination_pointer)


class CircuitsConfig(AppConfig):
    name = "circuits"
    verbose_name = "Circuits"

    def ready(self):
        from netbox.models.features import register_models

        from . import search, signals  # noqa: F401

        # Register models
        register_models(*self.get_models())
