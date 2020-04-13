# TODO: Rename the secrets app, probably
# Python 3.6 introduced a standard library named "secrets," which obviously conflicts with this Django app. To avoid
# renaming the app, we hotwire the components of the standard library that Django calls. (I don't like this any more
# than you do, but it works for now.) The only references to the secrets modules are in django/utils/crypto.py.
#
# First, we copy secrets.compare_digest, which comes from the hmac module:
from hmac import compare_digest

# Then, we instantiate SystemRandom and map its choice() function:
from random import SystemRandom
choice = SystemRandom().choice
