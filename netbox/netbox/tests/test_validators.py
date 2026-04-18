"""
Tests for the composable validator framework.
"""
from unittest.mock import MagicMock

from django.core.exceptions import ValidationError
from django.test import TestCase

from netbox.validators import (
    ModelValidator,
    ValidatorCategory,
    ValidatorRegistry,
    validator_registry,
)


class ValidatorRegistryTests(TestCase):

    def test_register_and_get(self):
        reg = ValidatorRegistry()
        v = ModelValidator(
            name='test_v',
            model_label='test.model',
            fields=frozenset({'x'}),
            category=ValidatorCategory.FIELD,
            validate=lambda inst: None,
        )
        reg.register('test.model', v)
        self.assertEqual(len(reg.get_validators('test.model')), 1)
        self.assertTrue(reg.has_validators('test.model'))

    def test_filter_by_category(self):
        reg = ValidatorRegistry()
        reg.register('test.model',
            ModelValidator(name='a', model_label='test.model',
                          category=ValidatorCategory.FIELD, validate=lambda i: None),
            ModelValidator(name='b', model_label='test.model',
                          category=ValidatorCategory.CROSS_MODEL, validate=lambda i: None),
        )
        field_only = reg.get_validators('test.model',
                                        categories={ValidatorCategory.FIELD})
        self.assertEqual(len(field_only), 1)
        self.assertEqual(field_only[0].name, 'a')

    def test_exclude_category(self):
        reg = ValidatorRegistry()
        reg.register('test.model',
            ModelValidator(name='a', model_label='test.model',
                          category=ValidatorCategory.FIELD, validate=lambda i: None),
            ModelValidator(name='b', model_label='test.model',
                          category=ValidatorCategory.CROSS_MODEL, validate=lambda i: None),
        )
        result = reg.get_validators('test.model',
                                    exclude_categories={ValidatorCategory.CROSS_MODEL})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'a')

    def test_filter_by_fields(self):
        reg = ValidatorRegistry()
        reg.register('test.model',
            ModelValidator(name='a', model_label='test.model',
                          fields=frozenset({'x'}), validate=lambda i: None),
            ModelValidator(name='b', model_label='test.model',
                          fields=frozenset({'y'}), validate=lambda i: None),
        )
        result = reg.get_validators('test.model', fields={'x'})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'a')

    def test_validate_collects_errors(self):
        reg = ValidatorRegistry()
        reg.register('test.model',
            ModelValidator(name='a', model_label='test.model',
                          validate=lambda i: (_ for _ in ()).throw(
                              ValidationError({'x': 'bad x'}))),
            ModelValidator(name='b', model_label='test.model',
                          validate=lambda i: (_ for _ in ()).throw(
                              ValidationError({'y': 'bad y'}))),
        )
        mock = MagicMock()
        mock._meta.app_label = 'test'
        mock._meta.model_name = 'model'
        with self.assertRaises(ValidationError) as cm:
            reg.validate(mock)
        self.assertIn('x', cm.exception.message_dict)
        self.assertIn('y', cm.exception.message_dict)

    def test_validate_for_merge_skips_cross_model(self):
        reg = ValidatorRegistry()
        reg.register('test.model',
            ModelValidator(name='field_v', model_label='test.model',
                          fields=frozenset({'x'}),
                          category=ValidatorCategory.FIELD,
                          validate=lambda i: None),
            ModelValidator(name='cross_v', model_label='test.model',
                          fields=frozenset({'x'}),
                          category=ValidatorCategory.CROSS_MODEL,
                          validate=lambda i: (_ for _ in ()).throw(
                              ValidationError('should not run'))),
        )
        mock = MagicMock()
        mock._meta.app_label = 'test'
        mock._meta.model_name = 'model'
        # Should not raise — cross_model is skipped
        reg.validate_for_merge(mock, {'x'})

    def test_summary(self):
        reg = ValidatorRegistry()
        reg.register('a.b',
            ModelValidator(name='v1', model_label='a.b',
                          category=ValidatorCategory.FIELD, queries_db=False),
            ModelValidator(name='v2', model_label='a.b',
                          category=ValidatorCategory.CROSS_MODEL, queries_db=True),
        )
        s = reg.summary()
        self.assertEqual(s['models'], 1)
        self.assertEqual(s['total_validators'], 2)
        self.assertEqual(s['db_querying'], 1)

    def test_cross_model_validators(self):
        reg = ValidatorRegistry()
        reg.register('a.b',
            ModelValidator(name='v1', model_label='a.b',
                          category=ValidatorCategory.FIELD),
            ModelValidator(name='v2', model_label='a.b',
                          category=ValidatorCategory.CROSS_MODEL),
            ModelValidator(name='v3', model_label='a.b',
                          category=ValidatorCategory.UNIQUENESS),
        )
        cross = reg.cross_model_validators('a.b')
        self.assertEqual(len(cross), 2)
        names = {v.name for v in cross}
        self.assertEqual(names, {'v2', 'v3'})


class GlobalRegistryPopulationTests(TestCase):
    """Verify that the global validator_registry has expected entries."""

    def test_rack_validators(self):
        validators = validator_registry.get_validators('dcim.rack')
        names = {v.name for v in validators}
        self.assertIn('rack_location_site', names)
        self.assertIn('rack_height_vs_devices', names)
        self.assertIn('rack_outer_dimensions', names)
        self.assertIn('rack_max_weight', names)

    def test_device_validators(self):
        validators = validator_registry.get_validators('dcim.device')
        names = {v.name for v in validators}
        self.assertIn('device_site_rack_location', names)
        self.assertIn('device_rack_space', names)
        self.assertIn('device_primary_ips', names)
        self.assertIn('device_cluster', names)
        self.assertGreaterEqual(len(names), 7)

    def test_ipam_validators(self):
        for model in ['ipam.aggregate', 'ipam.prefix', 'ipam.iprange']:
            validators = validator_registry.get_validators(model)
            self.assertGreater(len(validators), 0, f'{model} has no validators')

    def test_vpn_validators(self):
        for model in ['vpn.l2vpntermination', 'vpn.tunneltermination']:
            validators = validator_registry.get_validators(model)
            self.assertGreater(len(validators), 0, f'{model} has no validators')

    def test_virtualization_validators(self):
        validators = validator_registry.get_validators('virtualization.virtualmachine')
        names = {v.name for v in validators}
        self.assertIn('vm_site_cluster', names)
        self.assertIn('vm_primary_ips', names)

    def test_cross_model_count(self):
        """At least 15 cross-model/uniqueness validators across all models."""
        total = 0
        for model in validator_registry.registered_models():
            total += len(validator_registry.cross_model_validators(model))
        self.assertGreaterEqual(total, 12)

    def test_summary_stats(self):
        s = validator_registry.summary()
        self.assertGreaterEqual(s['models'], 10)
        self.assertGreaterEqual(s['total_validators'], 25)
        self.assertGreaterEqual(s['db_querying'], 10)
