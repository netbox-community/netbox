from django.test import TestCase

from dcim.choices import CableLengthUnitChoices, CoolingSourceTypeChoices, RackFormFactorChoices
from dcim.models import *
from netbox.choices import DiameterUnitChoices, FlowRateUnitChoices, WeightUnitChoices
from utilities.conversion import to_grams, to_liters_per_minute, to_meters, to_millimeters
from utilities.testing import create_test_device
from utilities.testing.mixins import NormalizedMeasurementTestMixin

#
# Per-measurement mixins
#


class WeightTestMixin(NormalizedMeasurementTestMixin):
    value_field = 'weight'
    unit_field = 'weight_unit'
    normalized_field = '_abs_weight'
    unit_choices = WeightUnitChoices
    converter = staticmethod(to_grams)


class MaxWeightTestMixin(WeightTestMixin):
    value_field = 'max_weight'
    normalized_field = '_abs_max_weight'
    value = 123  # max_weight is an integer field


class DiameterTestMixin(NormalizedMeasurementTestMixin):
    value_field = 'diameter'
    unit_field = 'diameter_unit'
    normalized_field = '_abs_diameter'
    unit_choices = DiameterUnitChoices
    converter = staticmethod(to_millimeters)


class MaxFlowTestMixin(NormalizedMeasurementTestMixin):
    value_field = 'max_flow'
    unit_field = 'max_flow_unit'
    normalized_field = '_abs_max_flow'
    unit_choices = FlowRateUnitChoices
    converter = staticmethod(to_liters_per_minute)


#
# Weight
#

class DeviceTypeWeightTestCase(WeightTestMixin, TestCase):
    model = DeviceType

    @classmethod
    def setUpTestData(cls):
        cls.manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

    def create_instance(self, **attrs):
        index = next(self.sequence)
        return DeviceType(
            manufacturer=self.manufacturer, model=f'Device Type {index}', slug=f'device-type-{index}', **attrs
        )


class ModuleTypeWeightTestCase(WeightTestMixin, TestCase):
    model = ModuleType

    @classmethod
    def setUpTestData(cls):
        cls.manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

    def create_instance(self, **attrs):
        return ModuleType(manufacturer=self.manufacturer, model=f'Module Type {next(self.sequence)}', **attrs)


class RackTypeTestMixin:
    model = RackType

    @classmethod
    def setUpTestData(cls):
        cls.manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

    def create_instance(self, **attrs):
        index = next(self.sequence)
        return RackType(
            manufacturer=self.manufacturer,
            model=f'Rack Type {index}',
            slug=f'rack-type-{index}',
            form_factor=RackFormFactorChoices.TYPE_CABINET,
            **attrs
        )


class RackTypeWeightTestCase(RackTypeTestMixin, WeightTestMixin, TestCase):
    pass


class RackTypeMaxWeightTestCase(RackTypeTestMixin, MaxWeightTestMixin, TestCase):
    pass


class RackTestMixin:
    model = Rack

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Site 1', slug='site-1')

    def create_instance(self, **attrs):
        return Rack(site=self.site, name=f'Rack {next(self.sequence)}', **attrs)


class RackWeightTestCase(RackTestMixin, WeightTestMixin, TestCase):
    pass


class RackMaxWeightTestCase(RackTestMixin, MaxWeightTestMixin, TestCase):
    pass


#
# Length
#

class CableLengthTestCase(NormalizedMeasurementTestMixin, TestCase):
    model = Cable
    value_field = 'length'
    unit_field = 'length_unit'
    normalized_field = '_abs_length'
    unit_choices = CableLengthUnitChoices
    converter = staticmethod(to_meters)

    def create_instance(self, **attrs):
        return Cable(**attrs)


#
# Cooling
#

class CoolingComponentTestMixin:

    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device('Device 1')

    def create_instance(self, **attrs):
        return self.model(device=self.device, name=f'Cooling Component {next(self.sequence)}', **attrs)


class CoolingIntakeDiameterTestCase(CoolingComponentTestMixin, DiameterTestMixin, TestCase):
    model = CoolingIntake


class CoolingIntakeMaxFlowTestCase(CoolingComponentTestMixin, MaxFlowTestMixin, TestCase):
    model = CoolingIntake


class CoolingOutflowDiameterTestCase(CoolingComponentTestMixin, DiameterTestMixin, TestCase):
    model = CoolingOutflow


class CoolingComponentTemplateTestMixin:

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        cls.device_type = DeviceType.objects.create(
            manufacturer=manufacturer, model='Device Type 1', slug='device-type-1'
        )

    def create_instance(self, **attrs):
        return self.model(
            device_type=self.device_type, name=f'Cooling Component {next(self.sequence)}', **attrs
        )


class CoolingIntakeTemplateDiameterTestCase(CoolingComponentTemplateTestMixin, DiameterTestMixin, TestCase):
    model = CoolingIntakeTemplate


class CoolingIntakeTemplateMaxFlowTestCase(CoolingComponentTemplateTestMixin, MaxFlowTestMixin, TestCase):
    model = CoolingIntakeTemplate


class CoolingOutflowTemplateDiameterTestCase(CoolingComponentTemplateTestMixin, DiameterTestMixin, TestCase):
    model = CoolingOutflowTemplate


class CoolingFeedMaxFlowTestCase(MaxFlowTestMixin, TestCase):
    model = CoolingFeed

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site 1', slug='site-1')
        cls.cooling_source = CoolingSource.objects.create(
            site=site, name='Cooling Source 1', type=CoolingSourceTypeChoices.TYPE_CHILLER
        )

    def create_instance(self, **attrs):
        return CoolingFeed(
            cooling_source=self.cooling_source, name=f'Cooling Feed {next(self.sequence)}', **attrs
        )
