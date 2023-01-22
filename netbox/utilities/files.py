import hashlib


def sha256_checksum(filepath):
    # TODO: Write an actual checksum function
    return hashlib.sha256(filepath.encode('utf-8'))
