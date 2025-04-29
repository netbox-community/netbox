import itertools

from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import Signal
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from dcim.choices import *
from dcim.constants import *
from dcim.fields import PathField
from dcim.utils import decompile_path_node, object_to_path_node
from netbox.models import ChangeLoggedModel, PrimaryModel
from utilities.conversion import to_meters
from utilities.exceptions import AbortRequest
from utilities.fields import ColorField, GenericArrayForeignKey
from utilities.querysets import RestrictedQuerySet
from wireless.models import WirelessLink
from .device_components import FrontPort, RearPort, PathEndpoint

__all__ = (
    'Cable',
    'CablePath',
    'CableTermination',
)

from ..exceptions import UnsupportedCablePath

trace_paths = Signal()


#
# Cables
#

class Cable(PrimaryModel):
    """
    A physical connection between two endpoints.
    """
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=CableTypeChoices,
        blank=True,
        null=True
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=50,
        choices=LinkStatusChoices,
        default=LinkStatusChoices.STATUS_CONNECTED
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='cables',
        blank=True,
        null=True
    )
    label = models.CharField(
        verbose_name=_('label'),
        max_length=100,
        blank=True
    )
    color = ColorField(
        verbose_name=_('color'),
        blank=True
    )
    length = models.DecimalField(
        verbose_name=_('length'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    length_unit = models.CharField(
        verbose_name=_('length unit'),
        max_length=50,
        choices=CableLengthUnitChoices,
        blank=True,
        null=True
    )
    # Stores the normalized length (in meters) for database ordering
    _abs_length = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True
    )

    clone_fields = ('tenant', 'type',)

    class Meta:
        ordering = ('pk',)
        verbose_name = _('cable')
        verbose_name_plural = _('cables')

    def __init__(self, *args, a_terminations=None, b_terminations=None, **kwargs):
        super().__init__(*args, **kwargs)

        # A copy of the PK to be used by __str__ in case the object is deleted
        self._pk = self.__dict__.get('id')

        # Cache the original status so we can check later if it's been changed
        self._orig_status = self.__dict__.get('status')

        self._terminations_modified = False

        # Assign or retrieve A/B terminations
        if a_terminations:
            self.a_terminations = a_terminations
        if b_terminations:
            self.b_terminations = b_terminations

    def __str__(self):
        pk = self.pk or self._pk
        return self.label or f'#{pk}'

    @property
    def a_terminations(self):
        if hasattr(self, '_a_terminations'):
            return self._a_terminations

        if not self.pk:
            return []

        # Query self.terminations.all() to leverage cached results
        return [
            ct.termination for ct in self.terminations.all() if ct.cable_end == CableEndChoices.SIDE_A
        ]

    @a_terminations.setter
    def a_terminations(self, value):
        if not self.pk or self.a_terminations != list(value):
            self._terminations_modified = True
        self._a_terminations = value

    @property
    def b_terminations(self):
        if hasattr(self, '_b_terminations'):
            return self._b_terminations

        if not self.pk:
            return []

        # Query self.terminations.all() to leverage cached results
        return [
            ct.termination for ct in self.terminations.all() if ct.cable_end == CableEndChoices.SIDE_B
        ]

    @b_terminations.setter
    def b_terminations(self, value):
        if not self.pk or self.b_terminations != list(value):
            self._terminations_modified = True
        self._b_terminations = value

    def clean(self):
        super().clean()

        # Validate length and length_unit
        if self.length is not None and not self.length_unit:
            raise ValidationError(_("Must specify a unit when setting a cable length"))

        if self._state.adding and self.pk is None and (not self.a_terminations or not self.b_terminations):
            raise ValidationError(_("Must define A and B terminations when creating a new cable."))

        if self._terminations_modified:

            # Check that all termination objects for either end are of the same type
            for terms in (self.a_terminations, self.b_terminations):
                if len(terms) > 1 and not all(isinstance(t, type(terms[0])) for t in terms[1:]):
                    raise ValidationError(_("Cannot connect different termination types to same end of cable."))

            # Check that termination types are compatible
            if self.a_terminations and self.b_terminations:
                a_type = self.a_terminations[0]._meta.model_name
                b_type = self.b_terminations[0]._meta.model_name
                if b_type not in COMPATIBLE_TERMINATION_TYPES.get(a_type):
                    raise ValidationError(
                        _("Incompatible termination types: {type_a} and {type_b}").format(type_a=a_type, type_b=b_type)
                    )
                if a_type == b_type:
                    # can't directly use self.a_terminations here as possible they
                    # don't have pk yet
                    a_pks = set(obj.pk for obj in self.a_terminations if obj.pk)
                    b_pks = set(obj.pk for obj in self.b_terminations if obj.pk)

                    if (a_pks & b_pks):
                        raise ValidationError(
                            _("A and B terminations cannot connect to the same object.")
                        )

            # Run clean() on any new CableTerminations
            for termination in self.a_terminations:
                CableTermination(cable=self, cable_end='A', termination=termination).clean()
            for termination in self.b_terminations:
                CableTermination(cable=self, cable_end='B', termination=termination).clean()

    def save(self, *args, **kwargs):
        _created = self.pk is None

        # Store the given length (if any) in meters for use in database ordering
        if self.length is not None and self.length_unit:
            self._abs_length = to_meters(self.length, self.length_unit)
        else:
            self._abs_length = None

        # Clear length_unit if no length is defined
        if self.length is None:
            self.length_unit = None

        super().save(*args, **kwargs)

        # Update the private pk used in __str__ in case this is a new object (i.e. just got its pk)
        self._pk = self.pk

        # Retrieve existing A/B terminations for the Cable
        a_terminations = {ct.termination: ct for ct in self.terminations.filter(cable_end='A')}
        b_terminations = {ct.termination: ct for ct in self.terminations.filter(cable_end='B')}

        # Delete stale CableTerminations
        if self._terminations_modified:
            for termination, ct in a_terminations.items():
                if termination.pk and termination not in self.a_terminations:
                    ct.delete()
            for termination, ct in b_terminations.items():
                if termination.pk and termination not in self.b_terminations:
                    ct.delete()

        # Save new CableTerminations (if any)
        if self._terminations_modified:
            for termination in self.a_terminations:
                if not termination.pk or termination not in a_terminations:
                    CableTermination(cable=self, cable_end='A', termination=termination).save()
            for termination in self.b_terminations:
                if not termination.pk or termination not in b_terminations:
                    CableTermination(cable=self, cable_end='B', termination=termination).save()
        try:
            trace_paths.send(Cable, instance=self, created=_created)
        except UnsupportedCablePath as e:
            raise AbortRequest(e)

    def get_status_color(self):
        return LinkStatusChoices.colors.get(self.status)


class CableTermination(ChangeLoggedModel):
    """
    A mapping between side A or B of a Cable and a terminating object (e.g. an Interface or CircuitTermination).
    """
    cable = models.ForeignKey(
        to='dcim.Cable',
        on_delete=models.CASCADE,
        related_name='terminations'
    )
    cable_end = models.CharField(
        max_length=1,
        choices=CableEndChoices,
        verbose_name=_('end')
    )
    termination_type = models.ForeignKey(
        to='contenttypes.ContentType',
        limit_choices_to=CABLE_TERMINATION_MODELS,
        on_delete=models.PROTECT,
        related_name='+'
    )
    termination_id = models.PositiveBigIntegerField()
    termination = GenericForeignKey(
        ct_field='termination_type',
        fk_field='termination_id'
    )

    # Cached associations to enable efficient filtering
    _device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    _rack = models.ForeignKey(
        to='dcim.Rack',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    _location = models.ForeignKey(
        to='dcim.Location',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    _site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ('cable', 'cable_end', 'pk')
        indexes = (
            models.Index(fields=('termination_type', 'termination_id')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('termination_type', 'termination_id'),
                name='%(app_label)s_%(class)s_unique_termination'
            ),
        )
        verbose_name = _('cable termination')
        verbose_name_plural = _('cable terminations')

    def __str__(self):
        return f'Cable {self.cable} to {self.termination}'

    def clean(self):
        super().clean()

        # Check for existing termination
        qs = CableTermination.objects.filter(
            termination_type=self.termination_type,
            termination_id=self.termination_id
        )
        if self.cable.pk:
            qs = qs.exclude(cable=self.cable)

        existing_termination = qs.first()
        if existing_termination is not None:
            raise ValidationError(
                _("Duplicate termination found for {app_label}.{model} {termination_id}: cable {cable_pk}".format(
                    app_label=self.termination_type.app_label,
                    model=self.termination_type.model,
                    termination_id=self.termination_id,
                    cable_pk=existing_termination.cable.pk
                ))
            )
        # Validate interface type (if applicable)
        if self.termination_type.model == 'interface' and self.termination.type in NONCONNECTABLE_IFACE_TYPES:
            raise ValidationError(
                _("Cables cannot be terminated to {type_display} interfaces").format(
                    type_display=self.termination.get_type_display()
                )
            )

        # A CircuitTermination attached to a ProviderNetwork cannot have a Cable
        if self.termination_type.model == 'circuittermination' and self.termination._provider_network is not None:
            raise ValidationError(_("Circuit terminations attached to a provider network may not be cabled."))

    def save(self, *args, **kwargs):

        # Cache objects associated with the terminating object (for filtering)
        self.cache_related_objects()

        super().save(*args, **kwargs)

        # Set the cable on the terminating object
        termination = self.termination._meta.model.objects.get(pk=self.termination_id)
        termination.snapshot()
        termination.cable = self.cable
        termination.cable_end = self.cable_end
        termination.save()

    def delete(self, *args, **kwargs):

        # Delete the cable association on the terminating object
        termination = self.termination._meta.model.objects.get(pk=self.termination_id)
        termination.snapshot()
        termination.cable = None
        termination.cable_end = None
        termination.save()

        super().delete(*args, **kwargs)

    def cache_related_objects(self):
        """
        Cache objects related to the termination (e.g. device, rack, site) directly on the object to
        enable efficient filtering.
        """
        assert self.termination is not None

        # Device components
        if getattr(self.termination, 'device', None):
            self._device = self.termination.device
            self._rack = self.termination.device.rack
            self._location = self.termination.device.location
            self._site = self.termination.device.site

        # Power feeds
        elif getattr(self.termination, 'rack', None):
            self._rack = self.termination.rack
            self._location = self.termination.rack.location
            self._site = self.termination.rack.site

        # Circuit terminations
        elif getattr(self.termination, 'site', None):
            self._site = self.termination.site
    cache_related_objects.alters_data = True

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.termination
        return objectchange


class CablePath(models.Model):
    """
    A CablePath instance represents the physical path from a set of origin nodes to a set of destination nodes,
    including all intermediate elements.

    `path` contains the ordered set of nodes, arranged in lists of (type, ID) tuples. (Each cable in the path can
    terminate to one or more objects.)  For example, consider the following
    topology:

                     A                              B                              C
        Interface 1 --- Front Port 1 | Rear Port 1 --- Rear Port 2 | Front Port 3 --- Interface 2
                        Front Port 2                                 Front Port 4

    This path would be expressed as:

    CablePath(
        path = [
            [Interface 1],
            [Cable A],
            [Front Port 1, Front Port 2],
            [Rear Port 1],
            [Cable B],
            [Rear Port 2],
            [Front Port 3, Front Port 4],
            [Cable C],
            [Interface 2],
        ]
    )

    `is_active` is set to True only if every Cable within the path has a status of "connected". `is_complete` is True
    if the instance represents a complete end-to-end path from origin(s) to destination(s). `is_split` is True if the
    path diverges across multiple cables.

    `_nodes` retains a flattened list of all nodes within the path to enable simple filtering.
    """
    path = models.JSONField(
        verbose_name=_('path'),
        default=list
    )
    is_active = models.BooleanField(
        verbose_name=_('is active'),
        default=False
    )
    is_complete = models.BooleanField(
        verbose_name=_('is complete'),
        default=False
    )
    is_split = models.BooleanField(
        verbose_name=_('is split'),
        default=False
    )
    _nodes = PathField()

    _netbox_private = True

    class Meta:
        verbose_name = _('cable path')
        verbose_name_plural = _('cable paths')

    def __str__(self):
        return f"Path #{self.pk}: {len(self.path)} hops"

    def save(self, *args, **kwargs):

        # Save the flattened nodes list
        self._nodes = list(itertools.chain(*self.path))

        super().save(*args, **kwargs)

        # Record a direct reference to this CablePath on its originating object(s)
        origin_model = self.origin_type.model_class()
        origin_ids = [decompile_path_node(node)[1] for node in self.path[0]]
        origin_model.objects.filter(pk__in=origin_ids).update(_path=self.pk)

    @property
    def origin_type(self):
        if self.path:
            ct_id, _ = decompile_path_node(self.path[0][0])
            return ObjectType.objects.get_for_id(ct_id)

    @property
    def destination_type(self):
        if self.is_complete:
            ct_id, _ = decompile_path_node(self.path[-1][0])
            return ObjectType.objects.get_for_id(ct_id)

    @property
    def _path_decompiled(self):
        res = []
        for step in self.path:
            nodes = []
            for node in step:
                nodes.append(decompile_path_node(node))
            res.append(nodes)
        return res

    path_objects = GenericArrayForeignKey("_path_decompiled")

    @property
    def origins(self):
        """
        Return the list of originating objects.
        """
        return self.path_objects[0]

    @property
    def destinations(self):
        """
        Return the list of destination objects, if the path is complete.
        """
        if not self.is_complete:
            return []
        return self.path_objects[-1]

    @property
    def segment_count(self):
        return int(len(self.path) / 3)

    @classmethod
    def from_origin(cls, terminations):
        """
        Create a new CablePath instance as traced from the given termination objects. These can be any object to which a
        Cable or WirelessLink connects (interfaces, console ports, circuit termination, etc.). All terminations must be
        of the same type and must belong to the same parent object.
        """
        from circuits.models import CircuitTermination

        if not terminations:
            return None

        # Ensure all originating terminations are attached to the same link
        if len(terminations) > 1 and not all(t.link == terminations[0].link for t in terminations[1:]):
            raise UnsupportedCablePath(_("All originating terminations must be attached to the same link"))

        path = []
        position_stack = []
        is_complete = False
        is_active = True
        is_split = False

        while terminations:

            # Terminations must all be of the same type
            if not all(isinstance(t, type(terminations[0])) for t in terminations[1:]):
                raise UnsupportedCablePath(_("All mid-span terminations must have the same termination type"))

            # All mid-span terminations must all be attached to the same device
            if (not isinstance(terminations[0], PathEndpoint) and not
                    all(t.parent_object == terminations[0].parent_object for t in terminations[1:])):
                raise UnsupportedCablePath(_("All mid-span terminations must have the same parent object"))

            # Check for a split path (e.g. rear port fanning out to multiple front ports with
            # different cables attached)
            if len(set(t.link for t in terminations)) > 1 and (
                    position_stack and len(terminations) != len(position_stack[-1])
            ):
                is_split = True
                break

            # Step 1: Record the near-end termination object(s)
            path.append([
                object_to_path_node(t) for t in terminations
            ])

            # Step 2: Determine the attached links (Cable or WirelessLink), if any
            links = [termination.link for termination in terminations if termination.link is not None]
            if len(links) == 0:
                if len(path) == 1:
                    # If this is the start of the path and no link exists, return None
                    return None
                # Otherwise, halt the trace if no link exists
                break
            if not all(type(link) in (Cable, WirelessLink) for link in links):
                raise UnsupportedCablePath(_("All links must be cable or wireless"))
            if not all(isinstance(link, type(links[0])) for link in links):
                raise UnsupportedCablePath(_("All links must match first link type"))

            # Step 3: Record asymmetric paths as split
            not_connected_terminations = [termination.link for termination in terminations if termination.link is None]
            if len(not_connected_terminations) > 0:
                is_complete = False
                is_split = True

            # Step 4: Record the links, keeping cables in order to allow for SVG rendering
            cables = []
            for link in links:
                if object_to_path_node(link) not in cables:
                    cables.append(object_to_path_node(link))
            path.append(cables)

            # Step 5: Update the path status if a link is not connected
            links_status = [link.status for link in links if link.status != LinkStatusChoices.STATUS_CONNECTED]
            if any([status != LinkStatusChoices.STATUS_CONNECTED for status in links_status]):
                is_active = False

            # Step 6: Determine the far-end terminations
            if isinstance(links[0], Cable):
                termination_type = ObjectType.objects.get_for_model(terminations[0])
                local_cable_terminations = CableTermination.objects.filter(
                    termination_type=termination_type,
                    termination_id__in=[t.pk for t in terminations]
                )

                q_filter = Q()
                for lct in local_cable_terminations:
                    cable_end = 'A' if lct.cable_end == 'B' else 'B'
                    q_filter |= Q(cable=lct.cable, cable_end=cable_end)

                # Make sure this filter has been populated; if not, we have probably been given invalid data
                if not q_filter:
                    break

                remote_cable_terminations = CableTermination.objects.filter(q_filter)
                remote_terminations = [ct.termination for ct in remote_cable_terminations]
            else:
                # WirelessLink
                remote_terminations = [
                    link.interface_b if link.interface_a is terminations[0] else link.interface_a for link in links
                ]

            # Remote Terminations must all be of the same type, otherwise return a split path
            if not all(isinstance(t, type(remote_terminations[0])) for t in remote_terminations[1:]):
                is_complete = False
                is_split = True
                break

            # Step 7: Record the far-end termination object(s)
            path.append([
                object_to_path_node(t) for t in remote_terminations if t is not None
            ])

            # Step 8: Determine the "next hop" terminations, if applicable
            if not remote_terminations:
                break

            if isinstance(remote_terminations[0], FrontPort):
                # Follow FrontPorts to their corresponding RearPorts
                rear_ports = RearPort.objects.filter(
                    pk__in=[t.rear_port_id for t in remote_terminations]
                )
                if len(rear_ports) > 1 or rear_ports[0].positions > 1:
                    position_stack.append([fp.rear_port_position for fp in remote_terminations])

                terminations = rear_ports

            elif isinstance(remote_terminations[0], RearPort):
                if len(remote_terminations) == 1 and remote_terminations[0].positions == 1:
                    front_ports = FrontPort.objects.filter(
                        rear_port_id__in=[rp.pk for rp in remote_terminations],
                        rear_port_position=1
                    )
                # Obtain the individual front ports based on the termination and all positions
                elif len(remote_terminations) > 1 and position_stack:
                    positions = position_stack.pop()

                    # Ensure we have a number of positions equal to the amount of remote terminations
                    if len(remote_terminations) != len(positions):
                        raise UnsupportedCablePath(
                            _("All positions counts within the path on opposite ends of links must match")
                        )

                    # Get our front ports
                    q_filter = Q()
                    for rt in remote_terminations:
                        position = positions.pop()
                        q_filter |= Q(rear_port_id=rt.pk, rear_port_position=position)
                    if q_filter is Q():
                        raise UnsupportedCablePath(_("Remote termination position filter is missing"))
                    front_ports = FrontPort.objects.filter(q_filter)
                # Obtain the individual front ports based on the termination and position
                elif position_stack:
                    front_ports = FrontPort.objects.filter(
                        rear_port_id=remote_terminations[0].pk,
                        rear_port_position__in=position_stack.pop()
                    )
                # If all rear ports have a single position, we can just get the front ports
                elif all([rp.positions == 1 for rp in remote_terminations]):
                    front_ports = FrontPort.objects.filter(rear_port_id__in=[rp.pk for rp in remote_terminations])

                    if len(front_ports) != len(remote_terminations):
                        # Some rear ports does not have a front port
                        is_split = True
                        break
                else:
                    # No position indicated: path has split, so we stop at the RearPorts
                    is_split = True
                    break

                terminations = front_ports

            elif isinstance(remote_terminations[0], CircuitTermination):
                # Follow a CircuitTermination to its corresponding CircuitTermination (A to Z or vice versa)
                if len(remote_terminations) > 1:
                    is_split = True
                    break
                circuit_termination = CircuitTermination.objects.filter(
                    circuit=remote_terminations[0].circuit,
                    term_side='Z' if remote_terminations[0].term_side == 'A' else 'A'
                ).first()
                if circuit_termination is None:
                    break
                elif circuit_termination._provider_network:
                    # Circuit terminates to a ProviderNetwork
                    path.extend([
                        [object_to_path_node(circuit_termination)],
                        [object_to_path_node(circuit_termination._provider_network)],
                    ])
                    is_complete = True
                    break
                elif circuit_termination.termination and not circuit_termination.cable:
                    # Circuit terminates to a Region/Site/etc.
                    path.extend([
                        [object_to_path_node(circuit_termination)],
                        [object_to_path_node(circuit_termination.termination)],
                    ])
                    break

                terminations = [circuit_termination]

            else:
                # Check for non-symmetric path
                if all(isinstance(t, type(remote_terminations[0])) for t in remote_terminations[1:]):
                    is_complete = True
                elif len(remote_terminations) == 0:
                    is_complete = False
                else:
                    # Unsupported topology, mark as split and exit
                    is_complete = False
                    is_split = True
                break

        return cls(
            path=path,
            is_complete=is_complete,
            is_active=is_active,
            is_split=is_split
        )

    def retrace(self):
        """
        Retrace the path from the currently-defined originating termination(s)
        """
        _new = self.from_origin(self.origins)
        if _new:
            self.path = _new.path
            self.is_complete = _new.is_complete
            self.is_active = _new.is_active
            self.is_split = _new.is_split
            self.save()
        else:
            self.delete()
    retrace.alters_data = True

    def get_cable_ids(self):
        """
        Return all Cable IDs within the path.
        """
        cable_ct = ObjectType.objects.get_for_model(Cable).pk
        cable_ids = []

        for node in self._nodes:
            ct, id = decompile_path_node(node)
            if ct == cable_ct:
                cable_ids.append(id)

        return cable_ids

    def get_total_length(self):
        """
        Return a tuple containing the sum of the length of each cable in the path
        and a flag indicating whether the length is definitive.
        """
        cable_ct = ObjectType.objects.get_for_model(Cable).pk

        # Pre-cache cable lengths by ID
        cable_ids = self.get_cable_ids()
        cables = {
            cable['pk']: cable['_abs_length']
            for cable in Cable.objects.filter(id__in=cable_ids, _abs_length__isnull=False).values('pk', '_abs_length')
        }

        # Iterate through each set of nodes in the path. For cables, add the length of the longest cable to the total
        # length of the path.
        total_length = 0
        for node_set in self.path:
            hop_length = 0
            for node in node_set:
                ct, pk = decompile_path_node(node)
                if ct != cable_ct:
                    break  # Not a cable
                if pk in cables and cables[pk] > hop_length:
                    hop_length = cables[pk]
            total_length += hop_length

        is_definitive = len(cables) == len(cable_ids)

        return total_length, is_definitive

    def get_split_nodes(self):
        """
        Return all available next segments in a split cable path.
        """
        from circuits.models import CircuitTermination
        nodes = self.path_objects[-1]

        # RearPort splitting to multiple FrontPorts with no stack position
        if type(nodes[0]) is RearPort:
            return FrontPort.objects.filter(rear_port__in=nodes)
        # Cable terminating to multiple FrontPorts mapped to different
        # RearPorts connected to different cables
        elif type(nodes[0]) is FrontPort:
            return RearPort.objects.filter(pk__in=[fp.rear_port_id for fp in nodes])
        # Cable terminating to multiple CircuitTerminations
        elif type(nodes[0]) is CircuitTermination:
            return [
                ct.get_peer_termination() for ct in nodes
            ]

    def get_asymmetric_nodes(self):
        """
        Return all available next segments in a split cable path.
        """
        from circuits.models import CircuitTermination
        asymmetric_nodes = []
        for nodes in self.path_objects:
            if type(nodes[0]) in [RearPort, FrontPort, CircuitTermination]:
                asymmetric_nodes.extend([node for node in nodes if node.link is None])

        return asymmetric_nodes
