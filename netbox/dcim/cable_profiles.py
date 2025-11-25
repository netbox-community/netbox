from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from dcim.models import CableTermination


class BaseCableProfile:
    # Maximum number of terminations allowed per side
    a_max_connections = None
    b_max_connections = None

    def clean(self, cable):
        # Enforce maximum connection limits
        if self.a_max_connections and len(cable.a_terminations) > self.a_max_connections:
            raise ValidationError({
                'a_terminations': _(
                    'Maximum A side connections for profile {profile}: {max}'
                ).format(
                    profile=cable.get_profile_display(),
                    max=self.a_max_connections,
                )
            })
        if self.b_max_connections and len(cable.b_terminations) > self.b_max_connections:
            raise ValidationError({
                'b_terminations': _(
                    'Maximum B side connections for profile {profile}: {max}'
                ).format(
                    profile=cable.get_profile_display(),
                    max=self.b_max_connections,
                )
            })

    def get_mapped_position(self, side, position):
        """
        Return the mapped position for a given cable end and position.

        By default, assume all positions are symmetrical.
        """
        return position

    def get_peer_terminations(self, terminations, position_stack):
        local_end = terminations[0].cable_end
        qs = CableTermination.objects.filter(
            cable=terminations[0].cable,
            cable_end=terminations[0].opposite_cable_end
        )

        # TODO: Optimize this to use a single query under any condition
        if position_stack:
            # Attempt to find a peer termination at the same position currently in the stack. Pop the stack only if
            # we find one. Otherwise, return any peer terminations with a null position.
            position = self.get_mapped_position(local_end, position_stack[-1][0])
            if peers := qs.filter(position=position):
                position_stack.pop()
                return peers

        return qs.filter(position=None)


class StraightSingleCableProfile(BaseCableProfile):
    a_max_connections = 1
    b_max_connections = 1


class StraightMultiCableProfile(BaseCableProfile):
    a_max_connections = None
    b_max_connections = None


class Shuffle2x2MPO8CableProfile(BaseCableProfile):
    a_max_connections = 8
    b_max_connections = 8
    _mapping = {
        1: 1,
        2: 2,
        3: 5,
        4: 6,
        5: 3,
        6: 4,
        7: 7,
        8: 8,
    }

    def get_mapped_position(self, side, position):
        return self._mapping.get(position)


class Shuffle4x4MPO8CableProfile(BaseCableProfile):
    a_max_connections = 8
    b_max_connections = 8
    # A side to B side position mapping
    _a_mapping = {
        1: 1,
        2: 3,
        3: 5,
        4: 7,
        5: 2,
        6: 4,
        7: 6,
        8: 8,
    }
    # B side to A side position mapping (reverse of _a_mapping)
    _b_mapping = {v: k for k, v in _a_mapping.items()}

    def get_mapped_position(self, side, position):
        if side.lower() == 'b':
            return self._b_mapping.get(position)
        return self._a_mapping.get(position)
