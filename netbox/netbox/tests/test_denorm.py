"""
Tests for the declarative denormalization framework.
"""
from unittest.mock import MagicMock

from django.test import TestCase

from netbox.denorm import DenormSpec, DenormRegistry, denorm_registry


class DenormSpecTests(TestCase):

    def test_source_path_resolution(self):
        spec = DenormSpec(field_name='_site', source_path='device.site')
        mock = MagicMock()
        mock.device.site = 'SiteA'
        self.assertEqual(spec.resolve(mock), 'SiteA')

    def test_source_path_none_intermediate(self):
        spec = DenormSpec(field_name='_site', source_path='device.site')
        mock = MagicMock()
        mock.device = None
        self.assertIsNone(spec.resolve(mock))

    def test_compute_function(self):
        spec = DenormSpec(
            field_name='available_power',
            compute=lambda inst: inst.voltage * inst.amperage,
        )
        mock = MagicMock()
        mock.voltage = 120
        mock.amperage = 20
        self.assertEqual(spec.resolve(mock), 2400)

    def test_compute_takes_precedence(self):
        spec = DenormSpec(
            field_name='_site',
            source_path='device.site',
            compute=lambda inst: 'computed',
        )
        mock = MagicMock()
        self.assertEqual(spec.resolve(mock), 'computed')


class DenormRegistryTests(TestCase):

    def test_register_and_get(self):
        reg = DenormRegistry()
        spec = DenormSpec(field_name='_site', source_path='device.site')
        reg.register('dcim.interface', spec)
        self.assertEqual(len(reg.get_specs('dcim.interface')), 1)
        self.assertTrue(reg.has_specs('dcim.interface'))
        self.assertFalse(reg.has_specs('dcim.other'))

    def test_compute_all(self):
        reg = DenormRegistry()
        reg.register('test.model',
            DenormSpec(field_name='x', compute=lambda i: 10),
            DenormSpec(field_name='y', compute=lambda i: 20),
        )
        mock = MagicMock()
        mock._meta.app_label = 'test'
        mock._meta.model_name = 'model'
        reg.compute_all(mock)
        # setattr is called on the mock for each field
        self.assertEqual(mock.x, 10)
        self.assertEqual(mock.y, 20)

    def test_compute_if_changed(self):
        reg = DenormRegistry()
        reg.register('test.model',
            DenormSpec(field_name='x', compute=lambda i: 10,
                       depends_on=frozenset({'a'})),
            DenormSpec(field_name='y', compute=lambda i: 20,
                       depends_on=frozenset({'b'})),
        )
        mock = MagicMock()
        mock._meta.app_label = 'test'
        mock._meta.model_name = 'model'
        reg.compute_if_changed(mock, {'a'})
        self.assertEqual(mock.x, 10)
        # y should not have been set (only 'a' changed)
        self.assertNotEqual(mock.y, 20)

    def test_summary(self):
        reg = DenormRegistry()
        reg.register('a.b', DenormSpec(field_name='x'))
        reg.register('a.b', DenormSpec(field_name='y'))
        reg.register('c.d', DenormSpec(field_name='z'))
        s = reg.summary()
        self.assertEqual(s['models'], 2)
        self.assertEqual(s['total_fields'], 3)


class GlobalRegistryPopulationTests(TestCase):
    """Verify that the global denorm_registry is populated with expected entries."""

    def test_component_models_registered(self):
        for model in ['dcim.consoleport', 'dcim.interface', 'dcim.powerport']:
            specs = denorm_registry.get_specs(model)
            field_names = {s.field_name for s in specs}
            self.assertIn('_site', field_names, f'{model} missing _site')
            self.assertIn('_location', field_names, f'{model} missing _location')
            self.assertIn('_rack', field_names, f'{model} missing _rack')

    def test_powerfeed_registered(self):
        specs = denorm_registry.get_specs('dcim.powerfeed')
        field_names = {s.field_name for s in specs}
        self.assertIn('available_power', field_names)

    def test_iprange_registered(self):
        specs = denorm_registry.get_specs('ipam.iprange')
        field_names = {s.field_name for s in specs}
        self.assertIn('size', field_names)

    def test_vlangroup_registered(self):
        specs = denorm_registry.get_specs('ipam.vlangroup')
        field_names = {s.field_name for s in specs}
        self.assertIn('_total_vlan_ids', field_names)

    def test_prefix_scope_cache(self):
        specs = denorm_registry.get_specs('ipam.prefix')
        field_names = {s.field_name for s in specs}
        for f in ['_region', '_site_group', '_site', '_location', 'prefix']:
            self.assertIn(f, field_names, f'ipam.prefix missing {f}')

    def test_circuit_termination_cache(self):
        specs = denorm_registry.get_specs('circuits.circuittermination')
        field_names = {s.field_name for s in specs}
        for f in ['_provider_network', '_region', '_site_group', '_site', '_location']:
            self.assertIn(f, field_names, f'circuits.circuittermination missing {f}')

    def test_weight_mixin_models(self):
        for model in ['dcim.devicetype', 'dcim.moduletype', 'dcim.rack', 'dcim.racktype']:
            specs = denorm_registry.get_specs(model)
            field_names = {s.field_name for s in specs}
            self.assertIn('_abs_weight', field_names, f'{model} missing _abs_weight')

    def test_distance_mixin_models(self):
        for model in ['circuits.circuit', 'wireless.wirelesslink']:
            specs = denorm_registry.get_specs(model)
            field_names = {s.field_name for s in specs}
            self.assertIn('_abs_distance', field_names, f'{model} missing _abs_distance')

    def test_cable_specs(self):
        specs = denorm_registry.get_specs('dcim.cable')
        field_names = {s.field_name for s in specs}
        self.assertIn('_abs_length', field_names)

    def test_cablepath_specs(self):
        specs = denorm_registry.get_specs('dcim.cablepath')
        field_names = {s.field_name for s in specs}
        self.assertIn('_nodes', field_names)

    def test_wireless_link_specs(self):
        specs = denorm_registry.get_specs('wireless.wirelesslink')
        field_names = {s.field_name for s in specs}
        self.assertIn('_interface_a_device', field_names)
        self.assertIn('_interface_b_device', field_names)

    def test_virtual_machine_specs(self):
        specs = denorm_registry.get_specs('virtualization.virtualmachine')
        field_names = {s.field_name for s in specs}
        self.assertIn('site', field_names)

    def test_cable_termination_specs(self):
        specs = denorm_registry.get_specs('dcim.cabletermination')
        field_names = {s.field_name for s in specs}
        for f in ['_device', '_rack', '_location', '_site']:
            self.assertIn(f, field_names, f'dcim.cabletermination missing {f}')

    def test_registry_summary(self):
        s = denorm_registry.summary()
        self.assertGreaterEqual(s['models'], 15)
        self.assertGreaterEqual(s['total_fields'], 40)
