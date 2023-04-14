import hashlib

__all__ = (
    'sha256_hash',
)


def sha256_hash(filepath):
    """
    Return the SHA256 hash of the file at the specified path.
    """
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read())
