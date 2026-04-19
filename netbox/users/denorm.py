"""
Denormalization declarations for users models.
"""
from netbox.denorm import DenormSpec, denorm_registry


# ──────────────────────────────────────────────────────────────────────
# Token — auto-generate token value on creation
# ──────────────────────────────────────────────────────────────────────

def _token_auto_generate(instance):
    if instance.token is None:
        from users.models import Token
        return Token.generate()
    return instance.token


denorm_registry.register(
    'users.token',
    DenormSpec(
        field_name='token',
        compute=_token_auto_generate,
        depends_on=frozenset({'token'}),
        only_on_create=True,
    ),
)
