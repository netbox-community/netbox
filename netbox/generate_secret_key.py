#!/usr/bin/env python
# This script will generate a random 50-character string suitable for use as a SECRET_KEY.
import random

charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)'
secure_random = random.SystemRandom()
print(''.join(secure_random.sample(charset, 50)))
