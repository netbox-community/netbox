import json

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import connection
from django.test import Client, TestCase, TransactionTestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APIClient

from core.choices import ObjectChangeActionChoices
from core.models import ObjectChange
from dcim.choices import CableProfileChoices, InterfaceTypeChoices
from dcim.filtersets import InterfaceFilterSet
from dcim.models import (
    Cable,
    CablePath,
    Device,
    DeviceRole,
    DeviceType,
    Interface,
    InterfaceTemplate,
    Manufacturer,
    Site,
)
from dcim.svg import CableTraceSVG
from dcim.svg.cables import Connector
from dcim.tests.utils import BaseCablePathTestCase
from users.constants import TOKEN_PREFIX
from users.models import Token, User
from utilities.ordering import naturalize_interface
from utilities.testing import TestCase as ViewTestCase


class ChannelizedCablePathTestCase(BaseCablePathTestCase):
    """
    Test cable path tracing for channelized interfaces. A single physical cable terminates to a channelized (parent)
    interface, and each of the parent's channel subinterfaces traces an independent path from the connector position
    identified by its channel_id.
    """

    def _create_channelized_interface(self, name, channels, device=None):
        """Create a channelized parent interface and its channel subinterfaces."""
        device = device or self.device
        parent = Interface.objects.create(
            device=device, name=name, type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS, channels=channels
        )
        children = [
            Interface.objects.create(
                device=device,
                name=f'{name}:{i}',
                type=InterfaceTypeChoices.TYPE_CHANNEL,
                parent=parent,
                channel_id=i,
            )
            for i in range(1, channels + 1)
        ]
        return parent, children

    def test_101_channelized_breakout_to_discrete_interfaces(self):
        """
        A 4-channel parent broken out to four discrete far-end interfaces via a 1C4P:4C1P breakout cable. Each channel
        subinterface traces to its corresponding far-end interface (and vice versa); the parent itself has no path.
        """
        parent, channels = self._create_channelized_interface('et0', 4)
        far = [
            Interface.objects.create(device=self.device, name=f'xe{i}', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS)
            for i in range(4)
        ]

        cable = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[parent],
            b_terminations=far,
        )
        cable.clean()
        cable.save()

        # One forward and one reverse path per channel; the parent originates no path
        self.assertEqual(CablePath.objects.count(), 8)
        parent.refresh_from_db()
        self.assertPathIsNotSet(parent)

        for i, (channel, far_iface) in enumerate(zip(channels, far), start=1):
            channel.refresh_from_db()
            far_iface.refresh_from_db()

            # The parent's cable is mirrored onto the channel, restricted to its single connector position
            self.assertEqual(channel.cable_id, cable.pk)
            self.assertEqual(channel.cable_connector, 1)
            self.assertEqual(channel.cable_positions, [i])

            forward = self.assertPathExists((channel, cable, far_iface), is_complete=True, is_active=True)
            reverse = self.assertPathExists((far_iface, cable, channel), is_complete=True, is_active=True)
            self.assertPathIsSet(channel, forward)
            self.assertPathIsSet(far_iface, reverse)

        # The trace SVG must render from both a channel subinterface and a discrete far-end interface
        CableTraceSVG(channels[0]).render()
        CableTraceSVG(far[0]).render()

    def test_102_channelized_to_channelized(self):
        """
        Two channelized interfaces connected by a single 1C4P cable (both ends channelized on one connector). Each
        near-end channel traces to the far-end channel bound to the same position.
        """
        near_parent, near_channels = self._create_channelized_interface('et0', 4)
        far_device = Device.objects.create(
            site=self.site, device_type=self.device.device_type, role=self.device.role, name='Device 2'
        )
        far_parent, far_channels = self._create_channelized_interface('et0', 4, device=far_device)

        cable = Cable(
            profile=CableProfileChoices.SINGLE_1C4P,
            a_terminations=[near_parent],
            b_terminations=[far_parent],
        )
        cable.clean()
        cable.save()

        self.assertEqual(CablePath.objects.count(), 8)
        for near, far in zip(near_channels, far_channels):
            near.refresh_from_db()
            far.refresh_from_db()
            self.assertPathExists((near, cable, far), is_complete=True, is_active=True)
            self.assertPathExists((far, cable, near), is_complete=True, is_active=True)

        # The trace SVG for a channel subinterface must render, drawing the cable between the two channels. The cable
        # terminates on the parent interfaces, so the connector is matched to the channels via their parents.
        svg = CableTraceSVG(near_channels[0])
        svg.render()
        self.assertTrue(
            any(isinstance(c, Connector) for c in svg.connectors),
            msg="Trace SVG did not render a cable connector for the channelized path"
        )

    def test_103_add_channel_after_cabling(self):
        """
        On an already-cabled parent, deleting a channel subinterface tears down its path, and adding a channel
        subinterface (re-adding one on the freed position) builds a fresh path for it in both directions.
        """
        parent, channels = self._create_channelized_interface('et0', 4)
        far = [
            Interface.objects.create(device=self.device, name=f'xe{i}', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS)
            for i in range(4)
        ]
        cable = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[parent],
            b_terminations=far,
        )
        cable.clean()
        cable.save()

        # Removing the fourth channel tears down its complete path in both directions
        channels[3].delete()
        self.assertPathDoesNotExist((channels[3], cable, far[3]))
        self.assertPathDoesNotExist((far[3], cable, channels[3]))

        # Re-adding a channel on position 4 restores the complete path in both directions
        new_channel = Interface.objects.create(
            device=self.device, name='et0:4', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=parent, channel_id=4
        )
        new_channel.refresh_from_db()
        self.assertEqual(new_channel.cable_positions, [4])
        self.assertPathExists((new_channel, cable, far[3]), is_complete=True, is_active=True)
        self.assertPathExists((far[3], cable, new_channel), is_complete=True, is_active=True)

    def test_104_change_channel_id(self):
        """
        Changing a channel's channel_id re-binds it to a different connector position, in both directions.
        """
        parent, channels = self._create_channelized_interface('et0', 4)
        far = [
            Interface.objects.create(device=self.device, name=f'xe{i}', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS)
            for i in range(4)
        ]
        # Delete channels 3 and 4 so their positions are free to reassign to
        channels[2].delete()
        channels[3].delete()
        cable = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[parent],
            b_terminations=far,
        )
        cable.clean()
        cable.save()

        # Channel 1 initially traces to far[0]
        self.assertPathExists((channels[0], cable, far[0]), is_complete=True, is_active=True)

        # Move channel 1 to position 3
        channels[0].channel_id = 3
        channels[0].save()
        channels[0].refresh_from_db()

        self.assertEqual(channels[0].cable_positions, [3])
        self.assertPathDoesNotExist((channels[0], cable, far[0]))
        self.assertPathExists((channels[0], cable, far[2]), is_complete=True, is_active=True)
        self.assertPathExists((far[2], cable, channels[0]), is_complete=True, is_active=True)

    def test_105_incomplete_channel(self):
        """
        A channel whose position has no far-end termination yields an incomplete path (rather than an error).
        """
        parent, channels = self._create_channelized_interface('et0', 4)
        # Only two far-end interfaces exist, on connectors 1 and 2
        far = [
            Interface.objects.create(device=self.device, name=f'xe{i}', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS)
            for i in range(2)
        ]
        cable = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[parent],
            b_terminations=far,
        )
        cable.clean()
        cable.save()

        # Channels 1 & 2 are complete; channels 3 & 4 have no far-end termination and trace an incomplete path
        channels[0].refresh_from_db()
        channels[2].refresh_from_db()
        self.assertPathExists((channels[0], cable, far[0]), is_complete=True)
        self.assertIsNotNone(channels[2]._path_id)
        self.assertFalse(channels[2].path.is_complete)

    def test_106_cable_removal_teardown(self):
        """
        Removing the cable from a channelized parent tears down every channel's path and clears the mirrored cable
        attributes from the channels.
        """
        parent, channels = self._create_channelized_interface('et0', 4)
        far = [
            Interface.objects.create(device=self.device, name=f'xe{i}', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS)
            for i in range(4)
        ]
        cable = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[parent],
            b_terminations=far,
        )
        cable.clean()
        cable.save()
        self.assertEqual(CablePath.objects.count(), 8)

        cable.delete()

        self.assertEqual(CablePath.objects.count(), 0)
        for channel in channels:
            channel.refresh_from_db()
            self.assertIsNone(channel.cable_id)
            self.assertIsNone(channel.cable_connector)
            self.assertIsNone(channel.cable_positions)
            self.assertPathIsNotSet(channel)

    def test_107_direct_cabling_of_channel_rejected(self):
        """
        A cable cannot be terminated directly to a channel subinterface.
        """
        parent, channels = self._create_channelized_interface('et0', 4)
        far = Interface.objects.create(
            device=self.device, name='xe0', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )
        cable = Cable(a_terminations=[channels[0]], b_terminations=[far])
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_108_unprofiled_cable_not_propagated(self):
        """
        An unprofiled cable carries no per-channel positions, so its attributes are not mirrored onto the parent's
        channel subinterfaces.
        """
        parent, channels = self._create_channelized_interface('et0', 4)
        far = Interface.objects.create(
            device=self.device, name='xe0', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )
        cable = Cable(a_terminations=[parent], b_terminations=[far])
        cable.clean()
        cable.save()

        # The parent itself is cabled, but no cable attributes are mirrored onto the channels
        parent.refresh_from_db()
        self.assertEqual(parent.cable_id, cable.pk)
        for channel in channels:
            channel.refresh_from_db()
            self.assertIsNone(channel.cable_id)
            self.assertIsNone(channel.cable_positions)

    def test_109_change_channel_count_after_cabling(self):
        """
        Increasing the channel count on an already-cabled parent re-propagates the cable to its existing channel
        subinterfaces and rebuilds their paths (the Cable itself is unchanged, so only the post_save signal fires).
        """
        parent, channels = self._create_channelized_interface('et0', 4)
        far = [
            Interface.objects.create(device=self.device, name=f'xe{i}', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS)
            for i in range(4)
        ]
        cable = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[parent],
            b_terminations=far,
        )
        cable.clean()
        cable.save()
        self.assertEqual(CablePath.objects.count(), 8)

        # Increase the channel count; the existing channels' paths must survive
        parent.refresh_from_db()
        parent.channels = 8
        parent.save()

        self.assertEqual(CablePath.objects.count(), 8)
        for i, (channel, far_iface) in enumerate(zip(channels, far), start=1):
            channel.refresh_from_db()
            self.assertEqual(channel.cable_positions, [i])
            self.assertPathExists((channel, cable, far_iface), is_complete=True, is_active=True)

    def test_110_move_channel_to_uncabled_parent(self):
        """
        Moving a channel subinterface from a cabled parent to a channelized-but-uncabled parent tears down the
        channel's mirrored cable attributes and its (now orphaned) path.
        """
        parent, channels = self._create_channelized_interface('et0', 4)
        far = [
            Interface.objects.create(device=self.device, name=f'xe{i}', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS)
            for i in range(4)
        ]
        cable = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[parent],
            b_terminations=far,
        )
        cable.clean()
        cable.save()

        # A second channelized parent with no cable
        uncabled_parent = Interface.objects.create(
            device=self.device, name='et1', type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS, channels=4
        )

        # Move the first channel to the uncabled parent; its mirrored cable & path must be torn down
        channel = channels[0]
        channel.refresh_from_db()
        self.assertEqual(channel.cable_id, cable.pk)
        channel.parent = uncabled_parent
        channel.save()

        channel.refresh_from_db()
        self.assertIsNone(channel.cable_id)
        self.assertIsNone(channel.cable_connector)
        self.assertIsNone(channel.cable_positions)
        self.assertPathIsNotSet(channel)
        self.assertPathDoesNotExist((channel, cable, far[0]))
        self.assertPathDoesNotExist((far[0], cable, channel))

    def _rename_cabled_channelized_pair(self, device_suffix, channel_count):
        """
        Build a cabled pair of channelized interfaces with the given channel count, rename the near parent, and
        return (query_count, near_channels, far_channels, cable) for the caller to assert against.
        """
        far_device = Device.objects.create(
            site=self.site, device_type=self.device.device_type, role=self.device.role,
            name=f'Device {device_suffix}'
        )
        near_parent, near_channels = self._create_channelized_interface(f'et{device_suffix}', channel_count)
        far_parent, far_channels = self._create_channelized_interface(
            f'et{device_suffix}', channel_count, device=far_device
        )
        profile = {2: CableProfileChoices.SINGLE_1C2P, 8: CableProfileChoices.SINGLE_1C8P}[channel_count]
        cable = Cable(profile=profile, a_terminations=[near_parent], b_terminations=[far_parent])
        cable.clean()
        cable.save()

        near_parent.refresh_from_db()
        with CaptureQueriesContext(connection) as ctx:
            near_parent.name = f'ex{device_suffix}'
            with self.captureOnCommitCallbacks(execute=True):
                near_parent.save()

        return len(ctx.captured_queries), near_channels, far_channels, cable

    def test_111_rename_cabled_parent_preserves_cable_paths_without_quadratic_cost(self):
        """
        Renaming a channelized parent that carries a cable must cascade the channel subinterfaces' names without
        disturbing their mirrored cable attributes or paths, and without re-deriving cable/channel state (a full
        propagate_channel_cables() + rebuild_cable_paths() cycle) once per renamed child — which would make the
        cost of a single rename quadratic in the channel count. Pinned here by comparing the query cost of
        renaming a 2-channel cabled parent against an 8-channel one (4x the channels): per-child work is
        necessarily linear in the channel count, but the quadratic regression this guards against would show up
        as a much steeper increase than the 4x growth in channel count alone.
        """
        queries_2ch, near_channels, far_channels, cable = self._rename_cabled_channelized_pair('A', 2)
        queries_8ch, _, _, _ = self._rename_cabled_channelized_pair('B', 8)

        self.assertLess(
            queries_8ch, queries_2ch * 4,
            "Renaming an 8-channel cabled parent cost disproportionately more than a 2-channel one; check "
            "whether update_channelized_cable_paths is re-running a full cable/path rebuild per renamed child."
        )

        for near, far in zip(near_channels, far_channels):
            near.refresh_from_db()
            self.assertTrue(near.name.startswith('exA:'))
            self.assertEqual(near.cable_id, cable.pk)
            self.assertPathExists((near, cable, far), is_complete=True, is_active=True)
            self.assertPathExists((far, cable, near), is_complete=True, is_active=True)


