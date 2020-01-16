import os

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def generate_random_key(bits=256):
    """
    Generate a random encryption key. Sizes is given in bits and must be in increments of 32.
    """
    if bits % 32:
        raise Exception("Invalid key size ({}). Key sizes must be in increments of 32 bits.".format(bits))
    return os.urandom(int(bits / 8))


def encrypt_master_key(master_key, public_key):
    """
    Encrypt a secret key with the provided public RSA key.
    """
    key = RSA.importKey(public_key)
    cipher = PKCS1_OAEP.new(key)
    return cipher.encrypt(master_key)


def decrypt_master_key(master_key_cipher, private_key):
    """
    Decrypt a secret key with the provided private RSA key.
    """
    key = RSA.importKey(private_key)
    cipher = PKCS1_OAEP.new(key)
    return cipher.decrypt(master_key_cipher)
