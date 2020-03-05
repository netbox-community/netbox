# Secrets

A secret represents a single credential or other sensitive string of characters which must be stored securely. Each secret is assigned to a device within NetBox. The plaintext value of a secret is encrypted to a ciphertext immediately prior to storage within the database using a 256-bit AES master key. A SHA256 hash of the plaintext is also stored along with each ciphertext to validate the decrypted plaintext.

Each secret can also store an optional name parameter, which is not encrypted. This may be useful for storing user names.
