from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from circuits.forms import CircuitTerminationForm
from circuits.models import Circuit, CircuitType, Provider, ProviderNetwork


class CircuitTerminationFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Circuit Type 1', slug='circuit-type-1')

        cls.circuit = Circuit.objects.create(
            cid='Circuit 1',
            provider=provider,
            type=circuit_type,
        )
        cls.provider_network = ProviderNetwork.objects.create(
            name='Provider Network 1',
            provider=provider,
        )

    def test_termination_required_when_termination_type_is_selected(self):
        """
        Selecting a termination type without a target object should report a
        validation error against the visible form field.
        """
        provider_network_type = ContentType.objects.get_for_model(ProviderNetwork)

        form = CircuitTerminationForm(
            data={
                'circuit': self.circuit.pk,
                'term_side': 'A',
                'termination_content_type': provider_network_type.pk,
                'termination_object_id': '',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('termination', form.errors)
        self.assertIn('Please select a provider network.', form.errors['termination'])
        self.assertNotIn('termination_object_id', form.errors)
