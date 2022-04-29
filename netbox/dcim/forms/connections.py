from circuits.models import Circuit, CircuitTermination, Provider
from dcim.models import *
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.forms import DynamicModelChoiceField, DynamicModelMultipleChoiceField, StaticSelect

__all__ = (
    'ConnectCableToCircuitTerminationForm',
    'ConnectCableToConsolePortForm',
    'ConnectCableToConsoleServerPortForm',
    'ConnectCableToFrontPortForm',
    'ConnectCableToInterfaceForm',
    'ConnectCableToPowerFeedForm',
    'ConnectCableToPowerPortForm',
    'ConnectCableToPowerOutletForm',
    'ConnectCableToRearPortForm',
)


class BaseCableConnectionForm(TenancyForm, NetBoxModelForm):
    a_terminations = DynamicModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        label='Name',
        disabled_indicator='_occupied'
    )
    b_terminations = DynamicModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        label='Name',
        disabled_indicator='_occupied'
    )

    def save(self, commit=True):
        instance = super().save(commit=commit)

        # Create CableTermination instances
        terminations = []
        terminations.extend([
            CableTermination(cable=instance, cable_end='A', termination=termination)
            for termination in self.cleaned_data['a_terminations']
        ])
        terminations.extend([
            CableTermination(cable=instance, cable_end='B', termination=termination)
            for termination in self.cleaned_data['b_terminations']
        ])

        if commit:
            CableTermination.objects.bulk_create(terminations)
        else:
            instance.terminations = [
                *self.cleaned_data['a_terminations'],
                *self.cleaned_data['b_terminations'],
            ]

        return instance


class ConnectCableToDeviceForm(BaseCableConnectionForm):
    """
    Base form for connecting a Cable to a Device component
    """
    termination_b_region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        label='Region',
        required=False,
        initial_params={
            'sites': '$termination_b_site'
        }
    )
    termination_b_sitegroup = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        label='Site group',
        required=False,
        initial_params={
            'sites': '$termination_b_site'
        }
    )
    termination_b_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Site',
        required=False,
        query_params={
            'region_id': '$termination_b_region',
            'group_id': '$termination_b_sitegroup',
        }
    )
    termination_b_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        label='Location',
        required=False,
        null_option='None',
        query_params={
            'site_id': '$termination_b_site'
        }
    )
    termination_b_rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        label='Rack',
        required=False,
        null_option='None',
        query_params={
            'site_id': '$termination_b_site',
            'location_id': '$termination_b_location',
        }
    )
    termination_b_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        label='Device',
        required=False,
        query_params={
            'site_id': '$termination_b_site',
            'location_id': '$termination_b_location',
            'rack_id': '$termination_b_rack',
        }
    )

    class Meta:
        model = Cable
        fields = [
            'a_terminations', 'termination_b_region', 'termination_b_sitegroup', 'termination_b_site',
            'termination_b_rack', 'termination_b_device', 'b_terminations', 'type', 'status', 'tenant_group',
            'tenant', 'label', 'color', 'length', 'length_unit', 'tags',
        ]
        widgets = {
            'status': StaticSelect,
            'type': StaticSelect,
            'length_unit': StaticSelect,
        }


class ConnectCableToConsolePortForm(ConnectCableToDeviceForm):
    b_terminations = DynamicModelMultipleChoiceField(
        queryset=ConsolePort.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToConsoleServerPortForm(ConnectCableToDeviceForm):
    b_terminations = DynamicModelMultipleChoiceField(
        queryset=ConsoleServerPort.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToPowerPortForm(ConnectCableToDeviceForm):
    b_terminations = DynamicModelMultipleChoiceField(
        queryset=PowerPort.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToPowerOutletForm(ConnectCableToDeviceForm):
    b_terminations = DynamicModelMultipleChoiceField(
        queryset=PowerOutlet.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToInterfaceForm(ConnectCableToDeviceForm):
    b_terminations = DynamicModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device',
            'kind': 'physical',
        }
    )


class ConnectCableToFrontPortForm(ConnectCableToDeviceForm):
    b_terminations = DynamicModelMultipleChoiceField(
        queryset=FrontPort.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToRearPortForm(ConnectCableToDeviceForm):
    b_terminations = DynamicModelMultipleChoiceField(
        queryset=RearPort.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'device_id': '$termination_b_device'
        }
    )


class ConnectCableToCircuitTerminationForm(BaseCableConnectionForm):
    termination_b_provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        label='Provider',
        required=False
    )
    termination_b_region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        label='Region',
        required=False,
        initial_params={
            'sites': '$termination_b_site'
        }
    )
    termination_b_sitegroup = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        label='Site group',
        required=False,
        initial_params={
            'sites': '$termination_b_site'
        }
    )
    termination_b_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Site',
        required=False,
        query_params={
            'region_id': '$termination_b_region',
            'group_id': '$termination_b_sitegroup',
        }
    )
    termination_b_circuit = DynamicModelChoiceField(
        queryset=Circuit.objects.all(),
        label='Circuit',
        query_params={
            'provider_id': '$termination_b_provider',
            'site_id': '$termination_b_site',
        }
    )
    b_terminations = DynamicModelMultipleChoiceField(
        queryset=CircuitTermination.objects.all(),
        label='Side',
        disabled_indicator='_occupied',
        query_params={
            'circuit_id': '$termination_b_circuit'
        }
    )

    class Meta(ConnectCableToDeviceForm.Meta):
        fields = [
            'a_terminations', 'termination_b_provider', 'termination_b_region', 'termination_b_sitegroup',
            'termination_b_site', 'termination_b_circuit', 'b_terminations', 'type', 'status', 'tenant_group',
            'tenant', 'label', 'color', 'length', 'length_unit', 'tags',
        ]


class ConnectCableToPowerFeedForm(BaseCableConnectionForm):
    termination_b_region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        label='Region',
        required=False,
        initial_params={
            'sites': '$termination_b_site'
        }
    )
    termination_b_sitegroup = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        label='Site group',
        required=False,
        initial_params={
            'sites': '$termination_b_site'
        }
    )
    termination_b_site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        label='Site',
        required=False,
        query_params={
            'region_id': '$termination_b_region',
            'group_id': '$termination_b_sitegroup',
        }
    )
    termination_b_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        label='Location',
        required=False,
        query_params={
            'site_id': '$termination_b_site'
        }
    )
    termination_b_powerpanel = DynamicModelChoiceField(
        queryset=PowerPanel.objects.all(),
        label='Power Panel',
        required=False,
        query_params={
            'site_id': '$termination_b_site',
            'location_id': '$termination_b_location',
        }
    )
    b_terminations = DynamicModelMultipleChoiceField(
        queryset=PowerFeed.objects.all(),
        label='Name',
        disabled_indicator='_occupied',
        query_params={
            'power_panel_id': '$termination_b_powerpanel'
        }
    )

    class Meta(ConnectCableToDeviceForm.Meta):
        fields = [
            'a_terminations', 'termination_b_region', 'termination_b_sitegroup', 'termination_b_site',
            'termination_b_location', 'termination_b_powerpanel', 'b_terminations', 'type', 'status', 'tenant_group',
            'tenant', 'label', 'color', 'length', 'length_unit', 'tags',
        ]
