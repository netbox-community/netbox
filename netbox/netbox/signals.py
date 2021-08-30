from django.dispatch import Signal


# Signals that a model has completed its clean() method
post_clean = Signal()
