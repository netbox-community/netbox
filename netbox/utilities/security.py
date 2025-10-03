from django.core.exceptions import ImproperlyConfigured

__all__ = (
    'validate_peppers',
)


def validate_peppers(peppers):
    """
    Validate the given dictionary of cryptographic peppers for type & sufficient length.
    """
    if type(peppers) is not dict:
        raise ImproperlyConfigured("API_TOKEN_PEPPERS must be a dictionary.")
    for key, pepper in peppers.items():
        if type(key) is not int:
            raise ImproperlyConfigured(f"Invalid API_TOKEN_PEPPERS key: {key}. All keys must be integers.")
        if not 0 <= key <= 32767:
            raise ImproperlyConfigured(
                f"Invalid API_TOKEN_PEPPERS key: {key}. Key values must be between 0 and 32767, inclusive."
            )
        if type(pepper) is not str:
            raise ImproperlyConfigured(f"Invalid pepper {key}: Pepper value must be a string.")
        if len(pepper) < 50:
            raise ImproperlyConfigured(f"Invalid pepper {key}: Pepper must be at least 50 characters in length.")
