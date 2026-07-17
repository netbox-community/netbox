from functools import cached_property

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GistIndex
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from dcim.choices import *
from dcim.constants import *
from dcim.fields import WWNField
from dcim.models.base import PortMappingBase
from dcim.models.mixins import DiameterMixin, InterfaceValidationMixin, MaximumFlowMixin
from netbox.choices import ColorChoices
from netbox.models import NetBoxModel, OrganizationalModel
from netbox.models.features import ChangeLoggingMixin
from netbox.models.ltree import LtreeManager, LtreeModel, SortPathField
from netbox.models.mixins import OwnerMixin
from utilities.fields import ColorField, NaturalOrderingField
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
    'CoolingIntake',
    'CoolingOutflow',
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

        # Check list of Modules that allow device field to be changed
        if (type(self) not in [InventoryItem]) and (self.pk is not None) and (self._original_device != self.device_id):
            raise ValidationError({
                "device": _("Components cannot be moved to a different device.")
            })

    def save(self, *args, **kwargs):
        # Save denormalized references
        self._site = self.device.site
        self._location = self.device.location
        self._rack = self.device.rack

        super().save(*args, **kwargs)

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

        if self.cable:
            if not self.cable_end:
                raise ValidationError({
                    "cable_end": _("Must specify cable end (A or B) when attaching a cable.")
                })
            if self.cable_connector and not self.cable_positions:
                raise ValidationError({
                    "cable_positions": _("Must specify position(s) when specifying a cable connector.")
                })
            if self.cable_positions and not self.cable_connector:
                raise ValidationError({
                    "cable_positions": _("Cable positions cannot be set without a cable connector.")
                })
            if self.mark_connected:
                raise ValidationError({
                    "mark_connected": _("Cannot mark as connected with a cable attached.")
                })
        else:
            if self.cable_end:
                raise ValidationError({
                    "cable_end": _("Cable end must not be set without a cable.")
                })
            if self.cable_connector:
                raise ValidationError({
                    "cable_connector": _("Cable connector must not be set without a cable.")
                })
            if self.cable_positions:
                raise ValidationError({
                    "cable_positions": _("Cable termination positions must not be set without a cable.")
                })

    @property
    def link(self):
        """
        Generic wrapper for a Cable, WirelessLink, or some other relation to a connected termination.
        """
        return self.cable

    @cached_property
    def link_peers(self):
        if not self.cable:
            return []

        if self.cable.profile:
            return self._get_profile_link_peers()

        return [peer.termination for peer in self.cable.terminations.all() if peer.cable_end != self.cable_end]

    def _get_profile_link_peers(self):
        if self.cable_end is None or self.cable_connector is None or not self.cable_positions:
            return []

        profile = self.cable.profile_class()
        peer_terminations = {
            (peer.connector, position): peer.termination
            for peer in self.cable.terminations.all()
            if peer.cable_end == self.opposite_cable_end and peer.connector is not None
            for position in peer.positions or []
        }
        link_peers = []

        for position in self.cable_positions:
            mapped_position = profile.get_mapped_position(self.cable_end, self.cable_connector, position)
            if mapped_position is None:
                continue

            peer = peer_terminations.get(mapped_position)
            if peer is not None and peer not in link_peers:
                link_peers.append(peer)

        return link_peers

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

        Two stale cases are repaired by refreshing only the `_path` field
        from the database:

        1. The endpoint is linked (by cable or wireless link) but `_path` is
           unset, because the instance was loaded before its path was traced
           (e.g. while queued for event serialization during link creation).
        2. The cached relation points to a CablePath row that has just been
           deleted.

        Repairing case 1 costs one query per access for a linked endpoint
        whose path is genuinely absent in the database. That state is
        transient outside of tracing failures, so no result caching is
        attempted here.
        """
        if self._path_id is None:
            has_link = self.cable_id is not None or getattr(self, 'wireless_link_id', None) is not None
            if self.pk and has_link:
                self.refresh_from_db(fields=['_path'])

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

        if self.maximum_draw is not None and self.allocated_draw is not None:
            if self.allocated_draw > self.maximum_draw:
                raise ValidationError({
                    'allocated_draw': _(
                        "Allocated draw cannot exceed the maximum draw ({maximum_draw}W)."
                    ).format(maximum_draw=self.maximum_draw)
                })

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

    def get_power_draw(self, _seen=None):
        """
        Return the allocated and maximum power draw (in VA) and child PowerOutlet count for this PowerPort.
        """
        from dcim.models import PowerFeed

        # Calculate aggregate draw of all child power outlets if no numbers have been defined manually
        if self.allocated_draw is None and self.maximum_draw is None:

            def _aggregate(powerports, seen):
                # Recursively resolve the draw for each downstream PowerPort. Using the per-port value
                # (rather than a SQL aggregate over allocated_draw/maximum_draw) allows the draw to
                # propagate through intermediate auto-mode PowerPorts, e.g. PDU-internal fuse chains.
                # `seen` tracks visited PowerPorts to prevent infinite recursion if the topology
                # happens to form a cycle.
                allocated_total = 0
                maximum_total = 0
                for powerport in powerports:
                    if powerport.pk in seen:
                        continue
                    seen.add(powerport.pk)
                    draw = powerport.get_power_draw(_seen=seen)
                    allocated_total += draw['allocated']
                    maximum_total += draw['maximum']
                return allocated_total, maximum_total

            # Seed each _aggregate() call with a fresh copy of the inherited visited set so the full
            # and per-leg aggregations are independent. Otherwise, ports visited during the full
            # aggregation would be skipped during the per-leg passes.
            base_seen = set(_seen) if _seen else set()
            base_seen.add(self.pk)

            allocated, maximum = _aggregate(self.get_downstream_powerports(), set(base_seen))
            ret = {
                'allocated': allocated,
                'maximum': maximum,
                'outlet_count': self.poweroutlets.count(),
                'legs': [],
            }

            # Calculate per-leg aggregates for three-phase power feeds
            if len(self.link_peers) == 1 and isinstance(self.link_peers[0], PowerFeed) and \
                    self.link_peers[0].phase == PowerFeedPhaseChoices.PHASE_3PHASE:
                for leg, leg_name in PowerOutletFeedLegChoices:
                    leg_allocated, leg_maximum = _aggregate(
                        self.get_downstream_powerports(leg=leg), set(base_seen)
                    )
                    ret['legs'].append({
                        'name': leg_name,
                        'allocated': leg_allocated,
                        'maximum': leg_maximum,
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

        # Validate power port assignment
        if self.power_port and self.power_port.device != self.device:
            raise ValidationError(
                _("Parent power port ({power_port}) must belong to the same device").format(power_port=self.power_port)
            )

    def get_status_color(self):
        return PowerOutletStatusChoices.colors.get(self.status)


#
# Cooling components
#

class CoolingIntake(DiameterMixin, MaximumFlowMixin, ModularComponentModel, TrackingModelMixin):
    """
    A coolant intake/outlet port within a Device (e.g. a server cold-plate inlet or CDU intake). A
    CoolingIntake is supplied by an upstream CoolingOutflow or CoolingFeed.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=CoolingConnectorTypeChoices,
        blank=True,
        null=True,
        help_text=_('Physical connector type')
    )
    # diameter, diameter_unit, _abs_diameter provided by DiameterMixin
    # maximum_flow, maximum_flow_unit, _abs_maximum_flow provided by MaximumFlowMixin
    cooling_outflow = models.ForeignKey(
        to='dcim.CoolingOutflow',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='cooling_intakes',
        help_text=_('The upstream cooling outflow supplying this intake')
    )
    cooling_feed = models.ForeignKey(
        to='dcim.CoolingFeed',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='cooling_intakes',
        help_text=_('The upstream cooling feed supplying this port')
    )

    clone_fields = (
        'device', 'module', 'type', 'diameter', 'diameter_unit', 'maximum_flow',
        'maximum_flow_unit',
    )

    class Meta(ModularComponentModel.Meta):
        verbose_name = _('cooling intake')
        verbose_name_plural = _('cooling intakes')

    def clean(self):
        super().clean()

        # An intake may be supplied by either a cooling outflow or a cooling feed, but not both
        if self.cooling_outflow and self.cooling_feed:
            raise ValidationError(
                _("A cooling intake cannot be supplied by both a cooling outflow and a cooling feed.")
            )


