from collections import defaultdict

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models import Sum
from django.urls import reverse

from dcim.choices import *
from dcim.constants import *
from dcim.fields import MultiNodePathField, PathField
from dcim.utils import decompile_path_node, flatten_path, object_to_path_node, path_node_to_object
from netbox.models import NetBoxModel
from utilities.fields import ColorField
from utilities.utils import to_meters
from .devices import Device
from .device_components import FrontPort, RearPort


__all__ = (
    'Cable',
    'CablePath',
    'CableTermination',
)


#
# Cables
#

class Cable(NetBoxModel):
    """
    A physical connection between two endpoints.
    """
    type = models.CharField(
        max_length=50,
        choices=CableTypeChoices,
        blank=True
    )
    status = models.CharField(
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
        max_length=100,
        blank=True
    )
    color = ColorField(
        blank=True
    )
    length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    length_unit = models.CharField(
        max_length=50,
        choices=CableLengthUnitChoices,
        blank=True,
    )
    # Stores the normalized length (in meters) for database ordering
    _abs_length = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        blank=True,
        null=True
    )
    # Cache the associated device (where applicable) for the A and B terminations. This enables filtering of Cables by
    # their associated Devices.
    _termination_a_device = models.ForeignKey(
        to=Device,
        on_delete=models.CASCADE,
        related_name='+',
        blank=True,
        null=True
    )
    _termination_b_device = models.ForeignKey(
        to=Device,
        on_delete=models.CASCADE,
        related_name='+',
        blank=True,
        null=True
    )

    terminations = []

    class Meta:
        ordering = ('pk',)

    def __init__(self, *args, terminations=None, **kwargs):
        super().__init__(*args, **kwargs)

        # A copy of the PK to be used by __str__ in case the object is deleted
        self._pk = self.pk

        # Cache the original status so we can check later if it's been changed
        self._orig_status = self.status

        # Assign associated CableTerminations (if any)
        if terminations:
            assert type(terminations) is list
            assert self.pk is None
            for t in terminations:
                t.cable = self
                self.terminations.append(t)

    @classmethod
    def from_db(cls, db, field_names, values):
        """
        Cache the original A and B terminations of existing Cable instances for later reference inside clean().
        """
        instance = super().from_db(db, field_names, values)

        instance.terminations = CableTermination.objects.filter(cable=instance)

        # instance._orig_termination_a_type_id = instance.termination_a_type_id
        # instance._orig_termination_a_ids = instance.termination_a_ids
        # instance._orig_termination_b_type_id = instance.termination_b_type_id
        # instance._orig_termination_b_ids = instance.termination_b_ids

        return instance

    def __str__(self):
        pk = self.pk or self._pk
        return self.label or f'#{pk}'

    def get_absolute_url(self):
        return reverse('dcim:cable', args=[self.pk])

    def clean(self):
        super().clean()

        # TODO: Is this validation still necessary?
        # # Check that two connected RearPorts have the same number of positions (if both are >1)
        # if isinstance(self.termination_a, RearPort) and isinstance(self.termination_b, RearPort):
        #     if self.termination_a.positions > 1 and self.termination_b.positions > 1:
        #         if self.termination_a.positions != self.termination_b.positions:
        #             raise ValidationError(
        #                 f"{self.termination_a} has {self.termination_a.positions} position(s) but "
        #                 f"{self.termination_b} has {self.termination_b.positions}. "
        #                 f"Both terminations must have the same number of positions (if greater than one)."
        #             )

        # Validate length and length_unit
        if self.length is not None and not self.length_unit:
            raise ValidationError("Must specify a unit when setting a cable length")
        elif self.length is None:
            self.length_unit = ''

    def save(self, *args, **kwargs):

        # Store the given length (if any) in meters for use in database ordering
        if self.length and self.length_unit:
            self._abs_length = to_meters(self.length, self.length_unit)
        else:
            self._abs_length = None

        # TODO: Move to CableTermination
        # # Store the parent Device for the A and B terminations (if applicable) to enable filtering
        # if hasattr(self.termination_a[0], 'device'):
        #     self._termination_a_device = self.termination_a[0].device
        # if hasattr(self.termination_b[0], 'device'):
        #     self._termination_b_device = self.termination_b[0].device

        super().save(*args, **kwargs)

        # Update the private pk used in __str__ in case this is a new object (i.e. just got its pk)
        self._pk = self.pk

    def get_status_color(self):
        return LinkStatusChoices.colors.get(self.status)

    def get_a_terminations(self):
        return [
            term.termination for term in CableTermination.objects.filter(cable=self, cable_end='A')
        ]

    def get_b_terminations(self):
        return [
            term.termination for term in CableTermination.objects.filter(cable=self, cable_end='B')
        ]


