from functools import cached_property

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from dcim.choices import *
from dcim.constants import *
from dcim.fields import WWNField
from dcim.models.base import PortMappingBase
from dcim.models.mixins import InterfaceValidationMixin
from netbox.choices import ColorChoices
from netbox.models import NetBoxModel, OrganizationalModel
from netbox.models.mixins import OwnerMixin
from utilities.fields import ColorField, NaturalOrderingField
from utilities.mptt import TreeManager
from utilities.ordering import naturalize_interface
from utilities.query_functions import CollateAsChar
from utilities.tracking import TrackingModelMixin
from wireless.choices import *
from wireless.utils import get_channel_attr

__all__ = (
    'BaseInterface',
    'CabledObjectModel',
    'ConsolePort',
    'ConsoleServerPort',
    'DeviceBay',
    'FrontPort',
    'Interface',
    'InventoryItem',
    'InventoryItemRole',
    'ModuleBay',
    'PathEndpoint',
    'PortMapping',
    'PowerOutlet',
    'PowerPort',
    'RearPort',
)


class ComponentModel(OwnerMixin, NetBoxModel):
    """
    An abstract model inherited by any model which has a parent Device.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='%(class)ss'
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=64,
        db_collation="natural_sort"
    )
    label = models.CharField(
        verbose_name=_('label'),
        max_length=64,
        blank=True,
        help_text=_('Physical label')
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )

    # Denormalized references replicated from the parent Device
    _site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
    )
    _location = models.ForeignKey(
        to='dcim.Location',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
    )
    _rack = models.ForeignKey(
        to='dcim.Rack',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True
        ordering = ('device', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=('device', 'name'),
                name='%(app_label)s_%(class)s_unique_device_name'
            ),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cache the original Device ID for reference under clean()
        self._original_device = self.__dict__.get('device_id')

    def __str__(self):
        if self.label:
            return f"{self.name} ({self.label})"
        return self.name

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.device
        return objectchange

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)

    @property
    def parent_object(self):
        return self.device


class ModularComponentModel(ComponentModel):
    module = models.ForeignKey(
        to='dcim.Module',
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        blank=True,
        null=True
    )
    inventory_items = GenericRelation(
        to='dcim.InventoryItem',
        content_type_field='component_type',
        object_id_field='component_id'
    )

    class Meta(ComponentModel.Meta):
        abstract = True


class CabledObjectModel(models.Model):
    """
    An abstract model inherited by all models to which a Cable can terminate. Provides the `cable` and `cable_end`
    fields for caching cable associations, as well as `mark_connected` to designate "fake" connections.
    """
    cable = models.ForeignKey(
        to='dcim.Cable',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    cable_end = models.CharField(
        verbose_name=_('cable end'),
        max_length=1,
        choices=CableEndChoices,
        blank=True,
        null=True
    )
    cable_connector = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=(
            MinValueValidator(CABLE_CONNECTOR_MIN),
            MaxValueValidator(CABLE_CONNECTOR_MAX)
        ),
    )
    cable_positions = ArrayField(
        base_field=models.PositiveSmallIntegerField(
            validators=(
                MinValueValidator(CABLE_POSITION_MIN),
                MaxValueValidator(CABLE_POSITION_MAX)
            )
        ),
        blank=True,
        null=True,
    )
    mark_connected = models.BooleanField(
        verbose_name=_('mark connected'),
        default=False,
        help_text=_('Treat as if a cable is connected')
    )

    cable_terminations = GenericRelation(
        to='dcim.CableTermination',
        content_type_field='termination_type',
        object_id_field='termination_id',
        related_query_name='%(class)s',
    )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)

    @property
    def link(self):
        """
        Generic wrapper for a Cable, WirelessLink, or some other relation to a connected termination.
        """
        return self.cable

    @cached_property
    def link_peers(self):
        if self.cable:
            return [
                peer.termination
                for peer in self.cable.terminations.all()
                if peer.cable_end != self.cable_end
            ]
        return []

    @property
    def _occupied(self):
        return bool(self.mark_connected or self.cable_id)

    @property
    def parent_object(self):
        raise NotImplementedError(
            _("{class_name} models must declare a parent_object property").format(class_name=self.__class__.__name__)
        )

    @property
    def opposite_cable_end(self):
        if not self.cable_end:
            return None
        return CableEndChoices.SIDE_A if self.cable_end == CableEndChoices.SIDE_B else CableEndChoices.SIDE_B

    def set_cable_termination(self, termination):
        """Save attributes from the given CableTermination on the terminating object."""
        self.cable = termination.cable
        self.cable_end = termination.cable_end
        self.cable_connector = termination.connector
        self.cable_positions = termination.positions
    set_cable_termination.alters_data = True

    def clear_cable_termination(self, termination):
        """Clear all cable termination attributes from the terminating object."""
        self.cable = None
        self.cable_end = None
        self.cable_connector = None
        self.cable_positions = None
    clear_cable_termination.alters_data = True


class PathEndpoint(models.Model):
    """
    An abstract model inherited by any CabledObjectModel subclass which represents the end of a CablePath; specifically,
    these include ConsolePort, ConsoleServerPort, PowerPort, PowerOutlet, Interface, and PowerFeed.

    `_path` references the CablePath originating from this instance, if any. It is set or cleared by the receivers in
    dcim.signals in response to changes in the cable path, and complements the `origin` GenericForeignKey field on the
    CablePath model. `_path` should not be accessed directly; rather, use the `path` property.

    `connected_endpoints()` is a convenience method for returning the destination of the associated CablePath, if any.
    """

    _path = models.ForeignKey(
        to='dcim.CablePath',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def trace(self):
        origin = self
        path = []

        # Construct the complete path (including e.g. bridged interfaces)
        while origin is not None:
            # Go through the public accessor rather than dereferencing `_path`
            # directly. During cable edits, CablePath rows can be deleted and
            # recreated while this endpoint instance is still in memory.
            cable_path = origin.path
            if cable_path is None:
                break

            path.extend(cable_path.path_objects)

            # If the path ends at a non-connected pass-through port, pad out the link and far-end terminations
            if len(path) % 3 == 1:
                path.extend(([], []))
            # If the path ends at a site or provider network, inject a null "link" to render an attachment
            elif len(path) % 3 == 2:
                path.insert(-1, [])

            # Check for a bridged relationship to continue the trace.
            destinations = cable_path.destinations
            if len(destinations) == 1:
                origin = getattr(destinations[0], 'bridge', None)
            else:
                origin = None

        # Return the path as a list of three-tuples (A termination(s), cable(s), B termination(s))
        return list(zip(*[iter(path)] * 3))

    @property
    def path(self):
        """
        Return this endpoint's current CablePath, if any.

        `_path` is a denormalized reference that is updated from CablePath
        save/delete handlers, including queryset.update() calls on origin
        endpoints. That means an already-instantiated endpoint can briefly hold
        a stale in-memory `_path` relation while the database already points to
        a different CablePath (or to no path at all).

        If the cached relation points to a CablePath that has just been
        deleted, refresh only the `_path` field from the database and retry.
        This keeps the fix cheap and narrowly scoped to the denormalized FK.
        """
        if self._path_id is None:
            return None

        try:
            return self._path
        except ObjectDoesNotExist:
            # Refresh only the denormalized FK instead of the whole model.
            # The expected problem here is in-memory staleness during path
            # rebuilds, not persistent database corruption.
            self.refresh_from_db(fields=['_path'])
            return self._path if self._path_id else None

    @cached_property
    def connected_endpoints(self):
        """
        Caching accessor for the attached CablePath's destinations (if any).

        Always route through `path` so stale in-memory `_path` references are
        repaired before we cache the result for the lifetime of this instance.
        """
        if cable_path := self.path:
            return cable_path.destinations
        return []


#
# Console components
#

class ConsolePort(ModularComponentModel, CabledObjectModel, PathEndpoint, TrackingModelMixin):
    """
    A physical console port within a Device. ConsolePorts connect to ConsoleServerPorts.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True,
        null=True,
        help_text=_('Physical port type')
    )
    speed = models.PositiveIntegerField(
        verbose_name=_('speed'),
        choices=ConsolePortSpeedChoices,
        blank=True,
        null=True,
        help_text=_('Port speed in bits per second')
    )

    clone_fields = ('device', 'module', 'type', 'speed')

    class Meta(ModularComponentModel.Meta):
        verbose_name = _('console port')
        verbose_name_plural = _('console ports')


