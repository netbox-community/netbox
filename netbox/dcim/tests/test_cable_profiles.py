from django.test import tag

from dcim.cable_profiles import (
    Breakout1C4Px4C1PCableProfile,
    Single1C1PCableProfile,
    Single1C4PCableProfile,
    Trunk2C2PCableProfile,
    Trunk2C4PShuffleCableProfile,
)
from dcim.choices import CableProfileChoices
from dcim.models import Cable, Interface, RearPort
from dcim.tests.utils import CablePathTestCase


class CableProfileLinkPeerTests(CablePathTestCase):
    """
    Tests for link peer resolution with cable profiles.
    """

    @tag('regression')  # #21917
    def test_trunk_4c1p_link_peers(self):
        """
        Link peers for trunk profile cables should honor connector mappings.
        """
        interfaces = [Interface.objects.create(device=self.device, name=f'Interface {i}') for i in range(1, 5)]
        rear_ports = [
            RearPort.objects.create(device=self.device, name=f'Rear Port {i}', positions=1) for i in range(1, 5)
        ]

        cable = Cable(
            profile=CableProfileChoices.TRUNK_4C1P,
            a_terminations=interfaces,
            b_terminations=rear_ports,
        )
        cable.clean()
        cable.save()

        for interface, rear_port in zip(interfaces, rear_ports):
            interface.refresh_from_db()
            rear_port.refresh_from_db()

            self.assertEqual(interface.link_peers, [rear_port])
            self.assertEqual(rear_port.link_peers, [interface])

    @tag('regression')  # #21917
    def test_breakout_shuffle_link_peers(self):
        """
        Link peers for asymmetric breakout profiles should honor mapped connectors.
        """
        rear_ports = [
            RearPort.objects.create(device=self.device, name=f'Rear Port {i}', positions=4) for i in range(1, 3)
        ]
        interfaces = [Interface.objects.create(device=self.device, name=f'Interface {i}') for i in range(1, 9)]

        cable = Cable(
            profile=CableProfileChoices.BREAKOUT_2C4P_8C1P_SHUFFLE,
            a_terminations=rear_ports,
            b_terminations=interfaces,
        )
        cable.clean()
        cable.save()

        for rear_port in rear_ports:
            rear_port.refresh_from_db()
        for interface in interfaces:
            interface.refresh_from_db()

        self.assertEqual(rear_ports[0].link_peers, [interfaces[0], interfaces[1], interfaces[4], interfaces[5]])
        self.assertEqual(rear_ports[1].link_peers, [interfaces[2], interfaces[3], interfaces[6], interfaces[7]])

        for interface in interfaces[0:2] + interfaces[4:6]:
            self.assertEqual(interface.link_peers, [rear_ports[0]])

        for interface in interfaces[2:4] + interfaces[6:8]:
            self.assertEqual(interface.link_peers, [rear_ports[1]])


