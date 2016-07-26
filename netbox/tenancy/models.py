from django.core.urlresolvers import reverse
from django.db import models

from utilities.models import CreatedUpdatedModel


class TenantGroup(models.Model):
    """
    An arbitrary collection of Tenants.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?group={}".format(reverse('tenancy:tenant_list'), self.slug)


class Tenant(CreatedUpdatedModel):
    """
    A Tenant represents an organization served by the NetBox owner. This is typically a customer or an internal
    department.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    group = models.ForeignKey('TenantGroup', related_name='tenants', on_delete=models.PROTECT)
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ['group', 'name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tenancy:tenant', args=[self.slug])

    def to_csv(self):
        return ','.join([
            self.name,
            self.slug,
            self.group.name,
        ])
