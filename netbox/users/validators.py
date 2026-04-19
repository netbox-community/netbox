"""
Extracted, composable validators for users models.
Each function is standalone and raises ValidationError on failure.
"""
import zoneinfo

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from netbox.validators import ModelValidator, ValidatorCategory, validator_registry

_fs = frozenset


# ──────────────────────────────────────────────────────────────────────
# User — username uniqueness (case-insensitive)
# ──────────────────────────────────────────────────────────────────────

def validate_user_username_unique(instance):
    model = instance._meta.model
    if model.objects.exclude(pk=instance.pk).filter(username__iexact=instance.username).exists():
        raise ValidationError(_("A user with this username already exists."))


validator_registry.register('users.user',
    ModelValidator(
        name='user_username_unique',
        model_label='users.user',
        fields=_fs({'username'}),
        category=ValidatorCategory.UNIQUENESS,
        validate=validate_user_username_unique,
        queries_db=True,
        description='Username must be unique (case-insensitive)',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Token — pepper config, expiration
# ──────────────────────────────────────────────────────────────────────

def validate_token_v2_peppers(instance):
    from users.choices import TokenVersionChoices
    if instance.version == TokenVersionChoices.V2 and not settings.API_TOKEN_PEPPERS:
        raise ValidationError(_("Unable to save v2 tokens: API_TOKEN_PEPPERS is not defined."))


def validate_token_pepper_id(instance):
    if instance._state.adding:
        if instance.pepper_id is not None and instance.pepper_id not in settings.API_TOKEN_PEPPERS:
            raise ValidationError(_(
                "Invalid pepper ID: {id}. Check configured API_TOKEN_PEPPERS."
            ).format(id=instance.pepper_id))


def validate_token_expiration(instance):
    if instance.pk is None and instance.is_expired:
        current_tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
        now = timezone.now().astimezone(current_tz)
        current_time_str = f'{now.date().isoformat()} {now.time().isoformat(timespec="seconds")}'
        message = _(
            'Expiration time must be in the future. Current server time is {current_time} ({timezone}).'
        ).format(current_time=current_time_str, timezone=current_tz.key)
        raise ValidationError({'expires': message})


validator_registry.register('users.token',
    ModelValidator(
        name='token_v2_peppers',
        model_label='users.token',
        fields=_fs({'version'}),
        category=ValidatorCategory.FIELD,
        validate=validate_token_v2_peppers,
        description='V2 tokens require API_TOKEN_PEPPERS to be configured',
    ),
    ModelValidator(
        name='token_pepper_id',
        model_label='users.token',
        fields=_fs({'pepper_id'}),
        category=ValidatorCategory.FIELD,
        validate=validate_token_pepper_id,
        description='Pepper ID must be valid if specified',
    ),
    ModelValidator(
        name='token_expiration',
        model_label='users.token',
        fields=_fs({'expires'}),
        category=ValidatorCategory.FIELD,
        validate=validate_token_expiration,
        description='New tokens cannot have a past expiration date',
    ),
)
