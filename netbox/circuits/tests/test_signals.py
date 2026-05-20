from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase

from circuits import signals
from circuits.models import Circuit, CircuitTermination, CircuitType, Provider
from dcim.models import (
    Cable,
    CablePath,
    Device,
    DeviceRole,
    DeviceType,
    Interface,
    Manufacturer,
    Site,
)


class RebuildCablepathsSignalTestCase(TestCase):
    """
    Verify circuits.signals.rebuild_cablepaths retraces paths that cross the peer termination
    when a CircuitTermination is saved or deleted.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Site', slug='site')
        manufacturer = Manufacturer.objects.create(name='Manufacturer', slug='manufacturer')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type')
        device_role = DeviceRole.objects.create(name='Device Role', slug='device-role')
        cls.device = Device.objects.create(site=cls.site, device_type=device_type, role=device_role, name='Device 1')
        provider = Provider.objects.create(name='Provider', slug='provider')
        circuit_type = CircuitType.objects.create(name='Circuit Type', slug='circuit-type')
        cls.circuit = Circuit.objects.create(provider=provider, type=circuit_type, cid='Circuit 1')

    def test_saving_termination_rebuilds_peer_path(self):
        interface = Interface.objects.create(device=self.device, name='Interface 1')
        site_z = Site.objects.create(name='Site Z', slug='site-z')
        termination_a = CircuitTermination.objects.create(circuit=self.circuit, termination=self.site, term_side='A')
        termination_z = CircuitTermination.objects.create(circuit=self.circuit, termination=site_z, term_side='Z')
        Cable(a_terminations=[interface], b_terminations=[termination_a]).save()
        original_path = CablePath.objects.get()

        # Saving the Z (peer) termination should cause rebuild_paths to run for the A peer.
        with patch('circuits.signals.rebuild_paths') as rebuild_paths:
            termination_z.save()

        rebuild_paths.assert_called_once()
        rebuilt_for = rebuild_paths.call_args.args[0]
        self.assertEqual([t.pk for t in rebuilt_for], [termination_a.pk])

        # Without patching, the real signal should retrace the path successfully.
        termination_z.save()
        self.assertEqual(CablePath.objects.count(), 1)
        self.assertNotEqual(CablePath.objects.get().pk, original_path.pk)

    def test_deleting_termination_rebuilds_peer_path(self):
        site_z = Site.objects.create(name='Site Z', slug='site-z')
        termination_a = CircuitTermination.objects.create(circuit=self.circuit, termination=self.site, term_side='A')
        termination_z = CircuitTermination.objects.create(circuit=self.circuit, termination=site_z, term_side='Z')

        with patch('circuits.signals.rebuild_paths') as rebuild_paths:
            termination_z.delete()

        rebuild_paths.assert_called_once()
        rebuilt_for = rebuild_paths.call_args.args[0]
        self.assertEqual([t.pk for t in rebuilt_for], [termination_a.pk])

    def test_saving_termination_without_peer_does_not_rebuild(self):
        termination = CircuitTermination.objects.create(circuit=self.circuit, termination=self.site, term_side='A')

        with patch('circuits.signals.rebuild_paths') as rebuild_paths:
            termination.save()

        rebuild_paths.assert_not_called()


class RebuildCablepathsDirectHandlerTestCase(SimpleTestCase):
    """
    Direct-call tests for rebuild_cablepaths branches that are not reachable through
    normal model operations (e.g. raw=True is only set by Django's loaddata pathway).
    """

    def test_raw_import_skips_peer_lookup_and_rebuild(self):
        instance = SimpleNamespace(get_peer_termination=MagicMock())

        with patch.object(signals, 'rebuild_paths') as rebuild_paths:
            signals.rebuild_cablepaths(instance=instance, raw=True)

        instance.get_peer_termination.assert_not_called()
        rebuild_paths.assert_not_called()
