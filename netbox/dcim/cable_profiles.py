from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from dcim.models import CableTermination


class BaseCableProfile:
    # Maximum number of terminations allowed per side
    a_max_connections = None
    b_max_connections = None

    # Number of A & B terminations must match
    symmetrical = True

    # Whether terminations on either side of the cable have a numeric position
    a_side_numbered = True
    b_side_numbered = True

    def clean(self, cable):
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
        if self.symmetrical and len(cable.a_terminations) != len(cable.b_terminations):
            raise ValidationError({
                'b_terminations': _(
                    'Number of A and B terminations must be equal for profile {profile}'
                ).format(
                    profile=cable.get_profile_display(),
                )
            })

    def get_mapped_position(self, position):
        return position

    def get_peer_terminations(self, terminations, position_stack):
        local_end = terminations[0].cable_end
        position = None

        # Pop the position stack if necessary
        if (local_end == 'A' and self.b_side_numbered) or (local_end == 'B' and self.a_side_numbered):
            try:
                position = position_stack.pop()[0]
            except IndexError:
                # TODO: Should this raise an error?
                # Bottomed out of stack
                pass

        qs = CableTermination.objects.filter(
            cable=terminations[0].cable,
            cable_end=terminations[0].opposite_cable_end
        )
        if position is not None:
            qs = qs.filter(position=self.get_mapped_position(position))
        return qs


class StraightSingleCableProfile(BaseCableProfile):
    a_max_connections = 1
    b_max_connections = 1


class StraightMultiCableProfile(BaseCableProfile):
    a_max_connections = None
    b_max_connections = None


class AToManyCableProfile(BaseCableProfile):
    a_max_connections = 1
    b_max_connections = None
    symmetrical = False
    a_side_numbered = False


class BToManyCableProfile(BaseCableProfile):
    a_max_connections = None
    b_max_connections = 1
    symmetrical = False
    b_side_numbered = False


class Shuffle2x2MPOCableProfile(BaseCableProfile):
    a_max_connections = 8
    b_max_connections = 8

    def get_mapped_position(self, position):
        return {
            1: 1,
            2: 2,
            3: 5,
            4: 6,
            5: 3,
            6: 4,
            7: 7,
            8: 8,
        }.get(position)
