import json
from unittest import mock

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import connection, router
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
        Renaming a cabled channelized parent must cascade the children's names without disturbing their cable
        paths, and without re-deriving cable state per child (which would make the rename quadratic in the
        channel count). Pinned by comparing query cost at 2 vs. 8 channels: linear per-child work scales with
        the 4x channel growth; a quadratic regression would blow well past it.
        """
        queries_2ch, near_channels_2ch, far_channels_2ch, cable_2ch = self._rename_cabled_channelized_pair('A', 2)
        queries_8ch, near_channels_8ch, far_channels_8ch, cable_8ch = self._rename_cabled_channelized_pair('B', 8)

        self.assertLess(
            queries_8ch, queries_2ch * 4,
            "Renaming an 8-channel cabled parent cost disproportionately more than a 2-channel one; check "
            "whether update_channelized_cable_paths is re-running a full cable/path rebuild per renamed child."
        )

        # Both the 2- and 8-channel cascades must have actually renamed and preserved paths correctly; checking
        # only the query count above would still pass if the larger (8-channel) cascade silently did neither.
        for prefix, near_channels, far_channels, cable in (
            ('exA:', near_channels_2ch, far_channels_2ch, cable_2ch),
            ('exB:', near_channels_8ch, far_channels_8ch, cable_8ch),
        ):
            for near, far in zip(near_channels, far_channels):
                near.refresh_from_db()
                self.assertTrue(near.name.startswith(prefix))
                self.assertEqual(near.cable_id, cable.pk)
                self.assertPathExists((near, cable, far), is_complete=True, is_active=True)
                self.assertPathExists((far, cable, near), is_complete=True, is_active=True)

    def test_112_full_resave_of_unchanged_channel_child_skips_propagation(self):
        """
        A full re-save of an already-channelized child with neither channel_id nor parent actually changed must
        not re-propagate cable state or rebuild the parent's paths; previously only update_fields-excluded
        partial saves were guarded, so a full save of an unrelated field still passed through.
        """
        parent, channels = self._create_channelized_interface('et0', 4)
        far = [
            Interface.objects.create(device=self.device, name=f'xe{i}', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS)
            for i in range(4)
        ]
        cable = Cable(profile=CableProfileChoices.BREAKOUT_1C4P_4C1P, a_terminations=[parent], b_terminations=far)
        cable.clean()
        cable.save()

        channel = channels[0]
        channel.refresh_from_db()
        channel.description = 'updated'
        with (
            mock.patch.object(Interface, 'propagate_channel_cables') as mock_propagate,
            mock.patch('dcim.signals.rebuild_cable_paths') as mock_rebuild,
        ):
            channel.save()

        mock_propagate.assert_not_called()
        mock_rebuild.assert_not_called()

    def test_113_detach_channel_clears_stale_cable_attributes(self):
        """
        Fully detaching a channel subinterface (clearing both parent and channel_id) must clear its mirrored
        cable attributes too -- once detached, it drops out of the old parent's propagation queryset and would
        otherwise retain a stale cable_id indefinitely.
        """
        parent, channels = self._create_channelized_interface('et0', 4)
        far = [
            Interface.objects.create(device=self.device, name=f'xe{i}', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS)
            for i in range(4)
        ]
        cable = Cable(profile=CableProfileChoices.BREAKOUT_1C4P_4C1P, a_terminations=[parent], b_terminations=far)
        cable.clean()
        cable.save()

        channel = channels[0]
        channel.refresh_from_db()
        self.assertEqual(channel.cable_id, cable.pk)

        channel.parent = None
        channel.channel_id = None
        channel.type = InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        channel.full_clean()
        channel.save()

        channel.refresh_from_db()
        self.assertIsNone(channel.cable_id)
        self.assertIsNone(channel.cable_connector)
        self.assertIsNone(channel.cable_positions)
        self.assertPathIsNotSet(channel)


class ChannelizedInterfaceTestCase(TestCase):
    """
    Test validation, properties, renaming, and REST/GraphQL filtering of channelized Interfaces and their channel
    subinterfaces. Cable-path and bulk-view coverage remain in their own specialized TestCase classes below;
    commit-dependent cascade side effects remain in the separate ChannelizedInterfaceRenameSideEffectsTestCase
    (a TransactionTestCase).
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

        # A second, isolated device for the kind=physical filter tests further below, so their pre-built channel
        # subinterface doesn't collide with the many ad hoc channel_id=1 children the tests above create against
        # cls.parent.
        cls.filter_device = Device.objects.create(site=site, device_type=device_type, role=role, name='Device 2')
        cls.filter_parent = Interface.objects.create(
            device=cls.filter_device, name='ft0', type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS, channels=1
        )
        cls.filter_channel = Interface.objects.create(
            device=cls.filter_device, name='ft0:1', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS,
            parent=cls.filter_parent, channel_id=1
        )
        cls.filter_plain = Interface.objects.create(
            device=cls.filter_device, name='fx0', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )

    # -- validation --------------------------------------------------------------------------------------------

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

    def test_channel_id_rejected_on_interface_with_existing_cable_termination(self):
        # A channel subinterface's cable state is mirrored from its parent; an interface that already carries its
        # own direct cable connection cannot also be converted into one.
        interface = Interface.objects.create(
            device=self.device, name='xe0', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )
        far = Interface.objects.create(
            device=self.device, name='xe1', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS
        )
        cable = Cable(a_terminations=[interface], b_terminations=[far])
        cable.clean()
        cable.save()

        interface.refresh_from_db()
        interface.parent = self.parent
        interface.channel_id = 1
        with self.assertRaises(ValidationError):
            interface.full_clean()

    # -- renaming ----------------------------------------------------------------------------------------------
    # Renaming a channelized parent interface updates the names of any channel subinterfaces which follow the
    # "<parent name>:<channel ID>" convention.

    def test_rename_updates_conforming_children(self):
        child = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )

        self.parent.name = 'et1'
        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save()

        child.refresh_from_db()
        self.assertEqual(child.name, 'et1:1')

    def test_rename_cascade_uses_save_state_db_not_router(self):
        # The deferred callback and child query/save must reuse self._state.db (the DB actually used by
        # save()), not re-invoke router.db_for_write() -- which could differ from an explicit save(using=...).
        # Django's own base Model.save() legitimately consults the router once per plain save() call (when no
        # explicit using= is given); the pre-fix mixin code consulted it twice more for the same instance during
        # the cascade. Spy on calls for the Interface model specifically to confirm only that one call remains.
        child = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )

        self.parent.name = 'et1'
        real_db_for_write = router.db_for_write
        calls = []

        def spy(model, **hints):
            if model is Interface:
                calls.append(model)
            return real_db_for_write(model, **hints)

        with mock.patch('django.db.router.db_for_write', side_effect=spy):
            with self.captureOnCommitCallbacks(execute=True):
                self.parent.save()

        child.refresh_from_db()
        self.assertEqual(child.name, 'et1:1')
        self.assertEqual(
            len(calls), 1,
            "router.db_for_write(Interface) was consulted more than once; the rename cascade should reuse "
            "self._state.db instead of re-invoking the router."
        )

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
        # colliding_child conforms to the naming convention, so it reaches save() and genuinely hits
        # IntegrityError; a collision there must not block the other, non-colliding child's rename.
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
        # A sibling object saved later in the same transaction (e.g. by a bulk view) must not be able to
        # silently undo the cascade by writing back a stale in-memory copy of the child's name.
        child = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )

        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            self.parent.name = 'et1'
            self.parent.save()

            # Deferred until "commit" (running the captured callbacks below): not yet propagated.
            child.refresh_from_db()
            self.assertEqual(child.name, 'et0:1')

            # Simulate a sibling's own save() in the same batch, re-asserting the child's stale name — exactly
            # what BulkRenameView does when the same child is also selected in a bulk rename.
            stale_copy = Interface.objects.get(pk=child.pk)
            stale_copy.save()

        # The deferred cascade is the last write once the transaction commits: still renames the child.
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

    def test_generator_update_fields_cascades_rename(self):
        # A one-shot iterable naming 'name' must still persist the rename and cascade it.
        child = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )

        self.parent.name = 'et1'
        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save(update_fields=(field for field in ('name',)))

        self.parent.refresh_from_db()
        child.refresh_from_db()
        self.assertEqual(self.parent.name, 'et1')
        self.assertEqual(child.name, 'et1:1')

    def test_update_fields_excluding_name_does_not_desync_later_full_rename(self):
        # A later full save() must still correctly cascade, proving the earlier partial save didn't refresh
        # _original_name to its unpersisted in-memory value.
        child = Interface.objects.create(
            device=self.device, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL, parent=self.parent, channel_id=1
        )

        self.parent.name = 'et1'
        self.parent.save(update_fields=['description'])  # Not persisted; DB name is still 'et0'

        with self.captureOnCommitCallbacks(execute=True):
            self.parent.save()  # Full save: persists 'et1', cascading from the true prior (DB) name 'et0'

        child.refresh_from_db()
        self.assertEqual(child.name, 'et1:1')

    # -- kind=physical filtering ---------------------------------------------------------------------------------
    # A channel subinterface is excluded from kind=physical (REST) / kind: PHYSICAL (GraphQL), even when it keeps
    # its own specific physical type rather than the generic "channel" type -- matching Interface.is_wired, since
    # it derives its cable from its channelized parent and cannot be cabled directly.

    def test_rest_kind_physical_excludes_channel_subinterface(self):
        filterset = InterfaceFilterSet({'kind': 'physical'}, Interface.objects.all())
        results = set(filterset.qs.values_list('pk', flat=True))
        self.assertIn(self.filter_parent.pk, results)
        self.assertIn(self.filter_plain.pk, results)
        self.assertNotIn(self.filter_channel.pk, results)

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
        self.assertIn(self.filter_parent.pk, result_ids)
        self.assertIn(self.filter_plain.pk, result_ids)
        self.assertNotIn(self.filter_channel.pk, result_ids)


