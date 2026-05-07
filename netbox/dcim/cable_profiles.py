from collections import defaultdict, namedtuple

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from dcim.choices import CableEndChoices
from dcim.models import CableTermination

PeerLookupKey = namedtuple('PeerLookupKey', ['cable_id', 'cable_end', 'connector', 'position'])


class BaseCableProfile:
    """Base class for representing a cable profile."""

    # Mappings of connectors to the number of positions presented by each, at either end of the cable. For example, a
    # 12-strand MPO fiber cable would have one connector at either end with six positions (six bidirectional fiber
    # pairs).
    a_connectors = {}
    b_connectors = {}

    # Defined a mapping of A/B connector & position pairings. If not defined, all positions are presumed to be
    # symmetrical (i.e. 1:1 on side A maps to 1:1 on side B). If defined, it must be constructed as a dictionary of
    # two-item tuples, e.g. {(1, 1): (1, 1)}.
    _mapping = None

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
        if self._mapping:
            return self._mapping.get((connector, position))
        return connector, position

    #
    # Peer termination resolution
    #

    def _get_peer_lookup_key(self, termination, position):
        """
        Given a cabled object and a local position, return the (cable_id, cable_end, connector, position)
        tuple identifying the corresponding peer CableTermination on the opposite end of the cable.
        """
        try:
            connector, position = self.get_mapped_position(
                termination.cable_end,
                termination.cable_connector,
                position
            )
        except TypeError:
            raise ValueError(
                f"Could not map connector {termination.cable_connector} position {position} on side "
                f"{termination.cable_end}"
            )
        return PeerLookupKey(termination.cable_id, termination.opposite_cable_end, connector, position)

    def get_peer_termination(self, termination, position):
        """
        Given a terminating object, return the peer terminating object (if any) on the opposite end of the cable.
        """
        cable_id, cable_end, connector, position = self._get_peer_lookup_key(termination, position)
        try:
            ct = CableTermination.objects.get(
                cable_id=cable_id,
                cable_end=cable_end,
                connector=connector,
                positions__contains=[position],
            )
            return ct.termination, position
        except CableTermination.DoesNotExist:
            return None, None

    def get_peer_terminations(self, term_position_pairs):
        """
        Resolve a batch of (termination, position) pairs to peer terminations.
        """
        if not term_position_pairs:
            return []

        # Fast path: a single pair doesn't benefit from batching
        if len(term_position_pairs) == 1:
            return [self.get_peer_termination(*term_position_pairs[0])]

        lookup_keys = [
            self._get_peer_lookup_key(termination, position) for termination, position in term_position_pairs
        ]

        # Group requested positions by (cable_id, cable_end, connector) so we can
        # build one overlap clause per group instead of one clause per position.
        positions_by_group = defaultdict(set)
        for key in lookup_keys:
            positions_by_group[(key.cable_id, key.cable_end, key.connector)].add(key.position)

        q_filter = Q()
        for (cable_id, cable_end, connector), positions in positions_by_group.items():
            q_filter |= Q(
                cable_id=cable_id,
                cable_end=cable_end,
                connector=connector,
                positions__overlap=list(positions),
            )

        peer_ct_by_key = {}
        term_ids_by_type = defaultdict(set)
        model_by_type = {}

        for ct in CableTermination.objects.filter(q_filter).select_related('termination_type'):
            model_by_type[ct.termination_type_id] = ct.termination_type.model_class()
            term_ids_by_type[ct.termination_type_id].add(ct.termination_id)

            group_key = (ct.cable_id, ct.cable_end, ct.connector)
            requested_positions = positions_by_group.get(group_key, ())

            # The overlap query may return a termination carrying additional
            # positions, so only index the positions we actually requested.
            for pos in ct.positions or []:
                if pos not in requested_positions:
                    continue

                key = PeerLookupKey(ct.cable_id, ct.cable_end, ct.connector, pos)
                if key in peer_ct_by_key and peer_ct_by_key[key].pk != ct.pk:
                    raise CableTermination.MultipleObjectsReturned(
                        f"Multiple peer terminations found for cable {ct.cable_id} end {ct.cable_end} "
                        f"connector {ct.connector} position {pos}"
                    )
                peer_ct_by_key[key] = ct

        # Use _base_manager to ensure all termination objects are loaded
        # regardless of any custom default manager filters (e.g. soft-delete).
        # Note: Django's GenericForeignKey / ContentType.get_object_for_this_type()
        # uses _default_manager, but _base_manager is safer for bulk resolution
        # during path tracing.
        term_by_type = {
            type_id: model_by_type[type_id]._base_manager.in_bulk(ids) for type_id, ids in term_ids_by_type.items()
        }

        results = []
        for key in lookup_keys:
            ct = peer_ct_by_key.get(key)
            if ct is None:
                results.append((None, None))
            else:
                termination = term_by_type[ct.termination_type_id].get(ct.termination_id)
                results.append((termination, key.position if termination is not None else None))

        return results

    @staticmethod
    def get_position_list(n):
        """Return a list of integers from 1 to n, inclusive."""
        return list(range(1, n + 1))


