from django.db import models
from django.db.models import Count, ProtectedError, Q
from django.utils.translation import gettext_lazy as _

from netbox.models import NestedGroupModel, PrimaryModel
from netbox.models.features import ContactsMixin

__all__ = (
    'Tenant',
    'TenantGroup',
)


class TenantGroup(NestedGroupModel):
    """
    An arbitrary collection of Tenants.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True,
        db_collation="natural_sort"
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=100,
        unique=True
    )

    class Meta:
        ordering = ['name']
        # Empty tuple triggers Django migration detection for MPTT indexes
        # (see #21016, django-mptt/django-mptt#682)
        indexes = ()
        verbose_name = _('tenant group')
        verbose_name_plural = _('tenant groups')

    def delete(self, *args, **kwargs):
        # Ungrouping the tenants of this group and its descendants can violate tenant name and slug uniqueness.
        ungrouped = Tenant.objects.filter(
            Q(group__isnull=True) | Q(group__in=self.get_descendants(include_self=True))
        )
        duplicate_names = ungrouped.values('name').annotate(count=Count('pk')).filter(count__gt=1).values('name')
        duplicate_slugs = ungrouped.values('slug').annotate(count=Count('pk')).filter(count__gt=1).values('slug')
        if conflicts := set(ungrouped.filter(Q(name__in=duplicate_names) | Q(slug__in=duplicate_slugs))):
            raise ProtectedError(
                _(
                    "Unable to delete tenant group {tenant_group}. Ungrouping its tenants, including those of any "
                    "nested groups, would create duplicate tenant names or slugs."
                ).format(tenant_group=self),
                conflicts,
            )

        return super().delete(*args, **kwargs)


class Tenant(ContactsMixin, PrimaryModel):
    """
    A Tenant represents an organization served by the NetBox owner. This is typically a customer or an internal
    department.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        db_collation="natural_sort"
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=100
    )
    group = models.ForeignKey(
        to='tenancy.TenantGroup',
        on_delete=models.SET_NULL,
        related_name='tenants',
        blank=True,
        null=True
    )

    clone_fields = (
        'group', 'description',
    )

    class Meta:
        ordering = ['name']
        constraints = (
            models.UniqueConstraint(
                fields=('group', 'name'),
                name='%(app_label)s_%(class)s_unique_group_name',
                violation_error_message=_("Tenant name must be unique per group.")
            ),
            models.UniqueConstraint(
                fields=('name',),
                name='%(app_label)s_%(class)s_unique_name',
                condition=Q(group__isnull=True)
            ),
            models.UniqueConstraint(
                fields=('group', 'slug'),
                name='%(app_label)s_%(class)s_unique_group_slug',
                violation_error_message=_("Tenant slug must be unique per group.")
            ),
            models.UniqueConstraint(
                fields=('slug',),
                name='%(app_label)s_%(class)s_unique_slug',
                condition=Q(group__isnull=True)
            ),
        )
        verbose_name = _('tenant')
        verbose_name_plural = _('tenants')

    def __str__(self):
        return self.name