class ChannelizedInterfaceRenameSideEffectsTestCase(TransactionTestCase):
    """
    Test that a cascaded channel subinterface rename behaves as a full save() (updating _name and last_updated,
    and recording an ObjectChange), not merely as a raw name update. Uses TransactionTestCase, not TestCase, so
    the request's transaction really commits and on_commit() fires inline as in production — under TestCase the
    whole test runs inside one uncommitted transaction, and captureOnCommitCallbacks() would only fire the
    deferred rename after the request (and its changelog's current_request context) has already torn down.
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


class ChannelizedInterfaceTemplateTestCase(TestCase):
    """
    Test validation, instantiation-time replication, and renaming of channelized InterfaceTemplates and their
    channel subinterface templates.
    """

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Generic', slug='generic')
        cls.device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device', slug='test-device')
        cls.role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        cls.site = Site.objects.create(name='Site', slug='site')
        cls.parent = InterfaceTemplate.objects.create(
            device_type=cls.device_type, name='et0', type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS, channels=4
        )

        # A second, isolated device type with its own pre-built channel subinterface templates, for the
        # instantiation-replication test below -- so its four pre-existing channel_id 1-4 children don't collide
        # with the many ad hoc children the validation/rename tests create against cls.parent.
        cls.replication_device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Replication Device', slug='replication-device'
        )
        replication_parent = InterfaceTemplate.objects.create(
            device_type=cls.replication_device_type, name='et0', type=InterfaceTypeChoices.TYPE_40GE_QSFP_PLUS,
            channels=4
        )
        for i in range(1, 5):
            InterfaceTemplate.objects.create(
                device_type=cls.replication_device_type,
                name=f'et0:{i}',
                type=InterfaceTypeChoices.TYPE_CHANNEL,
                parent=replication_parent,
                channel_id=i,
            )

    # -- instantiation-time replication -------------------------------------------------------------------------

    def test_channelization_replicated_on_instantiation(self):
        device = Device.objects.create(
            site=self.site, device_type=self.replication_device_type, role=self.role, name='Device 1'
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

    # -- validation ----------------------------------------------------------------------------------------------

    def test_parent_template_validation(self):
        # A parent template must belong to the same device type
        other_type = DeviceType.objects.create(
            manufacturer=self.device_type.manufacturer, model='Other Device', slug='other-device'
        )
        template = InterfaceTemplate(
            device_type=other_type, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=1
        )
        with self.assertRaises(ValidationError):
            template.full_clean()

    def test_template_channel_id_allowed_on_specific_physical_type(self):
        # A channel subinterface template may keep its own specific physical type (e.g. to record the actual
        # transceiver in use) instead of the generic "channel" type.
        template = InterfaceTemplate(
            device_type=self.device_type, name='et0:1', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS,
            parent=self.parent, channel_id=1
        )
        template.full_clean()  # Should not raise

    def test_template_parent_channel_id_must_be_unique(self):
        InterfaceTemplate.objects.create(
            device_type=self.device_type, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=1
        )
        duplicate = InterfaceTemplate(
            device_type=self.device_type, name='et0:1b', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=1
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_template_channel_id_within_parent_range(self):
        # A channel_id beyond the parent's channel count is rejected at the template level
        template = InterfaceTemplate(
            device_type=self.device_type, name='et0:5', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=5
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

    def test_template_channel_id_requires_parent(self):
        # A channel_id with no parent assigned is rejected, regardless of type
        template = InterfaceTemplate(
            device_type=self.device_type, name='xe1', type=InterfaceTypeChoices.TYPE_10GE_SFP_PLUS,
            channel_id=1
        )
        with self.assertRaises(ValidationError):
            template.full_clean()

    def test_template_reduce_channels_below_bound_child_rejected(self):
        # Bind a channel to the highest channel of the parent, then attempt to reduce the parent's channel count
        InterfaceTemplate.objects.create(
            device_type=self.device_type, name='et0:4', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=4
        )
        self.parent.channels = 2
        with self.assertRaises(ValidationError):
            self.parent.full_clean()

    def test_template_clear_channels_with_bound_child_rejected(self):
        # De-channelizing a parent template entirely is rejected while a channel subinterface template is bound to it
        InterfaceTemplate.objects.create(
            device_type=self.device_type, name='et0:1', type=InterfaceTypeChoices.TYPE_CHANNEL,
            parent=self.parent, channel_id=1
        )
        self.parent.channels = None
        with self.assertRaises(ValidationError):
            self.parent.full_clean()

    # -- renaming ------------------------------------------------------------------------------------------------
    # Renaming a channelized parent InterfaceTemplate updates the names of any channel subinterface templates
    # which follow the "<parent name>:<channel ID>" convention.

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