# Profile naming:
#  - Single: One connector per side, with one or more positions
#  - Trunk: Two or more connectors per side, with one or more positions per connector
#  - Breakout: One or more connectors on the A side which map to a greater number of B side connectors
#  - Shuffle: A cable with nonlinear position mappings between sides

class Single1C1PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 1,
    }
    b_connectors = a_connectors


class Single1C2PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 2,
    }
    b_connectors = a_connectors


class Single1C4PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 4,
    }
    b_connectors = a_connectors


class Single1C6PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 6,
    }
    b_connectors = a_connectors


class Single1C8PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 8,
    }
    b_connectors = a_connectors


class Single1C12PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 12,
    }
    b_connectors = a_connectors


class Single1C16PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 16,
    }
    b_connectors = a_connectors


class Trunk2C1PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 1,
        2: 1,
    }
    b_connectors = a_connectors


class Trunk2C2PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 2,
        2: 2,
    }
    b_connectors = a_connectors


class Trunk2C4PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 4,
        2: 4,
    }
    b_connectors = a_connectors


class Trunk2C6PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 6,
        2: 6,
    }
    b_connectors = a_connectors


class Trunk2C8PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 8,
        2: 8,
    }
    b_connectors = a_connectors


class Trunk2C12PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 12,
        2: 12,
    }
    b_connectors = a_connectors


class Trunk4C1PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 1,
        2: 1,
        3: 1,
        4: 1,
    }
    b_connectors = a_connectors


class Trunk4C2PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 2,
        2: 2,
        3: 2,
        4: 2,
    }
    b_connectors = a_connectors


class Trunk4C4PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 4,
        2: 4,
        3: 4,
        4: 4,
    }
    b_connectors = a_connectors


class Trunk4C6PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 6,
        2: 6,
        3: 6,
        4: 6,
    }
    b_connectors = a_connectors


class Trunk4C8PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 8,
        2: 8,
        3: 8,
        4: 8,
    }
    b_connectors = a_connectors


class Trunk8C4PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 4,
        2: 4,
        3: 4,
        4: 4,
        5: 4,
        6: 4,
        7: 4,
        8: 4,
    }
    b_connectors = a_connectors


class Breakout1C2Px2C1PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 2,
    }
    b_connectors = {
        1: 1,
        2: 1,
    }
    _mapping = {
        (1, 1): (1, 1),
        (1, 2): (2, 1),
        (2, 1): (1, 2),
    }


class Breakout1C4Px4C1PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 4,
    }
    b_connectors = {
        1: 1,
        2: 1,
        3: 1,
        4: 1,
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


class Breakout1C6Px6C1PCableProfile(BaseCableProfile):
    a_connectors = {
        1: 6,
    }
    b_connectors = {
        1: 1,
        2: 1,
        3: 1,
        4: 1,
        5: 1,
        6: 1,
    }
    _mapping = {
        (1, 1): (1, 1),
        (1, 2): (2, 1),
        (1, 3): (3, 1),
        (1, 4): (4, 1),
        (1, 5): (5, 1),
        (1, 6): (6, 1),
        (2, 1): (1, 2),
        (3, 1): (1, 3),
        (4, 1): (1, 4),
        (5, 1): (1, 5),
        (6, 1): (1, 6),
    }


class Trunk2C4PShuffleCableProfile(BaseCableProfile):
    a_connectors = {
        1: 4,
        2: 4,
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


class Trunk4C4PShuffleCableProfile(BaseCableProfile):
    a_connectors = {
        1: 4,
        2: 4,
        3: 4,
        4: 4,
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


class Breakout2C4Px8C1PShuffleCableProfile(BaseCableProfile):
    a_connectors = {
        1: 4,
        2: 4,
    }
    b_connectors = {
        1: 1,
        2: 1,
        3: 1,
        4: 1,
        5: 1,
        6: 1,
        7: 1,
        8: 1,
    }
    _a_mapping = {
        (1, 1): (1, 1),
        (1, 2): (2, 1),
        (1, 3): (5, 1),
        (1, 4): (6, 1),
        (2, 1): (3, 1),
        (2, 2): (4, 1),
        (2, 3): (7, 1),
        (2, 4): (8, 1),
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
        if side.upper() == CableEndChoices.SIDE_A:
            return self._a_mapping.get((connector, position))
        return self._b_mapping.get((connector, position))
