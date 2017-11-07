from __future__ import unicode_literals

from Crypto.PublicKey import RSA
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from secrets.hashers import SecretValidationHasher
from secrets.models import UserKey, Secret, encrypt_master_key, decrypt_master_key, generate_random_key


class UserKeyTestCase(TestCase):

    def setUp(self):
        self.TEST_KEYS = {}
        key_size = getattr(settings, 'SECRETS_MIN_PUBKEY_SIZE', 2048)
        for username in ['alice', 'bob']:
            User.objects.create_user(username=username, password=username)
            key = RSA.generate(key_size)
            self.TEST_KEYS['{}_public'.format(username)] = key.publickey().exportKey('PEM')
            self.TEST_KEYS['{}_private'.format(username)] = key.exportKey('PEM')

    def test_01_fill(self):
        """
        Validate the filling of a UserKey with public key material.
        """
        alice_uk = UserKey(user=User.objects.get(username='alice'))
        self.assertFalse(alice_uk.is_filled(), "UserKey with empty public_key is_filled() did not return False")
        alice_uk.public_key = self.TEST_KEYS['alice_public']
        self.assertTrue(alice_uk.is_filled(), "UserKey with public key is_filled() did not return True")

    def test_02_activate(self):
        """
        Validate the activation of a UserKey.
        """
        master_key = generate_random_key()
        alice_uk = UserKey(user=User.objects.get(username='alice'), public_key=self.TEST_KEYS['alice_public'])
        self.assertFalse(alice_uk.is_active(), "Inactive UserKey is_active() did not return False")
        alice_uk.activate(master_key)
        self.assertTrue(alice_uk.is_active(), "ActiveUserKey is_active() did not return True")

    def test_03_key_sizes(self):
        """
        Ensure that RSA keys which are too small or too large are rejected.
        """
        rsa = RSA.generate(getattr(settings, 'SECRETS_MIN_PUBKEY_SIZE', 2048) - 256)
        small_key = rsa.publickey().exportKey('PEM')
        try:
            UserKey(public_key=small_key).clean()
            self.fail("UserKey.clean() did not fail with an undersized RSA key")
        except ValidationError:
            pass
        rsa = RSA.generate(4096 + 256)  # Max size is 4096 (enforced by master_key_cipher field size)
        big_key = rsa.publickey().exportKey('PEM')
        try:
            UserKey(public_key=big_key).clean()
            self.fail("UserKey.clean() did not fail with an oversized RSA key")
        except ValidationError:
            pass

    def test_04_master_key_retrieval(self):
        """
        Test the decryption of a master key using the user's private key.
        """
        master_key = generate_random_key()
        alice_uk = UserKey(user=User.objects.get(username='alice'), public_key=self.TEST_KEYS['alice_public'])
        alice_uk.activate(master_key)
        retrieved_master_key = alice_uk.get_master_key(self.TEST_KEYS['alice_private'])
        self.assertEqual(master_key, retrieved_master_key, "Master key retrieval failed with correct private key")

    def test_05_invalid_private_key(self):
        """
        Ensure that an exception is raised when attempting to retrieve a secret key using an invalid private key.
        """
        secret_key = generate_random_key()
        secret_key_cipher = encrypt_master_key(secret_key, self.TEST_KEYS['alice_public'])
        try:
            decrypted_secret_key = decrypt_master_key(secret_key_cipher, self.TEST_KEYS['bob_private'])
            self.fail("Decrypting secret key from Alice's UserKey using Bob's private key did not fail")
        except ValueError:
            pass


class SecretTestCase(TestCase):

    def test_01_encrypt_decrypt(self):
        """
        Test basic encryption and decryption functionality using a random master key.
        """
        plaintext = "FooBar123"
        secret_key = generate_random_key()
        s = Secret(plaintext=plaintext)
        s.encrypt(secret_key)

        # Ensure plaintext is deleted upon encryption
        self.assertIsNone(s.plaintext, "Plaintext must be None after encrypting.")

        # Enforce minimum ciphertext length
        self.assertGreaterEqual(len(s.ciphertext), 80, "Ciphertext must be at least 80 bytes (16B IV + 64B+ ciphertext")

        # Ensure proper hashing algorithm is used
        hasher, iterations, salt, sha256 = s.hash.split('$')
        self.assertEqual(hasher, 'pbkdf2_sha256', "Hashing algorithm has been modified to: {}".format(hasher))
        self.assertGreaterEqual(int(iterations), SecretValidationHasher.iterations, "Insufficient iteration count ({}) for hash".format(iterations))
        self.assertGreaterEqual(len(salt), 12, "Hash salt is too short ({} chars)".format(len(salt)))

        # Test hash validation
        self.assertTrue(s.validate(plaintext), "Plaintext does not validate against the generated hash")
        self.assertFalse(s.validate(""), "Empty plaintext validated against hash")
        self.assertFalse(s.validate("Invalid plaintext"), "Invalid plaintext validated against hash")

        # Test decryption
        s.decrypt(secret_key)
        self.assertEqual(plaintext, s.plaintext, "Decrypting Secret returned incorrect plaintext")

    def test_02_ciphertext_uniqueness(self):
        """
        Generate 50 Secrets using the same plaintext and check for duplicate IVs or payloads.
        """
        plaintext = "1234567890abcdef"
        secret_key = generate_random_key()
        ivs = []
        ciphertexts = []
        for i in range(1, 51):
            s = Secret(plaintext=plaintext)
            s.encrypt(secret_key)
            ivs.append(s.ciphertext[0:16])
            ciphertexts.append(s.ciphertext[16:32])
        duplicate_ivs = [i for i, x in enumerate(ivs) if ivs.count(x) > 1]
        self.assertEqual(duplicate_ivs, [], "One or more duplicate IVs found!")
        duplicate_ciphertexts = [i for i, x in enumerate(ciphertexts) if ciphertexts.count(x) > 1]
        self.assertEqual(duplicate_ciphertexts, [], "One or more duplicate ciphertexts (first blocks) found!")