class ConsoleServerPort(ModularComponentModel, CabledObjectModel, PathEndpoint, TrackingModelMixin):
    """
    A physical port within a Device (typically a designated console server) which provides access to ConsolePorts.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=ConsolePortTypeChoices,
        blank=True,
        null=True,
        help_text=_('Physical port type')
    )
    speed = models.PositiveIntegerField(
        verbose_name=_('speed'),
        choices=ConsolePortSpeedChoices,
        blank=True,
        null=True,
        help_text=_('Port speed in bits per second')
    )

    clone_fields = ('device', 'module', 'type', 'speed')

    class Meta(ModularComponentModel.Meta):
        verbose_name = _('console server port')
        verbose_name_plural = _('console server ports')


#
# Power components
#

class PowerPort(ModularComponentModel, CabledObjectModel, PathEndpoint, TrackingModelMixin):
    """
    A physical power supply (intake) port within a Device. PowerPorts connect to PowerOutlets.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=PowerPortTypeChoices,
        blank=True,
        null=True,
        help_text=_('Physical port type')
    )
    maximum_draw = models.PositiveIntegerField(
        verbose_name=_('maximum draw'),
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text=_("Maximum power draw (watts)")
    )
    allocated_draw = models.PositiveIntegerField(
        verbose_name=_('allocated draw'),
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text=_('Allocated power draw (watts)')
    )

    clone_fields = ('device', 'module', 'maximum_draw', 'allocated_draw')

    class Meta(ModularComponentModel.Meta):
        verbose_name = _('power port')
        verbose_name_plural = _('power ports')

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)

    def get_downstream_powerports(self, leg=None):
        """
        Return a queryset of all PowerPorts connected via cable to a child PowerOutlet. For example, in the topology
        below, PP1.get_downstream_powerports() would return PP2-4.

               ---- PO1 <---> PP2
             /
        PP1 ------- PO2 <---> PP3
             \
               ---- PO3 <---> PP4

        """
        poweroutlets = self.poweroutlets.filter(cable__isnull=False)
        if leg:
            poweroutlets = poweroutlets.filter(feed_leg=leg)
        if not poweroutlets:
            return PowerPort.objects.none()

        q = Q()
        for poweroutlet in poweroutlets:
            q |= Q(
                cable=poweroutlet.cable,
                cable_end=poweroutlet.opposite_cable_end
            )

        return PowerPort.objects.filter(q)

    def get_power_draw(self):
        """
        Return the allocated and maximum power draw (in VA) and child PowerOutlet count for this PowerPort.
        """
        from dcim.models import PowerFeed

        # Calculate aggregate draw of all child power outlets if no numbers have been defined manually
        if self.allocated_draw is None and self.maximum_draw is None:
            utilization = self.get_downstream_powerports().aggregate(
                maximum_draw_total=Sum('maximum_draw'),
                allocated_draw_total=Sum('allocated_draw'),
            )
            ret = {
                'allocated': utilization['allocated_draw_total'] or 0,
                'maximum': utilization['maximum_draw_total'] or 0,
                'outlet_count': self.poweroutlets.count(),
                'legs': [],
            }

            # Calculate per-leg aggregates for three-phase power feeds
            if len(self.link_peers) == 1 and isinstance(self.link_peers[0], PowerFeed) and \
                    self.link_peers[0].phase == PowerFeedPhaseChoices.PHASE_3PHASE:
                for leg, leg_name in PowerOutletFeedLegChoices:
                    utilization = self.get_downstream_powerports(leg=leg).aggregate(
                        maximum_draw_total=Sum('maximum_draw'),
                        allocated_draw_total=Sum('allocated_draw'),
                    )
                    ret['legs'].append({
                        'name': leg_name,
                        'allocated': utilization['allocated_draw_total'] or 0,
                        'maximum': utilization['maximum_draw_total'] or 0,
                        'outlet_count': self.poweroutlets.filter(feed_leg=leg).count(),
                    })

            return ret

        # Default to administratively defined values
        return {
            'allocated': self.allocated_draw or 0,
            'maximum': self.maximum_draw or 0,
            'outlet_count': self.poweroutlets.count(),
            'legs': [],
        }


