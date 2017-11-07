from __future__ import unicode_literals

import django_filters
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from dcim.models import Site
from .constants import CF_TYPE_SELECT
from .models import CustomField, Graph, ExportTemplate, TopologyMap, UserAction


class CustomFieldFilter(django_filters.Filter):
    """
    Filter objects by the presence of a CustomFieldValue. The filter's name is used as the CustomField name.
    """

    def __init__(self, cf_type, *args, **kwargs):
        self.cf_type = cf_type
        super(CustomFieldFilter, self).__init__(*args, **kwargs)

    def filter(self, queryset, value):

        # Skip filter on empty value
        if not value.strip():
            return queryset

        # Selection fields get special treatment (values must be integers)
        if self.cf_type == CF_TYPE_SELECT:
            try:
                # Treat 0 as None
                if int(value) == 0:
                    return queryset.exclude(
                        custom_field_values__field__name=self.name,
                    )
                # Match on exact CustomFieldChoice PK
                else:
                    return queryset.filter(
                        custom_field_values__field__name=self.name,
                        custom_field_values__serialized_value=value,
                    )
            except ValueError:
                return queryset.none()

        return queryset.filter(
            custom_field_values__field__name=self.name,
            custom_field_values__serialized_value__icontains=value,
        )


class CustomFieldFilterSet(django_filters.FilterSet):
    """
    Dynamically add a Filter for each CustomField applicable to the parent model.
    """

    def __init__(self, *args, **kwargs):
        super(CustomFieldFilterSet, self).__init__(*args, **kwargs)

        obj_type = ContentType.objects.get_for_model(self._meta.model)
        custom_fields = CustomField.objects.filter(obj_type=obj_type, is_filterable=True)
        for cf in custom_fields:
            self.filters['cf_{}'.format(cf.name)] = CustomFieldFilter(name=cf.name, cf_type=cf.type)


class GraphFilter(django_filters.FilterSet):

    class Meta:
        model = Graph
        fields = ['type', 'name']


class ExportTemplateFilter(django_filters.FilterSet):

    class Meta:
        model = ExportTemplate
        fields = ['content_type', 'name']


class TopologyMapFilter(django_filters.FilterSet):
    site_id = django_filters.ModelMultipleChoiceFilter(
        name='site',
        queryset=Site.objects.all(),
        label='Site',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    class Meta:
        model = TopologyMap
        fields = ['name', 'slug']


class UserActionFilter(django_filters.FilterSet):
    username = django_filters.ModelMultipleChoiceFilter(
        name='user__username',
        queryset=User.objects.all(),
        to_field_name='username',
    )

    class Meta:
        model = UserAction
        fields = ['user']
