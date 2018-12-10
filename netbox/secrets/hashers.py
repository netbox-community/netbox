from django.contrib.auth.hashers import PBKDF2PasswordHasher


class SecretValidationHasher(PBKDF2PasswordHasher):
    """
    We're using Django's stock SHA256 hasher with a low iteration count to avoid introducing excessive delay when
    retrieving a large number of Secrets (the plaintext of each Secret is validated against its hash upon decryption).
    """
    iterations = 1000