class PowerOutlet(ModularComponentModel, CabledObjectModel, PathEndpoint, TrackingModelMixin):
    """
    A physical power outlet (output) within a Device which provides power to a PowerPort.
    """
    status = models.CharField(
        verbose_name=_('status'),
        max_length=50,
        choices=PowerOutletStatusChoices,
        default=PowerOutletStatusChoices.STATUS_ENABLED
    )
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=PowerOutletTypeChoices,
        blank=True,
        null=True,
        help_text=_('Physical port type')
    )
    power_port = models.ForeignKey(
        to='dcim.PowerPort',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='poweroutlets'
    )
    feed_leg = models.CharField(
        verbose_name=_('feed leg'),
        max_length=50,
        choices=PowerOutletFeedLegChoices,
        blank=True,
        null=True,
        help_text=_('Phase (for three-phase feeds)')
    )
    color = ColorField(
        verbose_name=_('color'),
        blank=True
    )

    clone_fields = ('device', 'module', 'type', 'power_port', 'feed_leg')

    class Meta(ModularComponentModel.Meta):
        verbose_name = _('power outlet')
        verbose_name_plural = _('power outlets')

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)

    def get_status_color(self):
        return PowerOutletStatusChoices.colors.get(self.status)


#
# Interfaces
#

class BaseInterface(models.Model):
    """
    Abstract base class for fields shared by dcim.Interface and virtualization.VMInterface.
    """
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True
    )
    mtu = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(INTERFACE_MTU_MIN),
            MaxValueValidator(INTERFACE_MTU_MAX)
        ],
        verbose_name=_('MTU')
    )
    mode = models.CharField(
        verbose_name=_('mode'),
        max_length=50,
        choices=InterfaceModeChoices,
        blank=True,
        null=True,
        help_text=_('IEEE 802.1Q tagging strategy')
    )
    parent = models.ForeignKey(
        to='self',
        on_delete=models.RESTRICT,
        related_name='child_interfaces',
        null=True,
        blank=True,
        verbose_name=_('parent interface')
    )
    bridge = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        related_name='bridge_interfaces',
        null=True,
        blank=True,
        verbose_name=_('bridge interface')
    )
    untagged_vlan = models.ForeignKey(
        to='ipam.VLAN',
        on_delete=models.SET_NULL,
        related_name='%(class)ss_as_untagged',
        null=True,
        blank=True,
        verbose_name=_('untagged VLAN')
    )
    tagged_vlans = models.ManyToManyField(
        to='ipam.VLAN',
        related_name='%(class)ss_as_tagged',
        blank=True,
        verbose_name=_('tagged VLANs')
    )
    qinq_svlan = models.ForeignKey(
        to='ipam.VLAN',
        on_delete=models.SET_NULL,
        related_name='%(class)ss_svlan',
        null=True,
        blank=True,
        verbose_name=_('Q-in-Q SVLAN')
    )
    vlan_translation_policy = models.ForeignKey(
        to='ipam.VLANTranslationPolicy',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('VLAN Translation Policy')
    )
    primary_mac_address = models.OneToOneField(
        to='dcim.MACAddress',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name=_('primary MAC address')
    )

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)

    @property
    def tunnel_termination(self):
        return self.tunnel_terminations.first()

    @property
    def count_ipaddresses(self):
        return self.ip_addresses.count()

    @property
    def count_fhrp_groups(self):
        return self.fhrp_group_assignments.count()

    @cached_property
    def mac_address(self):
        if self.primary_mac_address:
            return self.primary_mac_address.mac_address
        return None


