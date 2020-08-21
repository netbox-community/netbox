from collections import OrderedDict

from django.db.models import Q, QuerySet

from utilities.querysets import RestrictedQuerySet


class CustomFieldQueryset:
    """
    Annotate custom fields on objects within a QuerySet.
    """
    def __init__(self, queryset, custom_fields):
        self.queryset = queryset
        self.model = queryset.model
        self.custom_fields = custom_fields

    def __iter__(self):
        for obj in self.queryset:
            values_dict = {cfv.field_id: cfv.value for cfv in obj.custom_field_values.all()}
            obj.custom_fields = OrderedDict([(field, values_dict.get(field.pk)) for field in self.custom_fields])
            yield obj


class ConfigContextQuerySet(RestrictedQuerySet):

    def get_for_object(self, obj):
        """
        Return all applicable ConfigContexts for a given object. Only active ConfigContexts will be included.
        """

        # `device_role` for Device; `role` for VirtualMachine
        role = getattr(obj, 'device_role', None) or obj.role

        # Virtualization cluster for VirtualMachine
        cluster = getattr(obj, 'cluster', None)
        cluster_group = getattr(cluster, 'group', None)

        # Get the group of the assigned tenant, if any
        tenant_group = obj.tenant.group if obj.tenant else None

        # Match against the directly assigned region as well as any parent regions.
        region = getattr(obj.site, 'region', None)
        if region:
            regions = region.get_ancestors(include_self=True)
        else:
            regions = []

        return self.filter(
            Q(regions__in=regions) | Q(regions=None),
            Q(sites=obj.site) | Q(sites=None),
            Q(roles=role) | Q(roles=None),
            Q(platforms=obj.platform) | Q(platforms=None),
            Q(cluster_groups=cluster_group) | Q(cluster_groups=None),
            Q(clusters=cluster) | Q(clusters=None),
            Q(tenant_groups=tenant_group) | Q(tenant_groups=None),
            Q(tenants=obj.tenant) | Q(tenants=None),
            Q(tags__slug__in=obj.tags.slugs()) | Q(tags=None),
            is_active=True,
        ).order_by('weight', 'name')
