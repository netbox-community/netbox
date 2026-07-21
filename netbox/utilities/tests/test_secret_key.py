from unittest.mock import patch

from django.test import SimpleTestCase

from utilities.secret_key import SECRET_KEY_CHARSET, SECRET_KEY_LENGTH, generate_secret_key


class GenerateSecretKeyTest(SimpleTestCase):
    def test_generate_secret_key_length(self):
        self.assertEqual(SECRET_KEY_LENGTH, 50)
        self.assertEqual(len(generate_secret_key()), SECRET_KEY_LENGTH)

    def test_generate_secret_key_uses_only_charset_characters(self):
        self.assertTrue(set(generate_secret_key()) <= set(SECRET_KEY_CHARSET))

    def test_generate_secret_key_draws_every_character_via_secrets_choice(self):
        with patch('utilities.secret_key.secrets.choice', side_effect=lambda charset: charset[0]) as choice:
            self.assertEqual(generate_secret_key(), SECRET_KEY_CHARSET[0] * SECRET_KEY_LENGTH)
        self.assertEqual(choice.call_count, SECRET_KEY_LENGTH)
