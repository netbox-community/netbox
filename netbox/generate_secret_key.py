#!/usr/bin/env python
# This script will generate a random 50-character string suitable for use as a SECRET_KEY.
import os
import random

charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)'
random.seed = (os.urandom(2048))
print(''.join(random.choice(charset) for c in range(50)))
