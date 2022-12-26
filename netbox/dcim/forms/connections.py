from django import forms
from django.utils.translation import gettext as _

from circuits.models import Circuit, CircuitTermination, Provider
from dcim.models import *
from utilities.forms import DynamicModelChoiceField, DynamicModelMultipleChoiceField
from .model_forms import CableForm


def get_cable_form(a_type, b_type):

    class FormMetaclass(forms.models.ModelFormMetaclass):

        def __new__(mcs, name, bases, attrs):

            for cable_end, term_cls in (('a', a_type), ('b', b_type)):

                attrs[f'termination_{cable_end}_region'] = DynamicModelChoiceField(
                    queryset=Region.objects.all(),
                    label=_('Region'),
                    required=False,
                    initial_params={
                        'sites': f'$termination_{cable_end}_site'
                    }
                )
                attrs[f'termination_{cable_end}_sitegroup'] = DynamicModelChoiceField(
                    queryset=SiteGroup.objects.all(),
                    label=_('Site group'),
                    required=False,
                    initial_params={
                        'sites': f'$termination_{cable_end}_site'
                    }
                )
                attrs[f'termination_{cable_end}_site'] = DynamicModelChoiceField(
                    queryset=Site.objects.all(),
                    label=_('Site'),
                    required=False,
                    query_params={
                        'region_id': f'$termination_{cable_end}_region',
                        'group_id': f'$termination_{cable_end}_sitegroup',
                    }
                )
                attrs[f'termination_{cable_end}_location'] = DynamicModelChoiceField(
                    queryset=Location.objects.all(),
                    label=_('Location'),
                    required=False,
                    null_option='None',
                    query_params={
                        'site_id': f'$termination_{cable_end}_site'
                    }
                )

                # Device component
                if hasattr(term_cls, 'device'):

                    attrs[f'termination_{cable_end}_rack'] = DynamicModelChoiceField(
                        queryset=Rack.objects.all(),
                        label=_('Rack'),
                        required=False,
                        null_option='None',
                        initial_params={
                            'devices': f'$termination_{cable_end}_device'
                        },
                        query_params={
                            'site_id': f'$termination_{cable_end}_site',
                            'location_id': f'$termination_{cable_end}_location',
                        }
                    )
                    attrs[f'termination_{cable_end}_device'] = DynamicModelChoiceField(
                        queryset=Device.objects.all(),
                        label=_('Device'),
                        required=False,
                        initial_params={
                            f'{term_cls._meta.model_name}s__in': f'${cable_end}_terminations'
                        },
                        query_params={
                            'site_id': f'$termination_{cable_end}_site',
                            'location_id': f'$termination_{cable_end}_location',
                            'rack_id': f'$termination_{cable_end}_rack',
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
                        initial_params={
                            'powerfeeds__in': f'${cable_end}_terminations'
                        },
                        query_params={
                            'site_id': f'$termination_{cable_end}_site',
                            'location_id': f'$termination_{cable_end}_location',
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

                    attrs[f'termination_{cable_end}_provider'] = DynamicModelChoiceField(
                        queryset=Provider.objects.all(),
                        label=_('Provider'),
                        initial_params={
                            'circuits': f'$termination_{cable_end}_circuit'
                        },
                        required=False
                    )
                    attrs[f'termination_{cable_end}_circuit'] = DynamicModelChoiceField(
                        queryset=Circuit.objects.all(),
                        label=_('Circuit'),
                        initial_params={
                            'terminations__in': f'${cable_end}_terminations'
                        },
                        query_params={
                            'provider_id': f'$termination_{cable_end}_provider',
                            'site_id': f'$termination_{cable_end}_site',
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
