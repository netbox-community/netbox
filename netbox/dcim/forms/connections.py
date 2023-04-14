from django import forms
from django.utils.translation import gettext as _

from circuits.models import Circuit, CircuitTermination
from dcim.models import *
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField
from .model_forms import CableForm


def get_cable_form(a_type, b_type):

    class FormMetaclass(forms.models.ModelFormMetaclass):

        def __new__(mcs, name, bases, attrs):

            for cable_end, term_cls in (('a', a_type), ('b', b_type)):

                # Device component
                if hasattr(term_cls, 'device'):

                    attrs[f'termination_{cable_end}_device'] = DynamicModelChoiceField(
                        queryset=Device.objects.all(),
                        label=_('Device'),
                        required=False,
                        selector=True,
                        initial_params={
                            f'{term_cls._meta.model_name}s__in': f'${cable_end}_terminations'
                        }
                    )
                    attrs[f'{cable_end}_terminations'] = DynamicModelMultipleChoiceField(
                        queryset=term_cls.objects.all(),
                        label=term_cls._meta.verbose_name.title(),
                        disabled_indicator='_occupied',
                        query_params={
                            'device_id': f'$termination_{cable_end}_device',
                            'kind': 'physical',  # Exclude virtual interfaces
                        }
                    )

                # PowerFeed
                elif term_cls == PowerFeed:

                    attrs[f'termination_{cable_end}_powerpanel'] = DynamicModelChoiceField(
                        queryset=PowerPanel.objects.all(),
                        label=_('Power Panel'),
                        required=False,
                        selector=True,
                        initial_params={
                            'powerfeeds__in': f'${cable_end}_terminations'
                        }
                    )
                    attrs[f'{cable_end}_terminations'] = DynamicModelMultipleChoiceField(
                        queryset=term_cls.objects.all(),
                        label=_('Power Feed'),
                        disabled_indicator='_occupied',
                        query_params={
                            'power_panel_id': f'$termination_{cable_end}_powerpanel',
                        }
                    )

                # CircuitTermination
                elif term_cls == CircuitTermination:

                    attrs[f'termination_{cable_end}_circuit'] = DynamicModelChoiceField(
                        queryset=Circuit.objects.all(),
                        label=_('Circuit'),
                        selector=True,
                        initial_params={
                            'terminations__in': f'${cable_end}_terminations'
                        }
                    )
                    attrs[f'{cable_end}_terminations'] = DynamicModelMultipleChoiceField(
                        queryset=term_cls.objects.all(),
                        label=_('Side'),
                        disabled_indicator='_occupied',
                        query_params={
                            'circuit_id': f'$termination_{cable_end}_circuit',
                        }
                    )

            return super().__new__(mcs, name, bases, attrs)

    class _CableForm(CableForm, metaclass=FormMetaclass):

        def __init__(self, *args, **kwargs):

            # TODO: Temporary hack to work around list handling limitations with utils.normalize_querydict()
            for field_name in ('a_terminations', 'b_terminations'):
                if field_name in kwargs.get('initial', {}) and type(kwargs['initial'][field_name]) is not list:
                    kwargs['initial'][field_name] = [kwargs['initial'][field_name]]

            super().__init__(*args, **kwargs)

            if self.instance and self.instance.pk:
                # Initialize A/B terminations when modifying an existing Cable instance
                self.initial['a_terminations'] = self.instance.a_terminations
                self.initial['b_terminations'] = self.instance.b_terminations

        def clean(self):
            super().clean()

            # Set the A/B terminations on the Cable instance
            self.instance.a_terminations = self.cleaned_data['a_terminations']
            self.instance.b_terminations = self.cleaned_data['b_terminations']

    return _CableForm
