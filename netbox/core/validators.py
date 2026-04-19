"""
Extracted, composable validators for core models.
Each function is standalone and raises ValidationError on failure.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.validators import ModelValidator, ValidatorCategory, validator_registry

_fs = frozenset


# ──────────────────────────────────────────────────────────────────────
# DataSource
# ──────────────────────────────────────────────────────────────────────

def validate_datasource_backend_type(instance):
    from netbox.registry import registry
    if instance.type and instance.type not in registry['data_backends']:
        raise ValidationError({
            'type': _("Unknown backend type: {type}".format(type=instance.type))
        })


def validate_datasource_url_scheme(instance):
    if instance.backend_class.is_local and instance.url_scheme not in ('file', ''):
        raise ValidationError({
            'source_url': _("URLs for local sources must start with {scheme} (or specify no scheme)").format(
                scheme='file://'
            )
        })


validator_registry.register('core.datasource',
    ModelValidator(
        name='datasource_backend_type',
        model_label='core.datasource',
        fields=_fs({'type'}),
        category=ValidatorCategory.FIELD,
        validate=validate_datasource_backend_type,
        description='Backend type must be registered',
    ),
    ModelValidator(
        name='datasource_url_scheme',
        model_label='core.datasource',
        fields=_fs({'type', 'source_url'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_datasource_url_scheme,
        description='URL scheme must match backend type',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# ManagedFile
# ──────────────────────────────────────────────────────────────────────

def validate_managedfile_unique_path(instance):
    if instance._meta.model.objects.filter(
            file_root=instance.file_root, file_path=instance.file_path
    ).exclude(pk=instance.pk).exists():
        raise ValidationError(
            _("A {model} with this file path already exists ({path}).").format(
                model=instance._meta.verbose_name.lower(),
                path=f"{instance.file_root}/{instance.file_path}"
            ))


validator_registry.register('core.managedfile',
    ModelValidator(
        name='managedfile_unique_path',
        model_label='core.managedfile',
        fields=_fs({'file_root', 'file_path'}),
        category=ValidatorCategory.UNIQUENESS,
        validate=validate_managedfile_unique_path,
        queries_db=True,
        description='File root and path must be unique together',
    ),
)
