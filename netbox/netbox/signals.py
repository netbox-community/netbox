from django.dispatch import Signal


# Signals that a model has completed its clean() method
post_clean = Signal()

# Signals that a model form has completed its clean() method
post_form_clean = Signal()

# Signals that a model serializer has completed its validate() method
post_serializer_clean = Signal()
