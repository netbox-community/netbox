from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from circuits.models import Circuit, CircuitTermination
from dcim.models import *
from utilities.forms.fields import DynamicModelMultipleChoiceField
from .model_forms import CableForm


def get_cable_form(a_type, b_type):

    class FormMetaclass(forms.models.ModelFormMetaclass):

        def __new__(mcs, name, bases, attrs):

            for cable_end, term_cls in (('a', a_type), ('b', b_type)):

                # Device component
                if hasattr(term_cls, 'device'):

                    attrs[f'termination_{cable_end}_device'] = DynamicModelMultipleChoiceField(
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
                        context={
                            'disabled': '_occupied',
                            'parent': 'device',
                        },
                        query_params={
                            'device_id': f'$termination_{cable_end}_device',
                            'kind': 'physical',  # Exclude virtual interfaces
                        }
                    )

                # PowerFeed
                elif term_cls == PowerFeed:

                    attrs[f'termination_{cable_end}_powerpanel'] = DynamicModelMultipleChoiceField(
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
                        context={
                            'disabled': '_occupied',
                            'parent': 'powerpanel',
                        },
                        query_params={
                            'power_panel_id': f'$termination_{cable_end}_powerpanel',
                        }
                    )

                # CircuitTermination
                elif term_cls == CircuitTermination:

                    attrs[f'termination_{cable_end}_circuit'] = DynamicModelMultipleChoiceField(
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
                        context={
                            'disabled': '_occupied',
                            'parent': 'circuit',
                        },
                        query_params={
                            'circuit_id': f'$termination_{cable_end}_circuit',
                        }
                    )

            return super().__new__(mcs, name, bases, attrs)

    class _CableForm(CableForm, metaclass=FormMetaclass):

        def __init__(self, *args, initial=None, **kwargs):
            initial = initial or {}

            if a_type:
                a_ct = ContentType.objects.get_for_model(a_type)
                initial['a_terminations_type'] = f'{a_ct.app_label}.{a_ct.model}'
            if b_type:
                b_ct = ContentType.objects.get_for_model(b_type)
                initial['b_terminations_type'] = f'{b_ct.app_label}.{b_ct.model}'

            # TODO: Temporary hack to work around list handling limitations with utils.normalize_querydict()
            for field_name in ('a_terminations', 'b_terminations'):
                if field_name in initial and type(initial[field_name]) is not list:
                    initial[field_name] = [initial[field_name]]

            super().__init__(*args, initial=initial, **kwargs)

            if self.instance and self.instance.pk:
                # Initialize A/B terminations when modifying an existing Cable instance
                if a_type and self.instance.a_terminations and a_ct == ContentType.objects.get_for_model(self.instance.a_terminations[0]):
                    self.initial['a_terminations'] = self.instance.a_terminations
                if b_type and self.instance.b_terminations and b_ct == ContentType.objects.get_for_model(self.instance.b_terminations[0]):
                    self.initial['b_terminations'] = self.instance.b_terminations
            else:
                # Need to clear terminations if swapped type - but need to do it only
                # if not from instance
                if a_type:
                    initial.pop('a_terminations', None)
                if b_type:
                    initial.pop('b_terminations', None)

        def clean(self):
            super().clean()

            # Set the A/B terminations on the Cable instance
            self.instance.a_terminations = self.cleaned_data.get('a_terminations', [])
            self.instance.b_terminations = self.cleaned_data.get('b_terminations', [])

    return _CableForm