class ChannelizedInterfaceValidationTestCase(TestCase):
    """
    Test validation of the channels and channel_id fields on Interface.
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device')
        role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        site = Site.objects.create(name='Site', slug='site')
        cls.device = Device.objects.create(site=site, device_type=device_type, role=role, name='Device 1')
        cls.parent = Interface.objects.create(
            device=cls.device, name='et0', type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS, channels=4
        )

    def test_valid_channel_subinterface(self):
        interface = Interface(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )
        interface.full_clean()  # Should not raise

    def test_channel_type_requires_channel_id(self):
        interface = Interface(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent
        )
        with self.assertRaises(ValidationError):
            interface.full_clean()

    def test_channel_id_allowed_on_specific_physical_type(self):
        # A channel subinterface may keep its own specific physical type (e.g. to record the actual transceiver
        # in use) instead of the generic "channel" type.
        interface = Interface(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS,
            parent=self.parent, channel_id=1
        )
        interface.full_clean()  # Should not raise

    def test_channel_id_rejected_on_virtual_type(self):
        interface = Interface(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_VIRTUAL,
            parent=self.parent, channel_id=1
        )
        with self.assertRaises(ValidationError):
            interface.full_clean()

    def test_physical_type_parent_requires_channel_id(self):
        # A physical interface type may not simply be assigned a parent without also being bound to a channel
        interface = Interface(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS, parent=self.parent
        )
        with self.assertRaises(ValidationError):
            interface.full_clean()

    def test_channel_id_rejected_on_lag_type(self):
        interface = Interface(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_LAG, parent=self.parent, channel_id=1
        )
        with self.assertRaises(ValidationError):
            interface.full_clean()

    def test_channel_subinterface_with_physical_type_is_not_wired(self):
        # A channel subinterface derives its cable from its parent and cannot be cabled directly, regardless of
        # whether it uses the generic "channel" type or its own specific physical type.
        interface = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS,
            parent=self.parent, channel_id=1
        )
        self.assertFalse(interface.is_wired)

    def test_channel_subinterface_with_physical_type_is_channel(self):
        # is_channel is identified by channel_id, not by type, so it must agree with is_wired for a channel
        # subinterface that keeps its own specific physical type.
        interface = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS,
            parent=self.parent, channel_id=1
        )
        self.assertTrue(interface.is_channel)

    def test_generic_channel_type_is_channel(self):
        interface = Interface.objects.create(
            device=self.device, name='et0:2', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=2
        )
        self.assertTrue(interface.is_channel)

    def test_non_channel_interface_is_not_channel(self):
        interface = Interface.objects.create(
            device=self.device, name='xe0', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )
        self.assertFalse(interface.is_channel)

    def test_channel_requires_parent(self):
        interface = Interface(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, channel_id=1
        )
        with self.assertRaises(ValidationError):
            interface.full_clean()

    def test_channel_requires_channelized_parent(self):
        plain_parent = Interface.objects.create(
            device=self.device, name='xe0', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )
        interface = Interface(
            device=self.device, name='xe0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=plain_parent, channel_id=1
        )
        with self.assertRaises(ValidationError):
            interface.full_clean()

    def test_channel_id_within_parent_range(self):
        interface = Interface(
            device=self.device, name='et0:5', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=5
        )
        with self.assertRaises(ValidationError):
            interface.full_clean()

    def test_channels_and_channel_id_mutually_exclusive(self):
        interface = Interface(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=1, channels=4
        )
        with self.assertRaises(ValidationError):
            interface.full_clean()

    def test_channels_not_allowed_on_virtual_type(self):
        interface = Interface(
            device=self.device, name='vlan10', type=InterfaceTypeChoices.TYPE_VIRTUAL, channels=4
        )
        with self.assertRaises(ValidationError):
            interface.full_clean()

    def test_reduce_channels_below_bound_child_rejected(self):
        # Bind a channel to the highest channel of the parent, then attempt to reduce the parent's channel count
        Interface.objects.create(
            device=self.device, name='et0:4', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=4
        )
        self.parent.channels = 2
        with self.assertRaises(ValidationError):
            self.parent.full_clean()

    def test_clear_channels_with_bound_child_rejected(self):
        # De-channelizing a parent entirely must be rejected while any channel subinterface is still bound to it
        Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )
        self.parent.channels = None
        with self.assertRaises(ValidationError):
            self.parent.full_clean()

    def test_clear_channels_without_bound_child_allowed(self):
        # De-channelizing is permitted once no channel subinterfaces remain bound to the parent
        self.parent.channels = None
        self.parent.full_clean()  # Should not raise

    def test_parent_channel_id_must_be_unique(self):
        Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )
        duplicate = Interface(
            device=self.device, name='et0:1b', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()


class ChannelizedInterfaceRenameTestCase(TestCase):
    """
    Test that renaming a channelized parent interface updates the names of any channel subinterfaces which follow
    the "<parent name>:<channel ID>" convention.
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device')
        role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        site = Site.objects.create(name='Site', slug='site')
        cls.device = Device.objects.create(site=site, device_type=device_type, role=role, name='Device 1')
        cls.parent = Interface.objects.create(
            device=cls.device, name='et0', type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS, channels=4
        )

    def test_rename_updates_conforming_children(self):
        child = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )

        self.parent.name = 'et1'
        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save()

        child.refresh_from_db()
        self.assertEqual(child.name, 'et1:1')

    def test_rename_leaves_nonconforming_children_untouched(self):
        child = Interface.objects.create(
            device=self.device, name='et0-custom', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent,
            channel_id=1
        )

        self.parent.name = 'et1'
        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save()

        child.refresh_from_db()
        self.assertEqual(child.name, 'et0-custom')

    def test_rename_skips_child_on_collision(self):
        colliding_child = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )
        Interface.objects.create(device=self.device, name='et1:1', type=InterfaceTypeChoices.TYPE_VIRTUAL)

        self.parent.name = 'et1'
        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save()

        colliding_child.refresh_from_db()
        self.assertEqual(colliding_child.name, 'et0:1')

    def test_rename_collision_on_one_child_does_not_block_others(self):
        # Each child is renamed independently: a collision on one must not prevent another, non-colliding
        # subinterface in the same batch from being renamed. (This holds under the current per-child atomic
        # implementation; a single-statement bulk_update() would have aborted the whole batch if a collision
        # were present at execution time rather than being filtered out beforehand — not reachable here without
        # an actual concurrent write, but this pins the currently intended per-child independence regardless.)
        colliding_child = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )
        clear_child = Interface.objects.create(
            device=self.device, name='et0:2', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=2
        )
        Interface.objects.create(device=self.device, name='et1:1', type=InterfaceTypeChoices.TYPE_VIRTUAL)

        self.parent.name = 'et1'
        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save()

        colliding_child.refresh_from_db()
        clear_child.refresh_from_db()
        self.assertEqual(colliding_child.name, 'et0:1')
        self.assertEqual(clear_child.name, 'et1:2')

    def test_rename_cascade_is_deferred_until_transaction_commits(self):
        # The cascade must not run until the enclosing transaction commits, so that a sibling object saved later
        # in the same transaction (e.g. by a bulk view processing several selected objects together) cannot
        # silently undo it by writing back a stale in-memory copy of the child's name.
        child = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )

        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            self.parent.name = 'et1'
            self.parent.save()

            # The rename has not yet propagated: it's deferred until "commit" (i.e. until the captured
            # callbacks below are actually run).
            child.refresh_from_db()
            self.assertEqual(child.name, 'et0:1')

            # Simulate a sibling object's own save() in the same batch, re-asserting the child's stale name -
            # exactly what BulkRenameView does when the same child is also selected in a bulk rename.
            stale_copy = Interface.objects.get(pk=child.pk)
            stale_copy.save()

        # Once the transaction commits (simulated here by running the captured on_commit callbacks), the
        # deferred cascade is the last write: it still renames the child, rather than having been silently
        # overwritten by the sibling's stale save() above.
        for callback in callbacks:
            callback()
        child.refresh_from_db()
        self.assertEqual(child.name, 'et1:1')

    def test_rename_of_non_channelized_interface_is_a_no_op(self):
        plain = Interface.objects.create(
            device=self.device, name='xe0', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )
        plain.name = 'xe1'
        plain.save()  # Should not raise despite having no channel subinterfaces to check

    def test_rename_then_channelize_then_rename_again(self):
        # Renaming while channels is unset, then channelizing, then renaming again must correctly cascade the
        # second rename to any child created in between.
        interface = Interface.objects.create(
            device=self.device, name='zz0', type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS
        )
        interface.name = 'zz1'
        interface.save()  # Not yet channelized: no cascade, but _original_name must become 'zz1'

        interface.channels = 4
        interface.save()
        child = Interface.objects.create(
            device=self.device, name='zz1:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=interface, channel_id=1
        )

        interface.name = 'zz2'
        with self.captureOnCommitCallbacks(execute=True):
            interface.save()

        child.refresh_from_db()
        self.assertEqual(child.name, 'zz2:1')

    def test_original_name_is_set_for_an_instance_built_without_a_name_kwarg(self):
        # An instance constructed without passing name= (so __init__ caches _original_name as None) must still
        # cascade correctly once a name and channels are assigned and it's saved for the first time.
        interface = Interface(device=self.device, type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS)
        interface.name = 'zz0'
        interface.channels = 4
        interface.save()
        child = Interface.objects.create(
            device=self.device, name='zz0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=interface, channel_id=1
        )

        interface.name = 'zz1'
        with self.captureOnCommitCallbacks(execute=True):
            interface.save()

        child.refresh_from_db()
        self.assertEqual(child.name, 'zz1:1')

    def test_save_with_update_fields_excluding_name_does_not_cascade(self):
        # A save() that explicitly excludes 'name' from update_fields does not persist the in-memory name change,
        # so it must not cascade a rename to children, nor treat that unpersisted name as the new baseline.
        child = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )

        self.parent.name = 'et1'
        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save(update_fields=['description'])

        self.parent.refresh_from_db()
        child.refresh_from_db()
        self.assertEqual(self.parent.name, 'et0')  # Not persisted
        self.assertEqual(child.name, 'et0:1')  # Not cascaded

    def test_update_fields_excluding_name_does_not_desync_later_full_rename(self):
        # After a save() that excludes 'name' from update_fields, a later full save() (this time actually
        # persisting the name) must still correctly detect and cascade the rename — proving the partial save
        # did not incorrectly refresh _original_name to the unpersisted in-memory value.
        child = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )

        self.parent.name = 'et1'
        self.parent.save(update_fields=['description'])  # Not persisted; DB name is still 'et0'

        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save()  # Full save: persists 'et1', cascading from the true prior (DB) name 'et0'

        child.refresh_from_db()
        self.assertEqual(child.name, 'et1:1')


