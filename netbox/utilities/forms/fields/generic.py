import django_filters
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms.boundfield import BoundField
from django.utils.translation import gettext_lazy as _

from utilities.forms.widgets import APISelect, GenericObjectSelect, HTMXSelect
from utilities.views import get_action_url

from .content_types import ContentTypeChoiceField
from .dynamic import DynamicModelChoiceField

__all__ = (
    'GenericObjectChoiceField',
)


class GenericObjectChoiceField(forms.MultiValueField):
    """
    Select an object for assignment to a generic foreign key.

    Renders a content-type selector (HTMXSelect) plus an API-backed object selector (APISelect) as a single
    field. Changing the content type re-renders the form so the object selector is rebuilt for the new model.
    The field's cleaned value is the selected model instance (or None); assignment to the GFK descriptor is
    handled by GenericObjectFormMixin (or the consuming form's clean()).

    Args:
        content_type_queryset: Queryset of ContentTypes the user may choose from.
        query_params: Optional dict of static/dynamic ($field) query params forwarded to the object selector.
        selector: If True, expose the advanced object-selector modal for the object subwidget.
        gfk_name: Name of the model's GenericForeignKey descriptor, if it differs from the form field name.
        hx_method: HTTP method for the content-type HTMXSelect ('get' for model forms, 'post' for bulk edit).
        hx_include_id: HTML id of the container whose fields are included in the HTMX request. This should
            generally remain 'form_fields' so dependent fields can resolve against the full form state.
        hx_target_id: html_id of the enclosing FieldSet for an HTMX partial swap. If omitted, the whole
            #form_fields container is re-rendered.
    """
    default_error_messages = {
        'incomplete': _("Both an object type and an object must be specified."),
        'invalid_object_type': _("Invalid object type."),
    }

    def __init__(
        self, *, content_type_queryset, query_params=None, selector=False, gfk_name=None,
        hx_method='get', hx_include_id='form_fields', hx_target_id=None, **kwargs
    ):
        self.content_type_queryset = content_type_queryset
        self.query_params = query_params or {}
        self.selector = selector
        self.gfk_name = gfk_name
        self.hx_target_id = hx_target_id
        self.selected_model = None

        # NetBox's current HTMXSelect separates the include source from the swap target. Always include the
        # full form so server-side dependent-field resolution sees every field, while optionally targeting only
        # the containing fieldset for the swap. Bulk edit forms keep the historical hx-select=#form_fields path.
        htmx_attrs = {}
        if hx_target_id is None and hx_method.lower() == 'post':
            htmx_attrs['hx-select'] = '#form_fields'
        content_type_widget = HTMXSelect(
            method=hx_method,
            hx_include_id=hx_include_id,
            hx_target_id=hx_target_id,
            attrs=htmx_attrs or None,
        )
        object_widget = APISelect()

        fields = (
            ContentTypeChoiceField(queryset=content_type_queryset, required=False, widget=content_type_widget),
            # Empty placeholder until a content type is chosen; _configure_object_field installs the real
            # (and possibly permission-restricted) queryset.
            DynamicModelChoiceField(
                queryset=ContentType.objects.none(), required=False, selector=selector, widget=object_widget
            ),
        )
        widget = GenericObjectSelect(content_type_widget=content_type_widget, object_widget=object_widget)

        super().__init__(fields=fields, require_all_fields=False, widget=widget, **kwargs)

    @property
    def content_type_field(self):
        return self.fields[0]

    @property
    def object_field(self):
        return self.fields[1]

    @property
    def queryset(self):
        # Exposed at the top level so restrict_form_fields() (which only inspects top-level fields) can apply
        # object-permission restrictions to the nested object selector.
        return self.object_field.queryset

    @queryset.setter
    def queryset(self, queryset):
        self.object_field.queryset = queryset
        self.object_field.widget.choices = self.object_field.choices

    def _get_object_queryset(self, model):
        # Preserve a queryset already restricted by restrict_form_fields() when it targets the selected model;
        # otherwise start from the model's default manager.
        queryset = self.object_field.queryset
        if getattr(queryset, 'model', None) is model:
            return queryset.all()
        return model.objects.all()

    def _sync_widget_refs(self):
        # The form metaclass deep-copies the field, its subfields, and the MultiWidget independently. Re-point
        # the subfields at the MultiWidget's widgets so attrs we set on the object subfield are actually rendered.
        # Re-assign choices as well: Select widgets keep their own choices iterator, and a copied MultiWidget
        # subwidget can otherwise render as an empty Tom Select even though the subfield queryset is populated.
        self.content_type_field.widget = self.widget.widgets[0]
        self.object_field.widget = self.widget.widgets[1]
        self.content_type_field.widget.choices = self.content_type_field.choices
        self.object_field.widget.choices = self.object_field.choices

    def _resolve_subvalue(self, form, field_name, suffix):
        # Read the current value of one subwidget across the three paths: bound submit/POST re-render,
        # unbound HTMX GET re-render (values arrive as initial under the subwidget keys), and normal edit
        # (field-level initial holds the related object instance).
        key = f'{field_name}_{suffix}'
        if form.is_bound and key in form.data:
            return form.data.get(key)
        if key in form.initial:
            return form.initial.get(key)
        obj = form.initial.get(field_name, self.initial)
        if obj in self.empty_values or not hasattr(obj, '_meta'):
            return None
        if suffix == 'content_type':
            return ContentType.objects.get_for_model(obj).pk
        return obj.pk

    def _get_content_type(self, value):
        if value in self.empty_values:
            return None
        try:
            return self.content_type_queryset.get(pk=value)
        except (ObjectDoesNotExist, TypeError, ValueError):
            return None

    def _configure_object_field(self, content_type, object_value=None):
        # Clear any state left over from a previously selected content type
        widget = self.object_field.widget
        for attr in ('data-url', 'data-dynamic-params', 'data-static-params', 'disabled', 'selector'):
            widget.attrs.pop(attr, None)
        widget.dynamic_params = {}
        widget.static_params = {}
        self.selected_model = None

        model = content_type.model_class() if content_type else None
        if model is None:
            # No type selected: keep an empty placeholder queryset and disable the object selector.
            self.object_field.queryset = ContentType.objects.none()
            self.object_field.widget.choices = self.object_field.choices
            widget.attrs['disabled'] = 'disabled'
            return None

        self.selected_model = model

        # Narrow the queryset to the current value to avoid loading the entire table for rendering
        queryset = self._get_object_queryset(model)
        if object_value in self.empty_values:
            queryset = queryset.none()
        else:
            lookup = getattr(self.object_field, 'to_field_name', None) or 'pk'
            try:
                queryset = django_filters.ModelChoiceFilter(field_name=lookup).filter(queryset, object_value)
            except (TypeError, ValueError):
                queryset = queryset.none()
        self.object_field.queryset = queryset
        self.object_field.widget.choices = self.object_field.choices

        widget.attrs['data-url'] = get_action_url(model, action='list', rest_api=True)
        if self.query_params:
            widget.add_query_params(self.query_params)
        if self.selector:
            widget.attrs['selector'] = model._meta.label_lower

        return model

    def prepare(self, form, field_name):
        """Configure the object selector for the field's current content type (called during rendering)."""
        self._sync_widget_refs()

        # Clear the paired object selection client-side when the content type changes, so a stale object_id
        # cannot cross model boundaries on the HTMX re-render (a Site pk must not resurface as a Region pk).
        self.content_type_field.widget.attrs['hx-on::config-request'] = (
            f"event.detail.parameters['{field_name}_object_id'] = ''"
        )

        content_type_value = self._resolve_subvalue(form, field_name, 'content_type')
        object_value = self._resolve_subvalue(form, field_name, 'object_id')
        self._configure_object_field(self._get_content_type(content_type_value), object_value)

        # On an unbound HTMX GET re-render the submitted values live under the subwidget keys, not under the
        # field name; seed the field initial so the subwidgets render the current selection.
        if not form.is_bound:
            self.initial = [content_type_value, object_value]

    def get_bound_field(self, form, field_name):
        self.prepare(form, field_name)
        return BoundField(form, self, field_name)

    def clean(self, value):
        self._sync_widget_refs()
        value = value or []
        content_type_value = value[0] if len(value) > 0 else None
        object_value = value[1] if len(value) > 1 else None

        if content_type_value in self.empty_values and object_value in self.empty_values:
            self._configure_object_field(None)
            if self.required:
                raise ValidationError(self.error_messages['required'], code='required')
            return None

        if content_type_value in self.empty_values or object_value in self.empty_values:
            # Name the selected type when the object is missing so the message is actionable.
            if content_type_value not in self.empty_values:
                content_type = self._get_content_type(content_type_value)
                if content_type is not None and (model := content_type.model_class()) is not None:
                    raise ValidationError(
                        _("Please select a {object_type}.").format(object_type=model._meta.verbose_name),
                        code='incomplete',
                    )
            raise ValidationError(self.error_messages['incomplete'], code='incomplete')

        # Validates the content type is within the allowed queryset
        content_type = self.content_type_field.clean(content_type_value)
        model = self._configure_object_field(content_type, object_value)
        if model is None:
            raise ValidationError(self.error_messages['invalid_object_type'], code='invalid_object_type')

        # Validates the object exists (queryset was narrowed to the value)
        return self.object_field.clean(object_value)

    def compress(self, data_list):
        # clean() returns the validated object directly; compress() is intentionally bypassed.
        raise NotImplementedError("GenericObjectChoiceField.clean() returns the selected object directly.")
