#!/usr/bin/env python
# This script will generate a random 50-character string suitable for use as a SECRET_KEY.
import os
import base64

print(base64.urlsafe_b64encode(os.urandom(64))[:50])