class ChannelizedInterfaceRenameSideEffectsTestCase(TransactionTestCase):
    """
    Test that a cascaded channel subinterface rename behaves as a full save() (updating _name and last_updated,
    and recording an ObjectChange), not merely as a raw name update. Exercised via the REST API, using
    TransactionTestCase (rather than TestCase) so that the request's own transaction really commits and its
    on_commit() callback fires inline, as it would in production — under plain TestCase, the whole test body runs
    inside one uncommitted transaction, so the deferred rename would never run without manually forcing it via
    captureOnCommitCallbacks(), which fires only after the request has fully completed and its per-request
    signal machinery (e.g. the changelog's current_request context) has already been torn down.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', is_superuser=True)
        self.token = Token.objects.create(user=self.user)
        self.header = {'HTTP_AUTHORIZATION': f'Bearer {TOKEN_PREFIX}{self.token.key}.{self.token.token}'}
        self.client = APIClient()

        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device')
        role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        site = Site.objects.create(name='Site', slug='site')
        self.device = Device.objects.create(site=site, device_type=device_type, role=role, name='Device 1')
        self.parent = Interface.objects.create(
            device=self.device, name='et0', type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS, channels=4
        )
        self.child = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent,
            channel_id=1
        )

    def _rename_parent(self):
        url = reverse('dcim-api:interface-detail', kwargs={'pk': self.parent.pk})
        response = self.client.patch(url, {'name': 'et1'}, format='json', **self.header)
        self.assertEqual(response.status_code, 200, response.data)

    def test_rename_updates_child_name_ordering_field(self):
        self._rename_parent()

        self.child.refresh_from_db()
        self.assertEqual(self.child.name, 'et1:1')
        self.assertEqual(self.child._name, naturalize_interface('et1:1', max_length=100))

    def test_rename_bumps_child_last_updated(self):
        original_last_updated = self.child.last_updated

        self._rename_parent()

        self.child.refresh_from_db()
        self.assertGreater(self.child.last_updated, original_last_updated)

    def test_rename_records_child_changelog_entry(self):
        self._rename_parent()

        objectchange = ObjectChange.objects.filter(
            action=ObjectChangeActionChoices.ACTION_UPDATE,
            changed_object_type=ContentType.objects.get_for_model(Interface),
            changed_object_id=self.child.pk,
        ).first()
        self.assertIsNotNone(objectchange, "No ObjectChange was recorded for the cascaded child rename")
        self.assertEqual(objectchange.prechange_data['name'], 'et0:1')
        self.assertEqual(objectchange.postchange_data['name'], 'et1:1')


class ChannelizedInterfaceTemplateRenameTestCase(TestCase):
    """
    Test that renaming a channelized parent InterfaceTemplate updates the names of any channel subinterface
    templates which follow the "<parent name>:<channel ID>" convention.
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        cls.device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device', slug='test-device')
        cls.parent = InterfaceTemplate.objects.create(
            device_type=cls.device_type, name='et0', type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS, channels=4
        )

    def test_rename_updates_conforming_children(self):
        child = InterfaceTemplate.objects.create(
            device_type=self.device_type, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=1
        )

        self.parent.name = 'et1'
        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save()

        child.refresh_from_db()
        self.assertEqual(child.name, 'et1:1')

    def test_rename_leaves_nonconforming_children_untouched(self):
        child = InterfaceTemplate.objects.create(
            device_type=self.device_type, name='et0-custom', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=1
        )

        self.parent.name = 'et1'
        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save()

        child.refresh_from_db()
        self.assertEqual(child.name, 'et0-custom')

    def test_rename_skips_child_on_collision(self):
        colliding_child = InterfaceTemplate.objects.create(
            device_type=self.device_type, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=1
        )
        InterfaceTemplate.objects.create(
            device_type=self.device_type, name='et1:1', type=InterfaceTypeChoices.TYPE_VIRTUAL
        )

        self.parent.name = 'et1'
        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save()

        colliding_child.refresh_from_db()
        self.assertEqual(colliding_child.name, 'et0:1')

    def test_rename_does_not_collide_across_device_types(self):
        # A same-named channel subinterface template under a different device type must not block the rename
        other_type = DeviceType.objects.create(
            manufacturer=self.device_type.manufacturer, model='Other Device', slug='other-device'
        )
        InterfaceTemplate.objects.create(
            device_type=other_type, name='et1:1', type=InterfaceTypeChoices.TYPE_VIRTUAL
        )
        child = InterfaceTemplate.objects.create(
            device_type=self.device_type, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=1
        )

        self.parent.name = 'et1'
        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save()

        child.refresh_from_db()
        self.assertEqual(child.name, 'et1:1')

    def test_rename_collision_on_one_child_does_not_block_others(self):
        # Each child template is renamed independently: a collision on one must not prevent another,
        # non-colliding subinterface template in the same batch from being renamed.
        colliding_child = InterfaceTemplate.objects.create(
            device_type=self.device_type, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=1
        )
        clear_child = InterfaceTemplate.objects.create(
            device_type=self.device_type, name='et0:2', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=2
        )
        InterfaceTemplate.objects.create(
            device_type=self.device_type, name='et1:1', type=InterfaceTypeChoices.TYPE_VIRTUAL
        )

        self.parent.name = 'et1'
        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save()

        colliding_child.refresh_from_db()
        clear_child.refresh_from_db()
        self.assertEqual(colliding_child.name, 'et0:1')
        self.assertEqual(clear_child.name, 'et1:2')

    def test_rename_cascade_is_deferred_until_transaction_commits(self):
        # See the identical test on Interface: the cascade must not run until the enclosing transaction commits,
        # so a sibling template saved later in the same transaction cannot silently undo it.
        child = InterfaceTemplate.objects.create(
            device_type=self.device_type, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=1
        )

        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            self.parent.name = 'et1'
            self.parent.save()

            child.refresh_from_db()
            self.assertEqual(child.name, 'et0:1')

            stale_copy = InterfaceTemplate.objects.get(pk=child.pk)
            stale_copy.save()

        for callback in callbacks:
            callback()
        child.refresh_from_db()
        self.assertEqual(child.name, 'et1:1')


