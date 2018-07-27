# Secrets

A secret represents a single credential or other sensitive string of characters which must be stored securely. Each secret is assigned to a device within NetBox. The plaintext value of a secret is encrypted to a ciphertext immediately prior to storage within the database using a 256-bit AES master key. A SHA256 hash of the plaintext is also stored along with each ciphertext to validate the decrypted plaintext.

Each secret can also store an optional name parameter, which is not encrypted. This may be useful for storing user names.

## Roles

Each secret is assigned a functional role which indicates what it is used for. Secret roles are customizable. Typical roles might include:

* Login credentials
* SNMP community strings
* RADIUS/TACACS+ keys
* IKE key strings
* Routing protocol shared secrets

Roles are also used to control access to secrets. Each role is assigned an arbitrary number of groups and/or users. Only the users associated with a role have permission to decrypt the secrets assigned to that role. (A superuser has permission to decrypt all secrets, provided they have an active user key.)

---

# User Keys

Each user within NetBox can associate his or her account with an RSA public key. If activated by an administrator, this user key will contain a unique, encrypted copy of the AES master key needed to retrieve secret data.

User keys may be created by users individually, however they are of no use until they have been activated by a user who already possesses an active user key.

## Creating the First User Key

When NetBox is first installed, it contains no encryption keys. Before it can store secrets, a user (typically the superuser) must create a user key. This can be done by navigating to Profile > User Key.

To create a user key, you can either generate a new RSA key pair, or upload the public key belonging to a pair you already have. If generating a new key pair, **you must save the private key** locally before saving your new user key. Once your user key has been created, its public key will be displayed under your profile.

When the first user key is created in NetBox, a random master encryption key is generated automatically. This key is then encrypted using the public key provided and stored as part of your user key. **The master key cannot be recovered** without your private key.

Once a user key has been assigned an encrypted copy of the master key, it is considered activated and can now be used to encrypt and decrypt secrets.

## Creating Additional User Keys

Any user can create his or her user key by generating or uploading a public RSA key. However, a user key cannot be used to encrypt or decrypt secrets until it has been activated with an encrypted copy of the master key.

Only an administrator with an active user key can activate other user keys. To do so, access the NetBox admin UI and navigate to Secrets > User Keys. Select the user key(s) to be activated, and select "activate selected user keys" from the actions dropdown. You will need to provide your private key in order to decrypt the master key. A copy of the master key is then encrypted using the public key associated with the user key being activated.