class CoolingOutflow(DiameterMixin, ModularComponentModel, TrackingModelMixin):
    """
    A coolant outlet within a Device (e.g. a CDU or manifold outlet) which supplies one or more
    CoolingIntakes (referenced via CoolingIntake.cooling_outflow).
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=CoolingConnectorTypeChoices,
        blank=True,
        null=True,
        help_text=_('Physical connector type')
    )
    # diameter, diameter_unit, _abs_diameter provided by DiameterMixin
    cooling_intake = models.ForeignKey(
        to='dcim.CoolingIntake',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='coolingoutflows'
    )

    clone_fields = ('device', 'module', 'type', 'diameter', 'diameter_unit', 'cooling_intake')

    class Meta(ModularComponentModel.Meta):
        verbose_name = _('cooling outflow')
        verbose_name_plural = _('cooling outflows')

    def clean(self):
        super().clean()

        # Validate cooling intake assignment
        if self.cooling_intake and self.cooling_intake.device != self.device:
            raise ValidationError(
                _("Parent cooling intake ({cooling_intake}) must belong to the same device").format(
                    cooling_intake=self.cooling_intake)
            )


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

        # SVLAN can be defined only for Q-in-Q interfaces
        if self.qinq_svlan and self.mode != InterfaceModeChoices.MODE_Q_IN_Q:
            raise ValidationError({
                'qinq_svlan': _("Only Q-in-Q interfaces may specify a service VLAN.")
            })

        # Check that the primary MAC address (if any) is assigned to this interface
        if (
                self.primary_mac_address and
                self.primary_mac_address.assigned_object is not None and
                self.primary_mac_address.assigned_object != self
        ):
            raise ValidationError({
                'primary_mac_address': _(
                    "MAC address {mac_address} is assigned to a different interface ({interface})."
                ).format(
                    mac_address=self.primary_mac_address,
                    interface=self.primary_mac_address.assigned_object,
                )
            })

    def save(self, *args, **kwargs):

        # Remove untagged VLAN assignment for non-802.1Q interfaces
        if not self.mode:
            self.untagged_vlan = None

        # Only "tagged" interfaces may have tagged VLANs assigned. ("tagged all" implies all VLANs are assigned.)
        if not self._state.adding and self.mode != InterfaceModeChoices.MODE_TAGGED:
            self.tagged_vlans.clear()

        return super().save(*args, **kwargs)

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
    channels = models.PositiveSmallIntegerField(
        verbose_name=_('channels'),
        blank=True,
        null=True,
        validators=(
            MinValueValidator(INTERFACE_CHANNELS_MIN),
            MaxValueValidator(INTERFACE_CHANNELS_MAX)
        ),
        help_text=_('The number of channels into which this interface is channelized')
    )
    channel_id = models.PositiveSmallIntegerField(
        verbose_name=_('channel ID'),
        blank=True,
        null=True,
        validators=(
            MinValueValidator(INTERFACE_CHANNELS_MIN),
            MaxValueValidator(INTERFACE_CHANNELS_MAX)
        ),
        help_text=_('The channel on the parent interface to which this subinterface is bound')
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
        max_digits=8,
        decimal_places=3,
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
        'device', 'module', 'parent', 'bridge', 'lag', 'type', 'channels', 'mgmt_only', 'mtu', 'mode', 'speed',
        'duplex', 'rf_role', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'tx_power', 'poe_mode',
        'poe_type', 'vrf',
    )

    class Meta(ModularComponentModel.Meta):
        ordering = ('device', CollateAsChar('_name'))
        verbose_name = _('interface')
        verbose_name_plural = _('interfaces')
        constraints = (
            *ModularComponentModel.Meta.constraints,
            models.UniqueConstraint(
                fields=('parent', 'channel_id'),
                name='%(app_label)s_%(class)s_unique_parent_channel_id'
            ),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cache channelization-related fields so post-save signal handlers can detect changes which require rebuilding
        # cable paths (channelization does not involve modifying the Cable itself, so the cable signals do not fire).
        # _original_channels is additionally used by InterfaceValidationMixin.clean() to detect a channel-count
        # reduction that would orphan a bound subinterface.
        self._original_channels = self.__dict__.get('channels')
        self._original_channel_id = self.__dict__.get('channel_id')
        self._original_parent_id = self.__dict__.get('parent_id')

    def clean(self):
        super().clean()

        # Virtual Interfaces cannot have a Cable attached
        if self.is_virtual and self.cable:
            raise ValidationError({
                'type': _("{display_type} interfaces cannot have a cable attached.").format(
                    display_type=self.get_type_display()
                )
            })

        # Virtual Interfaces cannot be marked as connected
        if self.is_virtual and self.mark_connected:
            raise ValidationError({
                'mark_connected': _("{display_type} interfaces cannot be marked as connected.".format(
                    display_type=self.get_type_display())
                )
            })

        # Parent validation (self-reference and interface-type restrictions are enforced by InterfaceValidationMixin)

        # An interface's parent must belong to the same device or virtual chassis
        if self.parent and self.parent.device != self.device:
            if self.device.virtual_chassis is None:
                raise ValidationError({
                    'parent': _(
                        "The selected parent interface ({interface}) belongs to a different device ({device})"
                    ).format(interface=self.parent, device=self.parent.device)
                })
            if self.parent.device.virtual_chassis != self.device.virtual_chassis:
                raise ValidationError({
                    'parent': _(
                        "The selected parent interface ({interface}) belongs to {device}, which is not part of "
                        "virtual chassis {virtual_chassis}."
                    ).format(
                        interface=self.parent,
                        device=self.parent.device,
                        virtual_chassis=self.device.virtual_chassis
                    )
                })

        # Bridge validation

        # A bridged interface belongs to the same device or virtual chassis
        if self.bridge and self.bridge.device != self.device:
            if self.device.virtual_chassis is None:
                raise ValidationError({
                    'bridge': _(
                        "The selected bridge interface ({bridge}) belongs to a different device ({device})."
                    ).format(bridge=self.bridge, device=self.bridge.device)
                })
            if self.bridge.device.virtual_chassis != self.device.virtual_chassis:
                raise ValidationError({
                    'bridge': _(
                        "The selected bridge interface ({interface}) belongs to {device}, which is not part of virtual "
                        "chassis {virtual_chassis}."
                    ).format(
                        interface=self.bridge, device=self.bridge.device, virtual_chassis=self.device.virtual_chassis
                    )
                })

        # LAG validation

        # A virtual interface cannot have a parent LAG
        if self.type == InterfaceTypeChoices.TYPE_VIRTUAL and self.lag is not None:
            raise ValidationError({'lag': _("Virtual interfaces cannot have a parent LAG interface.")})

        # A LAG interface cannot be its own parent
        if self.pk and self.lag_id == self.pk:
            raise ValidationError({'lag': _("A LAG interface cannot be its own parent.")})

        # An interface's LAG must belong to the same device or virtual chassis
        if self.lag and self.lag.device != self.device:
            if self.device.virtual_chassis is None:
                raise ValidationError({
                    'lag': _(
                        "The selected LAG interface ({lag}) belongs to a different device ({device})."
                    ).format(lag=self.lag, device=self.lag.device)
                })
            if self.lag.device.virtual_chassis != self.device.virtual_chassis:
                raise ValidationError({
                    'lag': _(
                        "The selected LAG interface ({lag}) belongs to {device}, which is not part of virtual chassis "
                        "{virtual_chassis}.".format(
                            lag=self.lag, device=self.lag.device, virtual_chassis=self.device.virtual_chassis)
                    )
                })

        # Wireless validation

        # RF channel may only be set for wireless interfaces
        if self.rf_channel and not self.is_wireless:
            raise ValidationError({'rf_channel': _("Channel may be set only on wireless interfaces.")})

        # Validate channel frequency against interface type and selected channel (if any)
        if self.rf_channel_frequency:
            if not self.is_wireless:
                raise ValidationError({
                    'rf_channel_frequency': _("Channel frequency may be set only on wireless interfaces."),
                })
            if self.rf_channel and self.rf_channel_frequency != get_channel_attr(self.rf_channel, 'frequency'):
                raise ValidationError({
                    'rf_channel_frequency': _("Cannot specify custom frequency with channel selected."),
                })

        # Validate channel width against interface type and selected channel (if any)
        if self.rf_channel_width:
            if not self.is_wireless:
                raise ValidationError({'rf_channel_width': _("Channel width may be set only on wireless interfaces.")})
            if self.rf_channel and self.rf_channel_width != get_channel_attr(self.rf_channel, 'width'):
                raise ValidationError({'rf_channel_width': _("Cannot specify custom width with channel selected.")})

        # VLAN validation
        if not self.mode and self.untagged_vlan:
            raise ValidationError({'untagged_vlan': _("Interface mode does not support an untagged vlan.")})

        # Validate untagged VLAN
        if self.untagged_vlan and self.untagged_vlan.site not in [self.device.site, None]:
            raise ValidationError({
                'untagged_vlan': _(
                    "The untagged VLAN ({untagged_vlan}) must belong to the same site as the interface's parent "
                    "device, or it must be global."
                ).format(untagged_vlan=self.untagged_vlan)
            })

    def save(self, *args, **kwargs):

        # Set absolute channel attributes from selected options
        if self.rf_channel and not self.rf_channel_frequency:
            self.rf_channel_frequency = get_channel_attr(self.rf_channel, 'frequency')
        if self.rf_channel and not self.rf_channel_width:
            self.rf_channel_width = get_channel_attr(self.rf_channel, 'width')

        super().save(*args, **kwargs)

    @property
    def _occupied(self):
        return super()._occupied or bool(self.wireless_link_id)

    @property
    def is_wired(self):
        # Excludes virtual, wireless, and channel-type interfaces (channel subinterfaces derive their cable from the
        # channelized parent and cannot be cabled directly).
        return self.type not in NONCONNECTABLE_IFACE_TYPES

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
    def is_channel(self):
        return self.type == InterfaceTypeChoices.TYPE_CHANNEL

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

    def set_cable_termination(self, termination):
        super().set_cable_termination(termination)

        # A channelized interface carries no path of its own; instead, its cable is mirrored onto each channel
        # subinterface (occupying a single position of the shared connector) so that each channel traces independently.
        if self.channels:
            self.propagate_channel_cables()

    def clear_cable_termination(self, termination):
        super().clear_cable_termination(termination)

        if self.channels:
            self.clear_channel_cables()

    def propagate_channel_cables(self):
        """
        Mirror this channelized interface's cable attributes onto each of its channel subinterfaces, restricting each
        child to the single connector position identified by its channel_id. Only profiled cables map connector
        positions to channels; a positionless (unprofiled) cable carries no per-channel path, so nothing is mirrored.
        """
        # Only a profiled cable defines the connector positions that channels map onto; without one, clear any
        # previously-mirrored attributes rather than propagate an unusable cable reference.
        if not (self.cable and self.cable.profile):
            self.clear_channel_cables()
            return

        # Mirror via bulk_update() to issue a single UPDATE and, crucially, to bypass the post_save signal — a
        # per-child save() would re-trigger update_channelized_cable_paths() and recurse indefinitely.
        children = list(self.child_interfaces.filter(channel_id__isnull=False))
        for child in children:
            child.cable = self.cable
            child.cable_end = self.cable_end
            child.cable_connector = self.cable_connector
            child.cable_positions = [child.channel_id]
        type(self).objects.bulk_update(
            children, ['cable', 'cable_end', 'cable_connector', 'cable_positions']
        )

    def clear_channel_cables(self):
        """
        Clear the mirrored cable attributes from this channelized interface's channel subinterfaces.
        """
        # A queryset update() clears every child in a single query and bypasses the post_save signal (see above).
        # cable_end is cleared to '' to match the convention used elsewhere when nullifying a termination (see
        # nullify_connected_endpoints() and update_channelized_cable_paths() in dcim.signals).
        self.child_interfaces.filter(channel_id__isnull=False).update(
            cable=None,
            cable_end='',
            cable_connector=None,
            cable_positions=None,
        )


#
# Pass-through ports
#

class PortMapping(ChangeLoggingMixin, PortMappingBase):
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

    class Meta(PortMappingBase.Meta):
        # Inherit the unique constraints from PortMappingBase.Meta.
        pass

    def clean(self):
        super().clean()

        # Both ports must belong to the same device
        if self.front_port.device_id != self.rear_port.device_id:
            raise ValidationError({
                "rear_port": _("Rear port ({rear_port}) must belong to the same device").format(
                    rear_port=self.rear_port
                )
            })

    def save(self, *args, **kwargs):
        # Associate the mapping with the parent Device
        self.device = self.front_port.device
        super().save(*args, **kwargs)


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

        # Check that positions is greater than or equal to the number of associated RearPorts
        if not self._state.adding:
            mapping_count = self.mappings.count()
            if self.positions < mapping_count:
                raise ValidationError({
                    "positions": _(
                        "The number of positions cannot be less than the number of mapped rear ports ({count})"
                    ).format(count=mapping_count)
                })


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

        # Check that positions count is greater than or equal to the number of associated FrontPorts
        if not self._state.adding:
            mapping_count = self.mappings.count()
            if self.positions < mapping_count:
                raise ValidationError({
                    "positions": _(
                        "The number of positions cannot be less than the number of mapped front ports "
                        "({count})"
                    ).format(count=mapping_count)
                })


#
# Bays
#

class ModuleBay(ModularComponentModel, TrackingModelMixin, LtreeModel):
    """
    An empty space within a Device which can house a child device
    """
    parent = models.ForeignKey(
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
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True,
    )
    module_bay_types = models.ManyToManyField(
        to='dcim.ModuleBayType',
        related_name='module_bays',
        blank=True,
        verbose_name=_('module bay types'),
        help_text=_('Types of modules that can be installed in this bay (empty = unconstrained)'),
    )
    # sort_path inherits `name`'s natural_sort collation automatically (LtreeModelBase),
    # so ORDER BY sort_path sorts siblings naturally (Slot 0..Slot 13) — as MPTT's
    # order_insertion_by=('name',) did — rather than lexicographically.
    sort_path = SortPathField(
        editable=False,
        blank=True,
        default='',
    )

    clone_fields = ('device', 'enabled')

    objects = LtreeManager()

    class Meta(ModularComponentModel.Meta):
        # Order by sort_path alone (not device-first), reproducing the MPTT
        # ModuleBayManager's ('_root_name', 'lft'): sort_path begins with the tree's
        # root-bay name (natural_sort collation), so the global list groups by
        # root-bay name across devices, descendants following their root. `pk`
        # gives a deterministic tie-break among same-named roots on different devices
        # (MPTT's lft=1 left this order arbitrary).
        ordering = ('sort_path', 'pk')
        indexes = (
            GistIndex(fields=['path'], name='dcim_modulebay_path_gist'),
            models.Index(fields=['sort_path'], name='dcim_modulebay_sort_path_idx'),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('device', 'module', 'name'),
                name='%(app_label)s_%(class)s_unique_device_module_name'
            ),
        )
        verbose_name = _('module bay')
        verbose_name_plural = _('module bays')

    def clean(self):
        super().clean()

        # Check for recursion
        if module := self.module:
            module_bays = [self.pk]
            modules = []
            while module:
                if module.pk in modules or module.module_bay.pk in module_bays:
                    raise ValidationError(_("A module bay cannot belong to a module installed within it."))
                modules.append(module.pk)
                module_bays.append(module.module_bay.pk)
                module = module.module_bay.module if module.module_bay else None

    def save(self, *args, **kwargs):
        if self.module:
            self.parent = self.module.module_bay
        else:
            self.parent = None
        super().save(*args, **kwargs)

    def _parent_creates_cycle(self):
        # A ModuleBay's parent is system-derived from its module (see save()), not
        # user-assigned, and module/bay recursion is validated in clean(); skip the
        # generic ltree cycle guard.
        return False

    @property
    def _occupied(self):
        """
        Indicates whether the module bay is occupied by a module.
        """
        return bool(not self.enabled or hasattr(self, 'installed_module'))

    @property
    def is_module_compatible(self):
        """
        Return True if the installed module (if any) is compatible with this bay's type constraints,
        or if this bay has no type constraints, or if no module is installed.
        Returns False when this bay and the installed module's type have non-empty, disjoint bay type sets.
        """
        module = getattr(self, 'installed_module', None)
        if module is None:
            return True
        # Use .all() so a prefetch cache is honoured; see Module.is_bay_compatible for details.
        bay_types = {t.pk for t in self.module_bay_types.all()}
        if not bay_types:
            return True
        type_types = {t.pk for t in module.module_type.module_bay_types.all()}
        if type_types and not (bay_types & type_types):
            return False
        return True

    def get_incompatible_module(self):
        """
        Return the installed Module if it is incompatible with this bay's type constraints, else None.
        """
        module = getattr(self, 'installed_module', None)
        return module if module and not self.is_module_compatible else None


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
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True,
    )

    clone_fields = ('device', 'enabled')

    class Meta(ComponentModel.Meta):
        verbose_name = _('device bay')
        verbose_name_plural = _('device bays')

    def clean(self):
        super().clean()

        # Validate that the parent Device can have DeviceBays
        if hasattr(self, 'device') and not self.device.device_type.is_parent_device:
            raise ValidationError(_("This type of device ({device_type}) does not support device bays.").format(
                device_type=self.device.device_type
            ))

        # Prevent installing a device into a disabled bay
        if self.installed_device and not self.enabled:
            current_installed_device_id = (
                DeviceBay.objects.filter(pk=self.pk).values_list('installed_device_id', flat=True).first()
            )
            if self.pk is None or current_installed_device_id != self.installed_device_id:
                raise ValidationError({
                    'installed_device': _("Cannot install a device in a disabled device bay.")
                })

        # Cannot install a device into itself, obviously
        if self.installed_device and getattr(self, 'device', None) == self.installed_device:
            raise ValidationError(_("Cannot install a device into itself."))

        # Check that the installed device is not already installed elsewhere
        if self.installed_device:
            current_bay = DeviceBay.objects.filter(installed_device=self.installed_device).first()
            if current_bay and current_bay != self:
                raise ValidationError({
                    'installed_device': _(
                        "Cannot install the specified device; device is already installed in {bay}."
                    ).format(bay=current_bay)
                })

    @property
    def _occupied(self):
        """
        Indicates whether the device bay is occupied by a child device.
        """
        return bool(not self.enabled or self.installed_device_id)


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


class InventoryItem(LtreeModel, ComponentModel, TrackingModelMixin):
    """
    An InventoryItem represents a serialized piece of hardware within a Device, such as a line card or power supply.
    InventoryItems are used only for inventory purposes.
    """
    parent = models.ForeignKey(
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

    clone_fields = ('device', 'parent', 'role', 'manufacturer', 'status', 'part_id')

    objects = LtreeManager()

    class Meta:
        # Global list is flat + alphabetical by name (natural_sort collation). The
        # per-device Inventory tab renders the hierarchy instead — DeviceInventoryView
        # .get_children() orders that by `path`. `pk` is a deterministic tie-break for
        # same-named items on different devices.
        ordering = ('name', 'pk')
        indexes = (
            models.Index(fields=('component_type', 'component_id')),
            GistIndex(fields=['path'], name='dcim_inventoryitem_path_gist'),
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

        # Validation for moving InventoryItems
        if not self._state.adding:
            # Cannot move an InventoryItem to another device if it has a parent
            if self.parent and self.parent.device != self.device:
                raise ValidationError({
                    "parent": _("Parent inventory item does not belong to the same device.")
                })

            # Prevent moving InventoryItems with children
            first_child = self.get_children().first()
            if first_child and first_child.device != self.device:
                raise ValidationError(_("Cannot move an inventory item with dependent children"))

            # When moving an InventoryItem to another device, remove any associated component
            if self.component and self.component.device != self.device:
                self.component = None
        else:
            if self.component and self.component.device != self.device:
                raise ValidationError({
                    "device": _("Cannot assign inventory item to component on another device")
                })

    def get_status_color(self):
        return InventoryItemStatusChoices.colors.get(self.status)