class ChannelizedInterfaceKindFilterTestCase(TestCase):
    """
    Test that a channel subinterface is excluded from kind=physical (REST) / kind: PHYSICAL (GraphQL), even when
    it keeps its own specific physical type rather than the generic "channel" type — matching Interface.is_wired,
    since it derives its cable from its channelized parent and cannot be cabled directly.
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device')
        role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        site = Site.objects.create(name='Site', slug='site')
        device = Device.objects.create(site=site, device_type=device_type, role=role, name='Device 1')
        cls.parent = Interface.objects.create(
            device=device, name='et0', type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS, channels=1
        )
        cls.channel = Interface.objects.create(
            device=device, name='et0:1', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS, parent=cls.parent,
            channel_id=1
        )
        cls.plain = Interface.objects.create(
            device=device, name='xe0', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )

    def test_rest_kind_physical_excludes_channel_subinterface(self):
        filterset = InterfaceFilterSet({'kind': 'physical'}, Interface.objects.all())
        results = set(filterset.qs.values_list('pk', flat=True))
        self.assertIn(self.parent.pk, results)
        self.assertIn(self.plain.pk, results)
        self.assertNotIn(self.channel.pk, results)

    def test_graphql_kind_physical_excludes_channel_subinterface(self):
        user = User.objects.create_user(username='testuser', is_superuser=True)
        client = Client()
        client.force_login(user)

        query = '{ interface_list(filters: {kind: KIND_PHYSICAL}) { id } }'
        response = client.post(
            reverse('graphql'), data=json.dumps({'query': query}), content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertNotIn('errors', data)
        result_ids = {int(r['id']) for r in data['data']['interface_list']}
        self.assertIn(self.parent.pk, result_ids)
        self.assertIn(self.plain.pk, result_ids)
        self.assertNotIn(self.channel.pk, result_ids)


class ChannelizedInterfaceTemplateTestCase(TestCase):
    """
    Test that the channels, channel_id, and parent fields are replicated from InterfaceTemplate to the Interfaces
    instantiated for a new Device, and that parent interfaces are populated before their channel subinterfaces.
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        cls.device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device', slug='test-device')
        cls.role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        cls.site = Site.objects.create(name='Site', slug='site')

        # A channelized parent template broken out into four channel subinterface templates bound to it
        parent_template = InterfaceTemplate.objects.create(
            device_type=cls.device_type, name='et0', type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS, channels=4
        )
        for i in range(1, 5):
            InterfaceTemplate.objects.create(
                device_type=cls.device_type,
                name=f'et0:{i}',
                type=InterfaceTypeChoices.TYPE_CHANNEL,
                parent=parent_template,
                channel_id=i,
            )

    def test_channelization_replicated_on_instantiation(self):
        device = Device.objects.create(
            site=self.site, device_type=self.device_type, role=self.role, name='Device 1'
        )

        # The channelized parent carries its channel count
        parent = device.interfaces.get(name='et0')
        self.assertEqual(parent.channels, 4)
        self.assertIsNone(parent.channel_id)

        # Each channel subinterface carries its channel ID and is bound to the instantiated parent interface
        for i in range(1, 5):
            channel = device.interfaces.get(name=f'et0:{i}')
            self.assertEqual(channel.channel_id, i)
            self.assertIsNone(channel.channels)
            self.assertEqual(channel.parent, parent)

    def test_parent_template_validation(self):
        # A parent template must belong to the same device type
        other_type = DeviceType.objects.create(
            manufacturer=self.device_type.manufacturer, model='Other Device', slug='other-device'
        )
        foreign_parent = InterfaceTemplate.objects.get(device_type=self.device_type, name='et0')
        template = InterfaceTemplate(
            device_type=other_type, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=foreign_parent, channel_id=1
        )
        with self.assertRaises(ValidationError):
            template.full_clean()

    def test_template_parent_channel_id_must_be_unique(self):
        parent = InterfaceTemplate.objects.get(device_type=self.device_type, name='et0')
        # Channel 1 already exists on the parent (created in setUpTestData)
        duplicate = InterfaceTemplate(
            device_type=self.device_type, name='et0:1b', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=parent, channel_id=1
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_template_channel_id_within_parent_range(self):
        # A channel_id beyond the parent's channel count is rejected at the template level
        parent = InterfaceTemplate.objects.get(device_type=self.device_type, name='et0')
        template = InterfaceTemplate(
            device_type=self.device_type, name='et0:5', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=parent, channel_id=5
        )
        with self.assertRaises(ValidationError):
            template.full_clean()

    def test_template_channel_requires_channelized_parent(self):
        # A channel template bound to a non-channelized parent template is rejected
        plain_parent = InterfaceTemplate.objects.create(
            device_type=self.device_type, name='xe0', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )
        template = InterfaceTemplate(
            device_type=self.device_type, name='xe0:1', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=plain_parent, channel_id=1
        )
        with self.assertRaises(ValidationError):
            template.full_clean()

    def test_template_channel_id_requires_channel_type(self):
        # A channel_id on a non-channel-type template is rejected
        template = InterfaceTemplate(
            device_type=self.device_type, name='xe1', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS,
            channel_id=1
        )
        with self.assertRaises(ValidationError):
            template.full_clean()

    def test_template_reduce_channels_below_bound_child_rejected(self):
        # Reducing a parent template's channel count below a bound child template's channel_id is rejected (channels
        # 3 & 4 are bound in setUpTestData)
        parent = InterfaceTemplate.objects.get(device_type=self.device_type, name='et0')
        parent.channels = 2
        with self.assertRaises(ValidationError):
            parent.full_clean()

    def test_template_clear_channels_with_bound_child_rejected(self):
        # De-channelizing a parent template entirely is rejected while a channel subinterface template is bound to it
        parent = InterfaceTemplate.objects.get(device_type=self.device_type, name='et0')
        parent.channels = None
        with self.assertRaises(ValidationError):
            parent.full_clean()


class ChannelizedBulkCreateTestCase(ViewTestCase):
    """
    Test channel_id pattern expansion when bulk-creating channel subinterfaces (and interface templates) so that each
    generated object receives a distinct channel_id.
    """

    def setUp(self):
        super().setUp()
        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        self.device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Test Device', slug='test-device'
        )
        role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        site = Site.objects.create(name='Site', slug='site')
        self.device = Device.objects.create(
            site=site, device_type=self.device_type, role=role, name='Device 1'
        )

    def test_bulk_create_channel_subinterfaces(self):
        parent = Interface.objects.create(
            device=self.device, name='et0', type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS, channels=4
        )
        self.add_permissions('dcim.add_interface', 'dcim.view_interface')

        request_data = {
            'device': self.device.pk,
            'name': 'et0:[1-4]',
            'type': InterfaceTypeChoices.TYPE_CHANNEL,
            'parent': parent.pk,
            'channel_id': '[1-4]',
        }
        response = self.client.post(reverse('dcim:interface_add'), request_data)
        self.assertHttpStatus(response, 302)

        # Four channel subinterfaces are created, each bound to a distinct channel on the parent
        channels = Interface.objects.filter(parent=parent).order_by('channel_id')
        self.assertEqual(channels.count(), 4)
        for i, channel in enumerate(channels, start=1):
            self.assertEqual(channel.name, f'et0:{i}')
            self.assertEqual(channel.channel_id, i)

    def test_bulk_create_channel_subinterface_templates(self):
        parent = InterfaceTemplate.objects.create(
            device_type=self.device_type, name='et0', type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS, channels=4
        )
        self.add_permissions('dcim.add_interfacetemplate', 'dcim.view_interfacetemplate')

        request_data = {
            'device_type': self.device_type.pk,
            'name': 'et0:[1-4]',
            'type': InterfaceTypeChoices.TYPE_CHANNEL,
            'parent': parent.pk,
            'channel_id': '[1-4]',
        }
        response = self.client.post(reverse('dcim:interfacetemplate_add'), request_data)
        self.assertHttpStatus(response, 302)

        templates = InterfaceTemplate.objects.filter(parent=parent).order_by('channel_id')
        self.assertEqual(templates.count(), 4)
        for i, template in enumerate(templates, start=1):
            self.assertEqual(template.name, f'et0:{i}')
            self.assertEqual(template.channel_id, i)
