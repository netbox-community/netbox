from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from dcim.models import CableTermination


class BaseCableProfile:

    def clean(self, cable):
        # Enforce maximum terminations limits
        a_terminations_count = len(cable.a_terminations)
        b_terminations_count = len(cable.b_terminations)
        max_a_terminations = len(self.a_connectors)
        max_b_terminations = len(self.b_connectors)
        if a_terminations_count > max_a_terminations:
            raise ValidationError({
                'a_terminations': _(
                    'A side of cable has {count} terminations but only {max} are permitted for profile {profile}'
                ).format(
                    count=a_terminations_count,
                    profile=cable.get_profile_display(),
                    max=max_a_terminations,
                )
            })
        if b_terminations_count > max_b_terminations:
            raise ValidationError({
                'b_terminations': _(
                    'B side of cable has {count} terminations but only {max} are permitted for profile {profile}'
                ).format(
                    count=b_terminations_count,
                    profile=cable.get_profile_display(),
                    max=max_b_terminations,
                )
            })

    def get_mapped_position(self, side, connector, position):
        """
        Return the mapped far-end connector & position for a given cable end the local connector & position.
        """
        # By default, assume all positions are symmetrical.
        return connector, position

    def get_peer_termination(self, termination, position):
        """
        Given a terminating object, return the peer terminating object (if any) on the opposite end of the cable.
        """
        connector, position = self.get_mapped_position(
            termination.cable_end,
            termination.cable_connector,
            position
        )
        try:
            ct = CableTermination.objects.get(
                cable=termination.cable,
                cable_end=termination.opposite_cable_end,
                connector=connector,
                positions__contains=[position],
            )
            return ct.termination, position
        except CableTermination.DoesNotExist:
            return None, None


class Straight1C1PCableProfile(BaseCableProfile):
    a_connectors = {
        1: [1],
    }
    b_connectors = a_connectors


class Straight1C2PCableProfile(BaseCableProfile):
    a_connectors = {
        1: [1, 2],
    }
    b_connectors = a_connectors


class Straight1C4PCableProfile(BaseCableProfile):
    a_connectors = {
        1: [1, 2, 3, 4],
    }
    b_connectors = a_connectors


class Straight1C8PCableProfile(BaseCableProfile):
    a_connectors = {
        1: [1, 2, 3, 4, 5, 6, 7, 8],
    }
    b_connectors = a_connectors


class Straight2C1PCableProfile(BaseCableProfile):
    a_connectors = {
        1: [1],
        2: [1],
    }
    b_connectors = a_connectors


class Straight2C2PCableProfile(BaseCableProfile):
    a_connectors = {
        1: [1, 2],
        2: [1, 2],
    }
    b_connectors = a_connectors


class Breakout1x4CableProfile(BaseCableProfile):
    a_connectors = {
        1: [1, 2, 3, 4],
    }
    b_connectors = {
        1: [1],
        2: [1],
        3: [1],
        4: [1],
    }
    _mapping = {
        (1, 1): (1, 1),
        (1, 2): (2, 1),
        (1, 3): (3, 1),
        (1, 4): (4, 1),
        (2, 1): (1, 2),
        (3, 1): (1, 3),
        (4, 1): (1, 4),
    }

    def get_mapped_position(self, side, connector, position):
        return self._mapping.get((connector, position))


class MPOTrunk4x4CableProfile(BaseCableProfile):
    a_connectors = {
        1: [1, 2, 3, 4],
        2: [1, 2, 3, 4],
        3: [1, 2, 3, 4],
        4: [1, 2, 3, 4],
    }
    b_connectors = a_connectors


class MPOTrunk8x8CableProfile(BaseCableProfile):
    a_connectors = {
        1: [1, 2, 3, 4],
        2: [1, 2, 3, 4],
        3: [1, 2, 3, 4],
        4: [1, 2, 3, 4],
        5: [1, 2, 3, 4],
        6: [1, 2, 3, 4],
        7: [1, 2, 3, 4],
        8: [1, 2, 3, 4],
    }
    b_connectors = a_connectors


class Shuffle2x2MPO8CableProfile(BaseCableProfile):
    a_connectors = {
        1: [1, 2, 3, 4],
        2: [1, 2, 3, 4],
    }
    b_connectors = a_connectors
    _mapping = {
        (1, 1): (1, 1),
        (1, 2): (1, 2),
        (1, 3): (2, 1),
        (1, 4): (2, 2),
        (2, 1): (1, 3),
        (2, 2): (1, 4),
        (2, 3): (2, 3),
        (2, 4): (2, 4),
    }

    def get_mapped_position(self, side, connector, position):
        return self._mapping.get((connector, position))


class Shuffle4x4MPO8CableProfile(BaseCableProfile):
    a_connectors = {
        1: [1, 2, 3, 4],
        2: [1, 2, 3, 4],
        3: [1, 2, 3, 4],
        4: [1, 2, 3, 4],
    }
    b_connectors = a_connectors
    _mapping = {
        (1, 1): (1, 1),
        (1, 2): (2, 1),
        (1, 3): (3, 1),
        (1, 4): (4, 1),
        (2, 1): (1, 2),
        (2, 2): (2, 2),
        (2, 3): (3, 2),
        (2, 4): (4, 2),
        (3, 1): (1, 3),
        (3, 2): (2, 3),
        (3, 3): (3, 3),
        (3, 4): (4, 3),
        (4, 1): (1, 4),
        (4, 2): (2, 4),
        (4, 3): (3, 4),
        (4, 4): (4, 4),
    }

    def get_mapped_position(self, side, connector, position):
        return self._mapping.get((connector, position))


class ShuffleBreakout2x8CableProfile(BaseCableProfile):
    """
    Temporary solution for mapping 2 front/rear ports to 8 discrete interfaces
    """
    a_connectors = {
        1: [1, 2, 3, 4],
        2: [1, 2, 3, 4],
    }
    b_connectors = {
        1: [1],
        2: [1],
        3: [1],
        4: [1],
        5: [1],
        6: [1],
        7: [1],
        8: [1],
    }
    _a_mapping = {
        (1, 1): (1, 1),
        (1, 2): (2, 1),
        (1, 3): (5, 1),
        (1, 4): (6, 1),
        (2, 1): (3, 2),
        (2, 2): (4, 2),
        (2, 3): (7, 2),
        (2, 4): (8, 2),
    }
    _b_mapping = {
        (1, 1): (1, 1),
        (2, 1): (1, 2),
        (3, 1): (2, 1),
        (4, 1): (2, 2),
        (5, 1): (1, 3),
        (6, 1): (1, 4),
        (7, 1): (2, 3),
        (8, 1): (2, 4),
    }

    def get_mapped_position(self, side, connector, position):
        if side.lower() == 'a':
            return self._a_mapping.get((connector, position))
        return self._b_mapping.get((connector, position))
