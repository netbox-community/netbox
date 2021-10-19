from collections import defaultdict

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models import Sum
from django.urls import reverse

from dcim.choices import *
from dcim.constants import *
from dcim.fields import PathField
from dcim.utils import decompile_path_node, object_to_path_node, path_node_to_object
from extras.utils import extras_features
from netbox.models import BigIDModel, PrimaryModel
from utilities.fields import ColorField
from utilities.querysets import RestrictedQuerySet
from utilities.utils import to_meters
from .devices import Device
from .device_components import FrontPort, RearPort


__all__ = (
    'Cable',
    'CablePath',
)


#
# Cables
#

@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class Cable(PrimaryModel):
    """
    A physical connection between two endpoints.
    """
    termination_a_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=CABLE_TERMINATION_MODELS,
        on_delete=models.PROTECT,
        related_name='+'
    )
    termination_a_id = models.PositiveIntegerField()
    termination_a = GenericForeignKey(
        ct_field='termination_a_type',
        fk_field='termination_a_id'
    )
    termination_b_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=CABLE_TERMINATION_MODELS,
        on_delete=models.PROTECT,
        related_name='+'
    )
    termination_b_id = models.PositiveIntegerField()
    termination_b = GenericForeignKey(
        ct_field='termination_b_type',
        fk_field='termination_b_id'
    )
    type = models.CharField(
        max_length=50,
        choices=CableTypeChoices,
        blank=True
    )
    status = models.CharField(
        max_length=50,
        choices=CableStatusChoices,
        default=CableStatusChoices.STATUS_CONNECTED
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

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ['pk']
        unique_together = (
            ('termination_a_type', 'termination_a_id'),
            ('termination_b_type', 'termination_b_id'),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # A copy of the PK to be used by __str__ in case the object is deleted
        self._pk = self.pk

        # Cache the original status so we can check later if it's been changed
        self._orig_status = self.status

    @classmethod
    def from_db(cls, db, field_names, values):
        """
        Cache the original A and B terminations of existing Cable instances for later reference inside clean().
        """
        instance = super().from_db(db, field_names, values)

        instance._orig_termination_a_type_id = instance.termination_a_type_id
        instance._orig_termination_a_id = instance.termination_a_id
        instance._orig_termination_b_type_id = instance.termination_b_type_id
        instance._orig_termination_b_id = instance.termination_b_id

        return instance

    def __str__(self):
        pk = self.pk or self._pk
        return self.label or f'#{pk}'

    def get_absolute_url(self):
        return reverse('dcim:cable', args=[self.pk])

    def clean(self):
        from circuits.models import CircuitTermination

        super().clean()

        # Validate that termination A exists
        if not hasattr(self, 'termination_a_type'):
            raise ValidationError('Termination A type has not been specified')
        try:
            self.termination_a_type.model_class().objects.get(pk=self.termination_a_id)
        except ObjectDoesNotExist:
            raise ValidationError({
                'termination_a': 'Invalid ID for type {}'.format(self.termination_a_type)
            })

        # Validate that termination B exists
        if not hasattr(self, 'termination_b_type'):
            raise ValidationError('Termination B type has not been specified')
        try:
            self.termination_b_type.model_class().objects.get(pk=self.termination_b_id)
        except ObjectDoesNotExist:
            raise ValidationError({
                'termination_b': 'Invalid ID for type {}'.format(self.termination_b_type)
            })

        # If editing an existing Cable instance, check that neither termination has been modified.
        if self.pk:
            err_msg = 'Cable termination points may not be modified. Delete and recreate the cable instead.'
            if (
                self.termination_a_type_id != self._orig_termination_a_type_id or
                self.termination_a_id != self._orig_termination_a_id
            ):
                raise ValidationError({
                    'termination_a': err_msg
                })
            if (
                self.termination_b_type_id != self._orig_termination_b_type_id or
                self.termination_b_id != self._orig_termination_b_id
            ):
                raise ValidationError({
                    'termination_b': err_msg
                })

        type_a = self.termination_a_type.model
        type_b = self.termination_b_type.model

        # Validate interface types
        if type_a == 'interface' and self.termination_a.type in NONCONNECTABLE_IFACE_TYPES:
            raise ValidationError({
                'termination_a_id': 'Cables cannot be terminated to {} interfaces'.format(
                    self.termination_a.get_type_display()
                )
            })
        if type_b == 'interface' and self.termination_b.type in NONCONNECTABLE_IFACE_TYPES:
            raise ValidationError({
                'termination_b_id': 'Cables cannot be terminated to {} interfaces'.format(
                    self.termination_b.get_type_display()
                )
            })

        # Check that termination types are compatible
        if type_b not in COMPATIBLE_TERMINATION_TYPES.get(type_a):
            raise ValidationError(
                f"Incompatible termination types: {self.termination_a_type} and {self.termination_b_type}"
            )

        # Check that two connected RearPorts have the same number of positions (if both are >1)
        if isinstance(self.termination_a, RearPort) and isinstance(self.termination_b, RearPort):
            if self.termination_a.positions > 1 and self.termination_b.positions > 1:
                if self.termination_a.positions != self.termination_b.positions:
                    raise ValidationError(
                        f"{self.termination_a} has {self.termination_a.positions} position(s) but "
                        f"{self.termination_b} has {self.termination_b.positions}. "
                        f"Both terminations must have the same number of positions (if greater than one)."
                    )

        # A termination point cannot be connected to itself
        if self.termination_a == self.termination_b:
            raise ValidationError(f"Cannot connect {self.termination_a_type} to itself")

        # A front port cannot be connected to its corresponding rear port
        if (
            type_a in ['frontport', 'rearport'] and
            type_b in ['frontport', 'rearport'] and
            (
                getattr(self.termination_a, 'rear_port', None) == self.termination_b or
                getattr(self.termination_b, 'rear_port', None) == self.termination_a
            )
        ):
            raise ValidationError("A front port cannot be connected to it corresponding rear port")

        # A CircuitTermination attached to a ProviderNetwork cannot have a Cable
        if isinstance(self.termination_a, CircuitTermination) and self.termination_a.provider_network is not None:
            raise ValidationError({
                'termination_a_id': "Circuit terminations attached to a provider network may not be cabled."
            })
        if isinstance(self.termination_b, CircuitTermination) and self.termination_b.provider_network is not None:
            raise ValidationError({
                'termination_b_id': "Circuit terminations attached to a provider network may not be cabled."
            })

        # Check for an existing Cable connected to either termination object
        if self.termination_a.cable not in (None, self):
            raise ValidationError("{} already has a cable attached (#{})".format(
                self.termination_a, self.termination_a.cable_id
            ))
        if self.termination_b.cable not in (None, self):
            raise ValidationError("{} already has a cable attached (#{})".format(
                self.termination_b, self.termination_b.cable_id
            ))

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

        # Store the parent Device for the A and B terminations (if applicable) to enable filtering
        if hasattr(self.termination_a, 'device'):
            self._termination_a_device = self.termination_a.device
        if hasattr(self.termination_b, 'device'):
            self._termination_b_device = self.termination_b.device

        super().save(*args, **kwargs)

        # Update the private pk used in __str__ in case this is a new object (i.e. just got its pk)
        self._pk = self.pk

    def get_status_class(self):
        return CableStatusChoices.CSS_CLASSES.get(self.status)

    def get_compatible_types(self):
        """
        Return all termination types compatible with termination A.
        """
        if self.termination_a is None:
            return
        return COMPATIBLE_TERMINATION_TYPES[self.termination_a._meta.model_name]


class CablePath(BigIDModel):
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
    origin_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        related_name='+'
    )
    origin_id = models.PositiveIntegerField()
    origin = GenericForeignKey(
        ct_field='origin_type',
        fk_field='origin_id'
    )
    destination_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        related_name='+',
        blank=True,
        null=True
    )
    destination_id = models.PositiveIntegerField(
        blank=True,
        null=True
    )
    destination = GenericForeignKey(
        ct_field='destination_type',
        fk_field='destination_id'
    )
    path = PathField()
    is_active = models.BooleanField(
        default=False
    )
    is_split = models.BooleanField(
        default=False
    )

    class Meta:
        unique_together = ('origin_type', 'origin_id')

    def __str__(self):
        status = ' (active)' if self.is_active else ' (split)' if self.is_split else ''
        return f"Path #{self.pk}: {self.origin} to {self.destination} via {len(self.path)} nodes{status}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Record a direct reference to this CablePath on its originating object
        model = self.origin._meta.model
        model.objects.filter(pk=self.origin.pk).update(_path=self.pk)

    @property
    def segment_count(self):
        total_length = 1 + len(self.path) + (1 if self.destination else 0)
        return int(total_length / 3)

    @classmethod
    def from_origin(cls, origin):
        """
        Create a new CablePath instance as traced from the given path origin.
        """
        from circuits.models import CircuitTermination

        if origin is None or origin.cable is None:
            return None

        destination = None
        path = []
        position_stack = []
        is_active = True
        is_split = False

        node = origin
        while node.cable is not None:
            if node.cable.status != CableStatusChoices.STATUS_CONNECTED:
                is_active = False

            # Follow the cable to its far-end termination
            path.append(object_to_path_node(node.cable))
            peer_termination = node.get_cable_peer()

            # Follow a FrontPort to its corresponding RearPort
            if isinstance(peer_termination, FrontPort):
                path.append(object_to_path_node(peer_termination))
                node = peer_termination.rear_port
                if node.positions > 1:
                    position_stack.append(peer_termination.rear_port_position)
                path.append(object_to_path_node(node))

            # Follow a RearPort to its corresponding FrontPort (if any)
            elif isinstance(peer_termination, RearPort):
                path.append(object_to_path_node(peer_termination))

                # Determine the peer FrontPort's position
                if peer_termination.positions == 1:
                    position = 1
                elif position_stack:
                    position = position_stack.pop()
                else:
                    # No position indicated: path has split, so we stop at the RearPort
                    is_split = True
                    break

                try:
                    node = FrontPort.objects.get(rear_port=peer_termination, rear_port_position=position)
                    path.append(object_to_path_node(node))
                except ObjectDoesNotExist:
                    # No corresponding FrontPort found for the RearPort
                    break

            # Follow a CircuitTermination to its corresponding CircuitTermination (A to Z or vice versa)
            elif isinstance(peer_termination, CircuitTermination):
                path.append(object_to_path_node(peer_termination))
                # Get peer CircuitTermination
                node = peer_termination.get_peer_termination()
                if node:
                    path.append(object_to_path_node(node))
                    if node.provider_network:
                        destination = node.provider_network
                        break
                    elif node.site and not node.cable:
                        destination = node.site
                        break
                else:
                    # No peer CircuitTermination exists; halt the trace
                    break

            # Anything else marks the end of the path
            else:
                destination = peer_termination
                break

        if destination is None:
            is_active = False

        return cls(
            origin=origin,
            destination=destination,
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
        for node in self.path:
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
        for node in self.path:
            ct_id, object_id = decompile_path_node(node)
            path.append(prefetched[ct_id][object_id])

        return path

    @property
    def last_node(self):
        """
        Return either the destination or the last node within the path.
        """
        return self.destination or path_node_to_object(self.path[-1])

    def get_cable_ids(self):
        """
        Return all Cable IDs within the path.
        """
        cable_ct = ContentType.objects.get_for_model(Cable).pk
        cable_ids = []

        for node in self.path:
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
        rearport = path_node_to_object(self.path[-1])

        return FrontPort.objects.filter(rear_port=rearport)
