"""
Side-effect declarations for the users app.
"""
from netbox.side_effects import Effect, EffectTiming, EffectType, _fs, effect_registry

effect_registry.register_many(

    # --- Token.save ---
    Effect(
        effect_type=EffectType.OTHER,
        source_model='users.token',
        timing=EffectTiming.PRE_SAVE,
        description='Generates cryptographic token value on create.',
        handler='users.models.tokens.Token.save',
        only_on_create=True,
    ),

    # --- create_userconfig (post_save User) ---
    Effect(
        effect_type=EffectType.ENTITY_INSTANTIATION,
        source_model='users.user',
        target_model='users.userconfig',
        timing=EffectTiming.POST_SAVE,
        description='Creates UserConfig with default preferences for new users.',
        handler='users.signals.create_userconfig',
        only_on_create=True,
    ),
)
