#!/usr/bin/env python3
# This script will generate a random 50-character string suitable for use as a SECRET_KEY.
import secrets

charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)'
print(''.join(secrets.choice(charset) for _ in range(50)))
