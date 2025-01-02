from django.db.models import Q


# models values for ContentTypes which may be CircuitTermination termination types
CIRCUIT_TERMINATION_TERMINATION_TYPES = (
    'region', 'sitegroup', 'site', 'location', 'providernetwork',
)

CIRCUIT_GROUP_ASSIGNMENT_MEMBER_MODELS = Q(
    app_label='circuits',
    model__in=['circuit', 'virtualcircuit']
)