class Interface(
    InterfaceValidationMixin,
    ModularComponentModel,
    BaseInterface,
    CabledObjectModel,
    PathEndpoint,
    TrackingModelMixin,
):
    """
    A network interface within a Device. A physical Interface can connect to exactly one other Interface.
    """
    # Override ComponentModel._name to specify naturalize_interface function
    _name = NaturalOrderingField(
        target_field='name',
        naturalize_function=naturalize_interface,
        max_length=100,
        blank=True
    )
    vdcs = models.ManyToManyField(
        to='dcim.VirtualDeviceContext',
        related_name='interfaces'
    )
    lag = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        related_name='member_interfaces',
        null=True,
        blank=True,
        verbose_name=_('parent LAG')
    )
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=InterfaceTypeChoices
    )
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name=_('management only'),
        help_text=_('This interface is used only for out-of-band management')
    )
    speed = models.PositiveBigIntegerField(
        blank=True,
        null=True,
        verbose_name=_('speed (Kbps)')
    )
    duplex = models.CharField(
        verbose_name=_('duplex'),
        max_length=50,
        blank=True,
        null=True,
        choices=InterfaceDuplexChoices
    )
    wwn = WWNField(
        null=True,
        blank=True,
        verbose_name=_('WWN'),
        help_text=_('64-bit World Wide Name')
    )
    rf_role = models.CharField(
        max_length=30,
        choices=WirelessRoleChoices,
        blank=True,
        null=True,
        verbose_name=_('wireless role')
    )
    rf_channel = models.CharField(
        max_length=50,
        choices=WirelessChannelChoices,
        blank=True,
        null=True,
        verbose_name=_('wireless channel')
    )
    rf_channel_frequency = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('channel frequency (MHz)'),
        help_text=_("Populated by selected channel (if set)")
    )
    rf_channel_width = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        blank=True,
        null=True,
        verbose_name=('channel width (MHz)'),
        help_text=_("Populated by selected channel (if set)")
    )
    tx_power = models.SmallIntegerField(
        blank=True,
        null=True,
        validators=(
            MinValueValidator(-40),
            MaxValueValidator(127),
        ),
        verbose_name=_('transmit power (dBm)')
    )
    poe_mode = models.CharField(
        max_length=50,
        choices=InterfacePoEModeChoices,
        blank=True,
        null=True,
        verbose_name=_('PoE mode')
    )
    poe_type = models.CharField(
        max_length=50,
        choices=InterfacePoETypeChoices,
        blank=True,
        null=True,
        verbose_name=_('PoE type')
    )
    wireless_link = models.ForeignKey(
        to='wireless.WirelessLink',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    wireless_lans = models.ManyToManyField(
        to='wireless.WirelessLAN',
        related_name='interfaces',
        blank=True,
        verbose_name=_('wireless LANs')
    )
    vrf = models.ForeignKey(
        to='ipam.VRF',
        on_delete=models.SET_NULL,
        related_name='interfaces',
        null=True,
        blank=True,
        verbose_name=_('VRF')
    )
    ip_addresses = GenericRelation(
        to='ipam.IPAddress',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='interface'
    )
    mac_addresses = GenericRelation(
        to='dcim.MACAddress',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='interface'
    )
    fhrp_group_assignments = GenericRelation(
        to='ipam.FHRPGroupAssignment',
        content_type_field='interface_type',
        object_id_field='interface_id',
        related_query_name='+'
    )
    tunnel_terminations = GenericRelation(
        to='vpn.TunnelTermination',
        content_type_field='termination_type',
        object_id_field='termination_id',
        related_query_name='interface'
    )
    l2vpn_terminations = GenericRelation(
        to='vpn.L2VPNTermination',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='interface',
    )

    clone_fields = (
        'device', 'module', 'parent', 'bridge', 'lag', 'type', 'mgmt_only', 'mtu', 'mode', 'speed', 'duplex', 'rf_role',
        'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'tx_power', 'poe_mode', 'poe_type', 'vrf',
    )

    class Meta(ModularComponentModel.Meta):
        ordering = ('device', CollateAsChar('_name'))
        verbose_name = _('interface')
        verbose_name_plural = _('interfaces')

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def _occupied(self):
        return super()._occupied or bool(self.wireless_link_id)

    @property
    def is_wired(self):
        return not self.is_virtual and not self.is_wireless

    @property
    def is_virtual(self):
        return self.type in VIRTUAL_IFACE_TYPES

    @property
    def is_wireless(self):
        return self.type in WIRELESS_IFACE_TYPES

    @property
    def is_lag(self):
        return self.type == InterfaceTypeChoices.TYPE_LAG

    @property
    def is_bridge(self):
        return self.type == InterfaceTypeChoices.TYPE_BRIDGE

    @property
    def link(self):
        return self.cable or self.wireless_link

    @cached_property
    def link_peers(self):
        if self.cable:
            return super().link_peers
        if self.wireless_link:
            # Return the opposite side of the attached wireless link
            if self.wireless_link.interface_a == self:
                return [self.wireless_link.interface_b]
            return [self.wireless_link.interface_a]
        return []

    @property
    def l2vpn_termination(self):
        return self.l2vpn_terminations.first()

    @cached_property
    def connected_endpoints(self):
        # If this is a virtual interface, return the remote endpoint of the connected
        # virtual circuit, if any.
        if self.is_virtual and hasattr(self, 'virtual_circuit_termination'):
            return self.virtual_circuit_termination.peer_terminations
        return super().connected_endpoints


#
# Pass-through ports
#

class PortMapping(PortMappingBase):
    """
    Maps a FrontPort & position to a RearPort & position.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='port_mappings',
    )
    front_port = models.ForeignKey(
        to='dcim.FrontPort',
        on_delete=models.CASCADE,
        related_name='mappings',
    )
    rear_port = models.ForeignKey(
        to='dcim.RearPort',
        on_delete=models.CASCADE,
        related_name='mappings',
    )

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)


class FrontPort(ModularComponentModel, CabledObjectModel, TrackingModelMixin):
    """
    A pass-through port on the front of a Device.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=PortTypeChoices
    )
    color = ColorField(
        verbose_name=_('color'),
        blank=True
    )
    positions = models.PositiveSmallIntegerField(
        verbose_name=_('positions'),
        default=1,
        validators=[
            MinValueValidator(PORT_POSITION_MIN),
            MaxValueValidator(PORT_POSITION_MAX)
        ],
    )

    clone_fields = ('device', 'type', 'color', 'positions')

    class Meta(ModularComponentModel.Meta):
        constraints = (
            models.UniqueConstraint(
                fields=('device', 'name'),
                name='%(app_label)s_%(class)s_unique_device_name'
            ),
        )
        verbose_name = _('front port')
        verbose_name_plural = _('front ports')

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)


