import itertools
import logging

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.dispatch import Signal
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from dcim.choices import *
from dcim.constants import *
from dcim.exceptions import UnsupportedCablePath
from dcim.fields import PathField
from dcim.utils import decompile_path_node, object_to_path_node
from netbox.choices import ColorChoices
from netbox.models import ChangeLoggedModel, PrimaryModel
from utilities.conversion import to_meters
from utilities.exceptions import AbortRequest
from utilities.fields import ColorField, GenericArrayForeignKey
from utilities.querysets import RestrictedQuerySet
from utilities.serialization import deserialize_object, serialize_object
from wireless.models import WirelessLink

from .device_components import FrontPort, PathEndpoint, PortMapping, RearPort

__all__ = (
    'Cable',
    'CablePath',
    'CableTermination',
)

logger = logging.getLogger(f'netbox.{__name__}')

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
    profile = models.CharField(
        verbose_name=_('profile'),
        max_length=50,
        choices=CableProfileChoices,
        blank=True,
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

    clone_fields = ('tenant', 'type', 'profile')

    class Meta:
        ordering = ('pk',)
        verbose_name = _('cable')
        verbose_name_plural = _('cables')

    def __init__(self, *args, a_terminations=None, b_terminations=None, **kwargs):
        super().__init__(*args, **kwargs)

        # A copy of the PK to be used by __str__ in case the object is deleted
        self._pk = self.__dict__.get('id')

        # Cache the original profile & status so we can check later whether either has been changed
        self._orig_status = self.__dict__.get('status')
        self._orig_profile = self.__dict__.get('profile')

        self._terminations_modified = False

        # Assign or retrieve A/B terminations
        if a_terminations:
            self.a_terminations = a_terminations
        if b_terminations:
            self.b_terminations = b_terminations

    def __str__(self):
        pk = self.pk or self._pk
        return self.label or f'#{pk}'

    def get_status_color(self):
        return LinkStatusChoices.colors.get(self.status)

    @property
    def profile_class(self):
        from dcim import cable_profiles
        return {
            CableProfileChoices.SINGLE_1C1P: cable_profiles.Single1C1PCableProfile,
            CableProfileChoices.SINGLE_1C2P: cable_profiles.Single1C2PCableProfile,
            CableProfileChoices.SINGLE_1C4P: cable_profiles.Single1C4PCableProfile,
            CableProfileChoices.SINGLE_1C6P: cable_profiles.Single1C6PCableProfile,
            CableProfileChoices.SINGLE_1C8P: cable_profiles.Single1C8PCableProfile,
            CableProfileChoices.SINGLE_1C12P: cable_profiles.Single1C12PCableProfile,
            CableProfileChoices.SINGLE_1C16P: cable_profiles.Single1C16PCableProfile,
            CableProfileChoices.TRUNK_2C1P: cable_profiles.Trunk2C1PCableProfile,
            CableProfileChoices.TRUNK_2C2P: cable_profiles.Trunk2C2PCableProfile,
            CableProfileChoices.TRUNK_2C4P: cable_profiles.Trunk2C4PCableProfile,
            CableProfileChoices.TRUNK_2C4P_SHUFFLE: cable_profiles.Trunk2C4PShuffleCableProfile,
            CableProfileChoices.TRUNK_2C6P: cable_profiles.Trunk2C6PCableProfile,
            CableProfileChoices.TRUNK_2C8P: cable_profiles.Trunk2C8PCableProfile,
            CableProfileChoices.TRUNK_2C12P: cable_profiles.Trunk2C12PCableProfile,
            CableProfileChoices.TRUNK_4C1P: cable_profiles.Trunk4C1PCableProfile,
            CableProfileChoices.TRUNK_4C2P: cable_profiles.Trunk4C2PCableProfile,
            CableProfileChoices.TRUNK_4C4P: cable_profiles.Trunk4C4PCableProfile,
            CableProfileChoices.TRUNK_4C4P_SHUFFLE: cable_profiles.Trunk4C4PShuffleCableProfile,
            CableProfileChoices.TRUNK_4C6P: cable_profiles.Trunk4C6PCableProfile,
            CableProfileChoices.TRUNK_4C8P: cable_profiles.Trunk4C8PCableProfile,
            CableProfileChoices.TRUNK_8C4P: cable_profiles.Trunk8C4PCableProfile,
            CableProfileChoices.BREAKOUT_1C4P_4C1P: cable_profiles.Breakout1C4Px4C1PCableProfile,
            CableProfileChoices.BREAKOUT_1C6P_6C1P: cable_profiles.Breakout1C6Px6C1PCableProfile,
            CableProfileChoices.BREAKOUT_2C4P_8C1P_SHUFFLE: cable_profiles.Breakout2C4Px8C1PShuffleCableProfile,
        }.get(self.profile)

    def _get_x_terminations(self, side):
        """
        Return the terminating objects for the given cable end (A or B).
        """
        if side not in (CableEndChoices.SIDE_A, CableEndChoices.SIDE_B):
            raise ValueError(f"Unknown cable side: {side}")
        attr = f'_{side.lower()}_terminations'

        if hasattr(self, attr):
            return getattr(self, attr)
        if not self.pk:
            return []
        return [
            # Query self.terminations.all() to leverage cached results
            ct.termination for ct in self.terminations.all() if ct.cable_end == side
        ]

    def _set_x_terminations(self, side, value):
        """
        Set the terminating objects for the given cable end (A or B).
        """
        if side not in (CableEndChoices.SIDE_A, CableEndChoices.SIDE_B):
            raise ValueError(f"Unknown cable side: {side}")
        _attr = f'_{side.lower()}_terminations'

        # If the provided value is a list of CableTermination IDs, resolve them
        # to their corresponding termination objects.
        if all(isinstance(item, int) for item in value):
            value = [
                ct.termination for ct in CableTermination.objects.filter(pk__in=value).prefetch_related('termination')
            ]

        if not self.pk or getattr(self, _attr, []) != list(value):
            self._terminations_modified = True

        setattr(self, _attr, value)

    @property
    def a_terminations(self):
        return self._get_x_terminations(CableEndChoices.SIDE_A)

    @a_terminations.setter
    def a_terminations(self, value):
        self._set_x_terminations(CableEndChoices.SIDE_A, value)

    @property
    def b_terminations(self):
        return self._get_x_terminations(CableEndChoices.SIDE_B)

    @b_terminations.setter
    def b_terminations(self, value):
        self._set_x_terminations(CableEndChoices.SIDE_B, value)

    @property
    def color_name(self):
        color_name = ""
        for hex_code, label in ColorChoices.CHOICES:
            if hex_code.lower() == self.color.lower():
                color_name = str(label)

        return color_name

    def clean(self):
        super().clean()

        # Validate length and length_unit
        if self.length is not None and not self.length_unit:
            raise ValidationError(_("Must specify a unit when setting a cable length"))

        if self._state.adding and self.pk is None and (not self.a_terminations or not self.b_terminations):
            raise ValidationError(_("Must define A and B terminations when creating a new cable."))

        # Validate terminations against the assigned cable profile (if any)
        if self.profile:
            self.profile_class().clean(self)

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

    def save(self, *args, force_insert=False, force_update=False, using=None, update_fields=None):
        _created = self.pk is None

        # Store the given length (if any) in meters for use in database ordering
        if self.length is not None and self.length_unit:
            self._abs_length = to_meters(self.length, self.length_unit)
        else:
            self._abs_length = None

        # Clear length_unit if no length is defined
        if self.length is None:
            self.length_unit = None

        # If this is a new Cable, save it before attempting to create its CableTerminations
        if self._state.adding:
            super().save(*args, force_insert=True, using=using, update_fields=update_fields)
            # Update the private PK used in __str__()
            self._pk = self.pk

        if self._orig_profile != self.profile:
            print(f'profile changed from {self._orig_profile} to {self.profile}')
            self.update_terminations(force=True)
        elif self._terminations_modified:
            self.update_terminations()

        super().save(*args, force_update=True, using=using, update_fields=update_fields)

        try:
            trace_paths.send(Cable, instance=self, created=_created)
        except UnsupportedCablePath as e:
            raise AbortRequest(e)

    def serialize_object(self, exclude=None):
        data = serialize_object(self, exclude=exclude or [])

        # Add A & B terminations to the serialized data
        a_terminations, b_terminations = self.get_terminations()
        data['a_terminations'] = sorted([ct.pk for ct in a_terminations.values()])
        data['b_terminations'] = sorted([ct.pk for ct in b_terminations.values()])

        return data

    @classmethod
    def deserialize_object(cls, data, pk=None):
        a_terminations = data.pop('a_terminations', [])
        b_terminations = data.pop('b_terminations', [])

        instance = deserialize_object(cls, data, pk=pk)

        # Assign A & B termination objects to the Cable instance
        queryset = CableTermination.objects.prefetch_related('termination')
        instance.a_terminations = [
            ct.termination for ct in queryset.filter(pk__in=a_terminations)
        ]
        instance.b_terminations = [
            ct.termination for ct in queryset.filter(pk__in=b_terminations)
        ]

        return instance

    def get_terminations(self):
        """
        Return two dictionaries mapping A & B side terminating objects to their corresponding CableTerminations
        for this Cable.
        """
        a_terminations = {}
        b_terminations = {}

        for ct in CableTermination.objects.filter(cable=self).prefetch_related('termination'):
            if ct.cable_end == CableEndChoices.SIDE_A:
                a_terminations[ct.termination] = ct
            else:
                b_terminations[ct.termination] = ct

        return a_terminations, b_terminations

    def update_terminations(self, force=False):
        """
        Create/delete CableTerminations for this Cable to reflect its current state.

        Args:
            force: Force the recreation of all CableTerminations, even if no changes have been made. Needed e.g. when
                altering a Cable's assigned profile.
        """
        a_terminations, b_terminations = self.get_terminations()

        # Delete any stale CableTerminations
        for termination, ct in a_terminations.items():
            if force or (termination.pk and termination not in self.a_terminations):
                ct.delete()
        for termination, ct in b_terminations.items():
            if force or (termination.pk and termination not in self.b_terminations):
                ct.delete()

        # Save any new CableTerminations
        profile = self.profile_class() if self.profile else None
        for i, termination in enumerate(self.a_terminations, start=1):
            if force or not termination.pk or termination not in a_terminations:
                connector = positions = None
                if profile:
                    connector = i
                    positions = profile.get_position_list(profile.a_connectors[i])
                CableTermination(
                    cable=self,
                    cable_end=CableEndChoices.SIDE_A,
                    connector=connector,
                    positions=positions,
                    termination=termination
                ).save()
        for i, termination in enumerate(self.b_terminations, start=1):
            if force or not termination.pk or termination not in b_terminations:
                connector = positions = None
                if profile:
                    connector = i
                    positions = profile.get_position_list(profile.b_connectors[i])
                CableTermination(
                    cable=self,
                    cable_end=CableEndChoices.SIDE_B,
                    connector=connector,
                    positions=positions,
                    termination=termination
                ).save()


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
        on_delete=models.PROTECT,
        related_name='+'
    )
    termination_id = models.PositiveBigIntegerField()
    termination = GenericForeignKey(
        ct_field='termination_type',
        fk_field='termination_id'
    )
    connector = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=(
            MinValueValidator(CABLE_CONNECTOR_MIN),
            MaxValueValidator(CABLE_CONNECTOR_MAX)
        ),
    )
    positions = ArrayField(
        base_field=models.PositiveSmallIntegerField(
            validators=(
                MinValueValidator(CABLE_POSITION_MIN),
                MaxValueValidator(CABLE_POSITION_MAX)
            )
        ),
        blank=True,
        null=True,
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
        ordering = ('cable', 'cable_end', 'connector', 'pk')
        constraints = (
            models.UniqueConstraint(
                fields=('termination_type', 'termination_id'),
                name='%(app_label)s_%(class)s_unique_termination'
            ),
            models.UniqueConstraint(
                fields=('cable', 'cable_end', 'connector'),
                name='%(app_label)s_%(class)s_unique_connector'
            ),
        )
        verbose_name = _('cable termination')
        verbose_name_plural = _('cable terminations')

    def __str__(self):
        return f'Cable {self.cable} to {self.termination}'

    def clean(self):
        super().clean()

        # Disallow connecting a cable to any termination object that is
        # explicitly flagged as "mark connected".
        termination = getattr(self, 'termination', None)
        if termination is not None and getattr(termination, "mark_connected", False):
            raise ValidationError(
                _("Cannot connect a cable to {obj_parent} > {obj} because it is marked as connected.").format(
                    obj_parent=termination.parent_object,
                    obj=termination,
                )
            )

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
                _("Duplicate termination found for {app_label}.{model} {termination_id}: cable {cable_pk}").format(
                    app_label=self.termination_type.app_label,
                    model=self.termination_type.model,
                    termination_id=self.termination_id,
                    cable_pk=existing_termination.cable.pk
                )
            )
        # Validate the interface type (if applicable)
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
        termination.set_cable_termination(self)
        termination.save()

    def delete(self, *args, **kwargs):

        # Delete the cable association on the terminating object
        termination = self.termination._meta.model.objects.get(pk=self.termination_id)
        termination.snapshot()
        termination.clear_cable_termination(self)
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

    def delete(self, *args, **kwargs):
        # Mirror save() - clear _path on origins to prevent stale references
        # in table views that render _path.destinations
        if self.path:
            origin_model = self.origin_type.model_class()
            origin_ids = [decompile_path_node(node)[1] for node in self.path[0]]
            origin_model.objects.filter(pk__in=origin_ids, _path=self.pk).update(_path=None)

        super().delete(*args, **kwargs)

    @property
    def origin_type(self):
        if self.path:
            ct_id, _ = decompile_path_node(self.path[0][0])
            return ContentType.objects.get_for_id(ct_id)
        return None

    @property
    def destination_type(self):
        if self.is_complete:
            ct_id, _ = decompile_path_node(self.path[-1][0])
            return ContentType.objects.get_for_id(ct_id)
        return None

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
        from circuits.models import Circuit, CircuitTermination

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

        logger.debug(f'Tracing cable path from {terminations}...')

        segment = 0
        while terminations:
            segment += 1
            logger.debug(f'[Path segment #{segment}] Position stack: {position_stack}')
            logger.debug(f'[Path segment #{segment}] Local terminations: {terminations}')

            # Terminations must all be of the same type
            if not all(isinstance(t, type(terminations[0])) for t in terminations[1:]):
                raise UnsupportedCablePath(_("All mid-span terminations must have the same termination type"))

            # All mid-span terminations must all be attached to the same device
            if (
                not isinstance(terminations[0], PathEndpoint) and
                not isinstance(terminations[0].parent_object, Circuit) and
                not all(t.parent_object == terminations[0].parent_object for t in terminations[1:])
            ):
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
            # If not null, push cable position onto the stack
            if isinstance(terminations[0], PathEndpoint) and terminations[0].cable_positions:
                position_stack.append([terminations[0].cable_positions[0]])

            # Step 2: Determine the attached links (Cable or WirelessLink), if any
            links = list(dict.fromkeys(
                termination.link for termination in terminations if termination.link is not None
            ))
            logger.debug(f'[Path segment #{segment}] Links: {links}')
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
                # Profile-based tracing
                if links[0].profile:
                    cable_profile = links[0].profile_class()
                    position = position_stack.pop()[0] if position_stack else None
                    term, position = cable_profile.get_peer_termination(terminations[0], position)
                    remote_terminations = [term]
                    position_stack.append([position])

                # Legacy (positionless) behavior
                else:
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

            logger.debug(f'[Path segment #{segment}] Remote terminations: {remote_terminations}')

            # Remote Terminations must all be of the same type, otherwise return a split path
            if not all(isinstance(t, type(remote_terminations[0])) for t in remote_terminations[1:]):
                is_complete = False
                is_split = True
                logger.debug('Remote termination types differ; aborting trace.')
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
                if remote_terminations[0].positions > 1 and position_stack:
                    positions = position_stack.pop()
                    q_filter = Q()
                    for rt in remote_terminations:
                        q_filter |= Q(front_port=rt, front_port_position__in=positions)
                    port_mappings = PortMapping.objects.filter(q_filter)
                elif remote_terminations[0].positions > 1:
                    is_split = True
                    logger.debug(
                        'Encountered front port mapped to multiple rear ports but position stack is empty; aborting '
                        'trace.'
                    )
                    break
                else:
                    port_mappings = PortMapping.objects.filter(front_port__in=remote_terminations)
                if not port_mappings:
                    break

                # Compile the list of RearPorts without duplication or altering their ordering
                terminations = list(dict.fromkeys(mapping.rear_port for mapping in port_mappings))
                if any(t.positions > 1 for t in terminations):
                    position_stack.append([mapping.rear_port_position for mapping in port_mappings])

            elif isinstance(remote_terminations[0], RearPort):
                # Follow RearPorts to their corresponding FrontPorts
                if remote_terminations[0].positions > 1 and position_stack:
                    positions = position_stack.pop()
                    q_filter = Q()
                    for rt in remote_terminations:
                        q_filter |= Q(rear_port=rt, rear_port_position__in=positions)
                    port_mappings = PortMapping.objects.filter(q_filter)
                elif remote_terminations[0].positions > 1:
                    is_split = True
                    logger.debug(
                        'Encountered rear port mapped to multiple front ports but position stack is empty; aborting '
                        'trace.'
                    )
                    break
                else:
                    port_mappings = PortMapping.objects.filter(rear_port__in=remote_terminations)
                if not port_mappings:
                    break

                # Compile the list of FrontPorts without duplication or altering their ordering
                terminations = list(dict.fromkeys(mapping.front_port for mapping in port_mappings))
                if any(t.positions > 1 for t in terminations):
                    position_stack.append([mapping.front_port_position for mapping in port_mappings])

            elif isinstance(remote_terminations[0], CircuitTermination):
                # Follow a CircuitTermination to its corresponding CircuitTermination (A to Z or vice versa)
                qs = Q()
                for remote_termination in remote_terminations:
                    qs |= Q(
                        circuit=remote_termination.circuit,
                        term_side='Z' if remote_termination.term_side == 'A' else 'A'
                    )

                # Get all circuit terminations
                circuit_terminations = CircuitTermination.objects.filter(qs)

                if not circuit_terminations.exists():
                    break
                if all([ct._provider_network for ct in circuit_terminations]):
                    # Circuit terminates to a ProviderNetwork
                    path.extend([
                        [object_to_path_node(ct) for ct in circuit_terminations],
                        [object_to_path_node(ct._provider_network) for ct in circuit_terminations],
                    ])
                    is_complete = True
                    break
                if all([ct.termination and not ct.cable for ct in circuit_terminations]):
                    # Circuit terminates to a Region/Site/etc.
                    path.extend([
                        [object_to_path_node(ct) for ct in circuit_terminations],
                        [object_to_path_node(ct.termination) for ct in circuit_terminations],
                    ])
                    break
                if any([ct.cable in links for ct in circuit_terminations]):
                    # No valid path
                    is_split = True
                    break

                terminations = circuit_terminations

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
                    logger.warning('Encountered an unsupported topology; aborting trace.')
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
            return [
                mapping.front_port for mapping in
                PortMapping.objects.filter(rear_port__in=nodes).prefetch_related('front_port')
            ]
        # Cable terminating to multiple FrontPorts mapped to different
        # RearPorts connected to different cables
        if type(nodes[0]) is FrontPort:
            return [
                mapping.rear_port for mapping in
                PortMapping.objects.filter(front_port__in=nodes).prefetch_related('rear_port')
            ]
        # Cable terminating to multiple CircuitTerminations
        if type(nodes[0]) is CircuitTermination:
            return [
                ct.get_peer_termination() for ct in nodes
            ]
        return []

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