class CableTermination(models.Model):
    """
    A mapping between side A or B of a Cable and a terminating object (e.g. an Interface or CircuitTermination).
    """
    cable = models.ForeignKey(
        to='dcim.Cable',
        on_delete=models.CASCADE,
        related_name='+'
    )
    cable_end = models.CharField(
        max_length=1,
        choices=CableEndChoices,
        verbose_name='End'
    )
    termination_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=CABLE_TERMINATION_MODELS,
        on_delete=models.PROTECT,
        related_name='+'
    )
    termination_id = models.PositiveBigIntegerField()
    termination = GenericForeignKey(
        ct_field='termination_type',
        fk_field='termination_id'
    )

    class Meta:
        ordering = ['pk']
        constraints = (
            models.UniqueConstraint(
                fields=('termination_type', 'termination_id'),
                name='unique_termination'
            ),
        )

    def __str__(self):
        return f'Cable {self.cable} to {self.termination}'

    def clean(self):
        super().clean()

        # Validate interface type (if applicable)
        if self.termination_type.model == 'interface' and self.termination.type in NONCONNECTABLE_IFACE_TYPES:
            raise ValidationError({
                'termination': f'Cables cannot be terminated to {self.termination.get_type_display()} interfaces'
            })

        # A CircuitTermination attached to a ProviderNetwork cannot have a Cable
        if self.termination_type.model == 'circuittermination' and self.termination.provider_network is not None:
            raise ValidationError({
                'termination': "Circuit terminations attached to a provider network may not be cabled."
            })

        # TODO
        # # A front port cannot be connected to its corresponding rear port
        # if (
        #     type_a in ['frontport', 'rearport'] and
        #     type_b in ['frontport', 'rearport'] and
        #     (
        #         getattr(self.termination_a, 'rear_port', None) == self.termination_b or
        #         getattr(self.termination_b, 'rear_port', None) == self.termination_a
        #     )
        # ):
        #     raise ValidationError("A front port cannot be connected to it corresponding rear port")

        # TODO
        # # Check that termination types are compatible
        # if type_b not in COMPATIBLE_TERMINATION_TYPES.get(type_a):
        #     raise ValidationError(
        #         f"Incompatible termination types: {self.termination_a_type} and {self.termination_b_type}"
        #     )