class RearPort(ModularComponentModel, CabledObjectModel, TrackingModelMixin):
    """
    A pass-through port on the rear of a Device.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=PortTypeChoices
    )
    color = ColorField(
        verbose_name=_('color'),
        blank=True
    )
    positions = models.PositiveSmallIntegerField(
        verbose_name=_('positions'),
        default=1,
        validators=[
            MinValueValidator(PORT_POSITION_MIN),
            MaxValueValidator(PORT_POSITION_MAX)
        ],
    )

    clone_fields = ('device', 'type', 'color', 'positions')

    class Meta(ModularComponentModel.Meta):
        verbose_name = _('rear port')
        verbose_name_plural = _('rear ports')

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)


#
# Bays
#

class ModuleBay(ModularComponentModel, TrackingModelMixin, MPTTModel):
    """
    An empty space within a Device which can house a child device
    """
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        editable=False,
        db_index=True
    )
    position = models.CharField(
        verbose_name=_('position'),
        max_length=30,
        blank=True,
        help_text=_('Identifier to reference when renaming installed components')
    )

    objects = TreeManager()

    clone_fields = ('device',)

    class Meta(ModularComponentModel.Meta):
        # Empty tuple triggers Django migration detection for MPTT indexes
        # (see #21016, django-mptt/django-mptt#682)
        indexes = ()
        constraints = (
            models.UniqueConstraint(
                fields=('device', 'module', 'name'),
                name='%(app_label)s_%(class)s_unique_device_module_name'
            ),
        )
        verbose_name = _('module bay')
        verbose_name_plural = _('module bays')

    class MPTTMeta:
        order_insertion_by = ('name',)

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)


class DeviceBay(ComponentModel, TrackingModelMixin):
    """
    An empty space within a Device which can house a child device
    """
    installed_device = models.OneToOneField(
        to='dcim.Device',
        on_delete=models.SET_NULL,
        related_name='parent_bay',
        blank=True,
        null=True
    )

    clone_fields = ('device',)

    class Meta(ComponentModel.Meta):
        verbose_name = _('device bay')
        verbose_name_plural = _('device bays')

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)


#
# Inventory items
#


class InventoryItemRole(OrganizationalModel):
    """
    Inventory items may optionally be assigned a functional role.
    """
    color = ColorField(
        verbose_name=_('color'),
        default=ColorChoices.COLOR_GREY
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('inventory item role')
        verbose_name_plural = _('inventory item roles')


class InventoryItem(MPTTModel, ComponentModel, TrackingModelMixin):
    """
    An InventoryItem represents a serialized piece of hardware within a Device, such as a line card or power supply.
    InventoryItems are used only for inventory purposes.
    """
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='child_items',
        blank=True,
        null=True,
        db_index=True
    )
    component_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    component_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    component = GenericForeignKey(
        ct_field='component_type',
        fk_field='component_id'
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=50,
        choices=InventoryItemStatusChoices,
        default=InventoryItemStatusChoices.STATUS_ACTIVE
    )
    role = models.ForeignKey(
        to='dcim.InventoryItemRole',
        on_delete=models.PROTECT,
        related_name='inventory_items',
        blank=True,
        null=True
    )
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='inventory_items',
        blank=True,
        null=True
    )
    part_id = models.CharField(
        max_length=50,
        verbose_name=_('part ID'),
        blank=True,
        help_text=_('Manufacturer-assigned part identifier')
    )
    serial = models.CharField(
        max_length=50,
        verbose_name=_('serial number'),
        blank=True
    )
    asset_tag = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_('asset tag'),
        help_text=_('A unique tag used to identify this item')
    )
    discovered = models.BooleanField(
        verbose_name=_('discovered'),
        default=False,
        help_text=_('This item was automatically discovered')
    )

    objects = TreeManager()

    clone_fields = ('device', 'parent', 'role', 'manufacturer', 'status', 'part_id')

    class Meta:
        ordering = ('device__id', 'parent__id', 'name')
        indexes = (
            models.Index(fields=('component_type', 'component_id')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('device', 'parent', 'name'),
                name='%(app_label)s_%(class)s_unique_device_parent_name'
            ),
        )
        verbose_name = _('inventory item')
        verbose_name_plural = _('inventory items')

    def clean(self):
        super().clean()

        if not self._state.adding and self.component and self.component.device != self.device:
            self.component = None

        from netbox.validators import validator_registry
        validator_registry.validate(self)

    def get_status_color(self):
        return InventoryItemStatusChoices.colors.get(self.status)