class CableProfilePeerTerminationTests(CablePathTestCase):
    """
    Tests for BaseCableProfile.get_peer_termination() and get_peer_terminations().
    Verifies that the batch method produces identical results to calling
    the singular method in a loop.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Shared pool of interfaces — cables are created per-test since they
        # mutate CableTerminations and cached fields on save.
        cls.interfaces = [Interface(device=cls.device, name=f'Interface {i}') for i in range(1, 17)]
        Interface.objects.bulk_create(cls.interfaces)

    def _assert_batch_matches_singular(self, cable_profile, term_position_pairs):
        """
        Helper: assert get_peer_terminations() returns the same results as
        calling get_peer_termination() individually for each pair.
        """
        expected = [cable_profile.get_peer_termination(term, pos) for term, pos in term_position_pairs]
        actual = cable_profile.get_peer_terminations(term_position_pairs)
        self.assertEqual(len(actual), len(expected))
        for i, (exp, act) in enumerate(zip(expected, actual)):
            exp_peer, exp_pos = exp
            act_peer, act_pos = act
            self.assertEqual(
                (type(act_peer), getattr(act_peer, 'pk', None), act_pos),
                (type(exp_peer), getattr(exp_peer, 'pk', None), exp_pos),
                msg=f'Mismatch at index {i}: expected {exp}, got {act}',
            )

    def test_empty_pairs(self):
        """
        get_peer_terminations() with an empty list returns an empty list.
        """
        profile = Single1C1PCableProfile()
        self.assertEqual(profile.get_peer_terminations([]), [])

    def test_single_pair_fast_path(self):
        """
        A single-pair call should use the fast path and produce the same
        result as get_peer_termination().
        """
        cable = Cable(
            profile=CableProfileChoices.SINGLE_1C1P,
            a_terminations=[self.interfaces[0]],
            b_terminations=[self.interfaces[1]],
        )
        cable.clean()
        cable.save()

        self.interfaces[0].refresh_from_db()
        profile = Single1C1PCableProfile()

        self._assert_batch_matches_singular(profile, [(self.interfaces[0], 1)])

    def test_single_connector_multi_position(self):
        """
        Batch resolution on a Single 1C4P profile should return the same
        peers as individual lookups for each position.
        """
        cable = Cable(
            profile=CableProfileChoices.SINGLE_1C4P,
            a_terminations=[self.interfaces[0]],
            b_terminations=[self.interfaces[4]],
        )
        cable.clean()
        cable.save()

        self.interfaces[0].refresh_from_db()
        profile = Single1C4PCableProfile()

        # Query all 4 positions from the A-side termination
        pairs = [(self.interfaces[0], pos) for pos in range(1, 5)]
        self._assert_batch_matches_singular(profile, pairs)

    def test_multi_connector_multi_position(self):
        """
        Batch resolution on a Trunk 2C2P profile across both connectors
        should match individual lookups.
        """
        cable = Cable(
            profile=CableProfileChoices.TRUNK_2C2P,
            a_terminations=[self.interfaces[0], self.interfaces[1]],
            b_terminations=[self.interfaces[2], self.interfaces[3]],
        )
        cable.clean()
        cable.save()

        for iface in self.interfaces[:4]:
            iface.refresh_from_db()
        profile = Trunk2C2PCableProfile()

        # Build pairs for both A-side terminations across their positions
        pairs = []
        for iface in self.interfaces[:2]:
            for pos in iface.cable_positions:
                pairs.append((iface, pos))

        self._assert_batch_matches_singular(profile, pairs)

    def test_shuffle_profile_mapping(self):
        """
        Batch resolution on a shuffle profile should correctly apply the
        non-linear position mapping.
        """
        cable = Cable(
            profile=CableProfileChoices.TRUNK_2C4P_SHUFFLE,
            a_terminations=[self.interfaces[0], self.interfaces[1]],
            b_terminations=[self.interfaces[2], self.interfaces[3]],
        )
        cable.clean()
        cable.save()

        for iface in self.interfaces[:4]:
            iface.refresh_from_db()
        profile = Trunk2C4PShuffleCableProfile()

        pairs = []
        for iface in self.interfaces[:2]:
            for pos in iface.cable_positions:
                pairs.append((iface, pos))

        self._assert_batch_matches_singular(profile, pairs)

    def test_breakout_profile(self):
        """
        Batch resolution on a breakout profile should correctly map A-side
        positions to different B-side connectors.
        """
        cable = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[self.interfaces[8]],
            b_terminations=self.interfaces[9:13],
        )
        cable.clean()
        cable.save()

        self.interfaces[8].refresh_from_db()
        for iface in self.interfaces[9:13]:
            iface.refresh_from_db()
        profile = Breakout1C4Px4C1PCableProfile()

        # Test A→B direction (one connector, 4 positions → 4 connectors)
        a_pairs = [(self.interfaces[8], pos) for pos in self.interfaces[8].cable_positions]
        self._assert_batch_matches_singular(profile, a_pairs)

        # Test B→A direction (4 connectors, 1 position each → one connector)
        b_pairs = [(iface, 1) for iface in self.interfaces[9:13]]
        self._assert_batch_matches_singular(profile, b_pairs)

    def test_multi_position_single_termination(self):
        """
        When a single-connector multi-position profile has only one termination
        per side, all positions should resolve to the same peer object. The batch
        method must return identical results to the singular method for each.
        """
        # Use a multi-position profile but only connect one termination per side.
        # The CableTermination will have positions=[1,2,3,4] but only one object
        # is attached, so querying any position still resolves to that same peer.
        cable = Cable(
            profile=CableProfileChoices.SINGLE_1C4P,
            a_terminations=[self.interfaces[0]],
            b_terminations=[self.interfaces[1]],
        )
        cable.clean()
        cable.save()

        self.interfaces[0].refresh_from_db()
        profile = Single1C4PCableProfile()

        # All 4 positions should resolve to the same B-side termination
        pairs = [(self.interfaces[0], pos) for pos in range(1, 5)]
        self._assert_batch_matches_singular(profile, pairs)

    def test_duplicate_pairs(self):
        """
        Submitting the same (termination, position) pair multiple times should
        return the correct result for each occurrence without errors.
        """
        cable = Cable(
            profile=CableProfileChoices.SINGLE_1C1P,
            a_terminations=[self.interfaces[0]],
            b_terminations=[self.interfaces[1]],
        )
        cable.clean()
        cable.save()

        self.interfaces[0].refresh_from_db()
        profile = Single1C1PCableProfile()

        # The same pair submitted three times
        pairs = [(self.interfaces[0], 1)] * 3
        self._assert_batch_matches_singular(profile, pairs)
