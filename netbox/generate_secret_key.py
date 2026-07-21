#!/usr/bin/env python3
# This script will generate a random 50-character string suitable for use as a SECRET_KEY.
from utilities.secret_key import generate_secret_key

print(generate_secret_key())
