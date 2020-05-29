from django.db.models import OuterRef, Subquery

from utilities.querysets import RestrictedQuerySet


class CircuitQuerySet(RestrictedQuerySet):

    def annotate_sites(self):
        """
        Annotate the A and Z termination site names for ordering.
        """
        from circuits.models import CircuitTermination
        _terminations = CircuitTermination.objects.filter(circuit=OuterRef('pk'))
        return self.annotate(
            a_side=Subquery(_terminations.filter(term_side='A').values('site__name')[:1]),
            z_side=Subquery(_terminations.filter(term_side='Z').values('site__name')[:1]),
        )