class CablePath(models.Model):
    """
    A CablePath instance represents the physical path from an origin to a destination, including all intermediate
    elements in the path. Every instance must specify an `origin`, whereas `destination` may be null (for paths which do
    not terminate on a PathEndpoint).

    `path` contains a list of nodes within the path, each represented by a tuple of (type, ID). The first element in the
    path must be a Cable instance, followed by a pair of pass-through ports. For example, consider the following
    topology:

                     1                              2                              3
        Interface A --- Front Port A | Rear Port A --- Rear Port B | Front Port B --- Interface B

    This path would be expressed as:

    CablePath(
        origin = Interface A
        destination = Interface B
        path = [Cable 1, Front Port A, Rear Port A, Cable 2, Rear Port B, Front Port B, Cable 3]
    )

    `is_active` is set to True only if 1) `destination` is not null, and 2) every Cable within the path has a status of
    "connected".
    """
    path = MultiNodePathField()
    is_active = models.BooleanField(
        default=False
    )
    is_complete = models.BooleanField(
        default=False
    )
    is_split = models.BooleanField(
        default=False
    )
    _nodes = PathField()

    class Meta:
        pass

    def __str__(self):
        status = ' (active)' if self.is_active else ' (split)' if self.is_split else ''
        return f"Path #{self.pk}: {len(self.path)} nodes{status}"

    def save(self, *args, **kwargs):

        # Save the flattened nodes list
        self._nodes = flatten_path(self.path)

        super().save(*args, **kwargs)

        # Record a direct reference to this CablePath on its originating object(s)
        origins = [path_node_to_object(n) for n in self.path[0]]
        origin_model = origins[0]._meta.model
        origin_ids = [o.id for o in origins]
        origin_model.objects.filter(pk__in=origin_ids).update(_path=self.pk)

    @property
    def segment_count(self):
        return int(len(self.path) / 3)

    @classmethod
    def from_origin(cls, terminations):
        """
        Create a new CablePath instance as traced from the given path origin.
        """
        from circuits.models import CircuitTermination

        if not terminations or terminations[0].termination.link is None:
            return None

        path = []
        position_stack = []
        is_active = True
        is_split = False

        # Start building the path from its originating CableTerminations
        path.append([
            object_to_path_node(t.termination) for t in terminations
        ])

        node = terminations[0].termination
        while node.link is not None:
            if hasattr(node.link, 'status') and node.link.status != LinkStatusChoices.STATUS_CONNECTED:
                is_active = False

            # Append the cable
            path.append([object_to_path_node(node.link)])

            # Follow the link to its far-end termination
            if terminations[0].cable_end == 'A':
                peer_terminations = CableTermination.objects.filter(cable=terminations[0].cable, cable_end='B')
            else:
                peer_terminations = CableTermination.objects.filter(cable=terminations[0].cable, cable_end='A')

            # Follow FrontPorts to their corresponding RearPorts
            if isinstance(peer_terminations[0].termination, FrontPort):
                path.append([
                    object_to_path_node(t.termination) for t in peer_terminations
                ])
                terminations = CableTermination.objects.filter(
                    termination_type=ContentType.objects.get_for_model(RearPort),
                    termination_id__in=[t.termination_id for t in peer_terminations]
                )
                node = terminations[0].termination
                if node.positions > 1:
                    position_stack.append(node.rear_port_position)
                path.append([
                    object_to_path_node(t.termination) for t in terminations
                ])

            # Follow RearPorts to their corresponding FrontPorts (if any)
            elif isinstance(peer_terminations[0], RearPort):
                path.append([
                    object_to_path_node(t.termination) for t in peer_terminations
                ])

                # Determine the peer FrontPort's position
                if peer_terminations[0].termination.positions == 1:
                    position = 1
                elif position_stack:
                    position = position_stack.pop()
                else:
                    # No position indicated: path has split, so we stop at the RearPort
                    is_split = True
                    break

                # Map FrontPorts to their corresponding RearPorts
                terminations = FrontPort.objects.filter(
                    rear_port_id__in=[t.rear_port_id for t in peer_terminations],
                    rear_port_position=position
                )
                if terminations:
                    path.append([
                        object_to_path_node(t.termination) for t in terminations
                    ])

            # Follow a CircuitTermination to its corresponding CircuitTermination (A to Z or vice versa)
            elif isinstance(peer_terminations[0], CircuitTermination):
                path.append([
                    object_to_path_node(t.termination) for t in peer_terminations
                ])

                # Get peer CircuitTerminations
                term_side = 'Z' if peer_terminations[0].termination == 'A' else 'Z'
                terminations = CircuitTermination.objects.filter(
                    circuit=peer_terminations[0].circuit,
                    term_side=term_side
                )
                # Tracing across multiple circuits not currently supported
                if len(terminations) > 1:
                    is_split = True
                    break
                elif terminations:
                    path.append([
                        object_to_path_node(t.termination) for t in terminations
                    ])
                    # TODO
                    # if node.provider_network:
                    #     destination = node.provider_network
                    #     break
                    # elif node.site and not node.cable:
                    #     destination = node.site
                    #     break
                else:
                    # No peer CircuitTermination exists; halt the trace
                    break

            # Anything else marks the end of the path
            else:
                path.append([
                    object_to_path_node(t.termination) for t in peer_terminations
                ])
                break

        return cls(
            path=path,
            is_active=is_active,
            is_split=is_split
        )

    def get_path(self):
        """
        Return the path as a list of prefetched objects.
        """
        # Compile a list of IDs to prefetch for each type of model in the path
        to_prefetch = defaultdict(list)
        for node in self._nodes:
            ct_id, object_id = decompile_path_node(node)
            to_prefetch[ct_id].append(object_id)

        # Prefetch path objects using one query per model type. Prefetch related devices where appropriate.
        prefetched = {}
        for ct_id, object_ids in to_prefetch.items():
            model_class = ContentType.objects.get_for_id(ct_id).model_class()
            queryset = model_class.objects.filter(pk__in=object_ids)
            if hasattr(model_class, 'device'):
                queryset = queryset.prefetch_related('device')
            prefetched[ct_id] = {
                obj.id: obj for obj in queryset
            }

        # Replicate the path using the prefetched objects.
        path = []
        for step in self.path:
            nodes = []
            for node in step:
                ct_id, object_id = decompile_path_node(node)
                nodes.append(prefetched[ct_id][object_id])
            path.append(nodes)

        return path

    def get_destination(self):
        if not self.is_complete:
            return None
        return [
            path_node_to_object(node) for node in self.path[-1]
        ]

    @property
    def last_nodes(self):
        """
        Return either the destination or the last node within the path.
        """
        return [
            path_node_to_object(node) for node in self.path[-1]
        ]

    def get_cable_ids(self):
        """
        Return all Cable IDs within the path.
        """
        cable_ct = ContentType.objects.get_for_model(Cable).pk
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
        cable_ids = self.get_cable_ids()
        cables = Cable.objects.filter(id__in=cable_ids, _abs_length__isnull=False)
        total_length = cables.aggregate(total=Sum('_abs_length'))['total']
        is_definitive = len(cables) == len(cable_ids)

        return total_length, is_definitive

    def get_split_nodes(self):
        """
        Return all available next segments in a split cable path.
        """
        rearport = path_node_to_object(self._nodes[-1])

        return FrontPort.objects.filter(rear_port=rearport)
