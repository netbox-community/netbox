from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy

from core.models import ObjectType
from extras.choices import *
from extras.models import *
from users.models import Owner, OwnerGroup
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.widgets.misc import RestrictedChoiceLabel

__all__ = (
    'ChangelogMessageMixin',
    'CustomFieldsMixin',
    'OwnerFilterMixin',
    'OwnerMixin',
    'RestrictedRelatedFieldsMixin',
    'SavedFiltersMixin',
    'TagsMixin',
)


class ChangelogMessageMixin(forms.Form):
    """
    Adds an optional field for recording a message on the resulting changelog record(s).
    """
    changelog_message = forms.CharField(
        required=False,
        max_length=200,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Declare changelog_message a meta field
        if hasattr(self, 'meta_fields'):
            self.meta_fields.append('changelog_message')
        else:
            self.meta_fields = ['changelog_message']


class CustomFieldsMixin:
    """
    Extend a Form to include custom field support.

    Attributes:
        model: The model class
    """

    model = None

    def __init__(self, *args, **kwargs):
        self.custom_fields = {}
        self.custom_field_groups = {}

        super().__init__(*args, **kwargs)

        self._append_customfield_fields()

    def _get_content_type(self):
        """
        Return the ObjectType of the form's model.
        """
        if not getattr(self, 'model', None):
            raise NotImplementedError(_("{class_name} must specify a model class.").format(
                class_name=self.__class__.__name__
            ))
        return ObjectType.objects.get_for_model(self.model)

    def _get_custom_fields(self, content_type):
        # Return only custom fields that are not hidden from the UI
        return [
            cf for cf in CustomField.objects.get_for_model(content_type.model_class())
            if cf.ui_editable != CustomFieldUIEditableChoices.HIDDEN
        ]

    def _get_form_field(self, customfield):
        return customfield.to_form_field()

    def _append_customfield_fields(self):
        """
        Append form fields for all CustomFields assigned to this object type.
        """
        for customfield in self._get_custom_fields(self._get_content_type()):
            field_name = f'cf_{customfield.name}'
            self.fields[field_name] = self._get_form_field(customfield)

            # Annotate the field in the list of CustomField form fields
            self.custom_fields[field_name] = customfield
            if customfield.group_name not in self.custom_field_groups:
                self.custom_field_groups[customfield.group_name] = []
            self.custom_field_groups[customfield.group_name].append(field_name)


class SavedFiltersMixin(forms.Form):
    """
    Form mixin for forms that support saved filters.

    Provides a field for selecting a saved filter,
    with options limited to those applicable to the form's model.
    """

    filter_id = DynamicModelMultipleChoiceField(
        queryset=SavedFilter.objects.all(),
        required=False,
        label=_('Saved Filter'),
        query_params={
            'usable': True,
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ensure the underlying <select> has an accessible name even when Tom Select
        # hides the original element (the visible UI is a JS-built combobox).
        self.fields['filter_id'].widget.attrs['aria-label'] = _('Saved filter')

        # Limit saved filters to those applicable to the form's model
        if hasattr(self, 'model'):
            object_type = ObjectType.objects.get_for_model(self.model)
            self.fields['filter_id'].widget.add_query_params({
                'object_type_id': object_type.pk,
            })


class TagsMixin(forms.Form):
    """
    Mixin for forms that support tagging.

    Provides a field for selecting tags,
    with options limited to those applicable to the form's model.
    """

    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label=_('Tags'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit tags to those applicable to the object type
        object_type = ObjectType.objects.get_for_model(self._meta.model)
        if object_type and hasattr(self.fields['tags'].widget, 'add_query_param'):
            self.fields['tags'].widget.add_query_param('for_object_type_id', object_type.pk)


class OwnerMixin(forms.Form):
    """
    Mixin for forms which adds ownership fields.

    Include this mixin in forms for models which
    support owner and/or owner group assignment.
    """

    owner_group = DynamicModelChoiceField(
        label=_('Owner group'),
        queryset=OwnerGroup.objects.all(),
        required=False,
        null_option='None',
        initial_params={'members': '$owner'},
    )
    owner = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        query_params={'group_id': '$owner_group'},
        label=_('Owner'),
    )


class OwnerFilterMixin(forms.Form):
    """
    Mixin for filterset forms which adds owner and owner group filtering.

    Include this mixin in filterset forms for models
    which support owner and/or owner group assignment.
    """

    owner_group_id = DynamicModelMultipleChoiceField(
        queryset=OwnerGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Owner Group'),
    )
    owner_id = DynamicModelMultipleChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'group_id': '$owner_group_id'
        },
        label=_('Owner'),
    )


class RestrictedRelatedFieldsMixin:
    """
    Form mixin that preserves already-assigned related values hidden by object-permission filtering.

    Driven by restrict_form_fields() (or prepare_restricted_queryset_fields() directly): when a field's queryset is
    narrowed so the current value is no longer a choice, that value is shown read-only and preserved on save. Kept as
    a standalone mixin so forms that are not NetBoxModelForms (e.g. component-template forms) can opt in.
    """

    restricted_value_help_text = gettext_lazy(
        'This field includes one or more restricted values that cannot be changed. '
        'They will be preserved when this form is saved.'
    )

    # Maps selector form fields whose current value is stored under a different instance attribute (e.g. a
    # GenericForeignKey). Keys are form field names; entries may declare:
    #   path: dotted attribute path on the instance holding the current value (read from the instance only)
    #   model: expected model class; set when several selector fields share one path (picks the matching field)
    #   lock_fields: controller field names locked alongside the selector when its current value is hidden
    # Merged across the MRO by __init_subclass__: a subclass's entries combine with those declared by base
    # classes (e.g. ScopedForm's 'scope'), the subclass winning on key conflicts, so inherited selectors are
    # never silently dropped.
    restricted_related_selectors = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        merged = {}
        for klass in reversed(cls.__mro__):
            merged.update(klass.__dict__.get('restricted_related_selectors', {}))
        cls.restricted_related_selectors = merged

    def prepare_restricted_queryset_fields(self, restricted_fields, user=None, action='view'):
        """
        Render assigned values which were removed by object-permission filtering as read-only.

        `restricted_fields` maps each restricted field name to its original (pre-restriction) queryset. `user` and
        `action` allow re-checking visibility for GenericForeignKey values whose model differs from the field.

        Security rules:

        * Only values already assigned to the current instance are added back; the rest of the original queryset is
          never exposed.
        * A value is preserved only when the user cannot view it; values excluded by the form's own base queryset
          are left untouched.
        * Restricted current values are read-only and submitted or tampered values for them are ignored.

        Scalar fields (and fields already disabled, e.g. read-only custom fields) are disabled entirely. Editable
        multi-value fields stay editable so the user can manage permitted values, while restricted current members
        are shown as disabled options and preserved server-side in clean().
        """
        # Guard against running twice on the same form (which would double-wrap labels and duplicate help text).
        if getattr(self, '_restricted_queryset_fields_prepared', False) or not self.instance.pk:
            return
        self._restricted_queryset_fields_prepared = True
        self._restricted_preserved_members = {}

        for field_name, original_queryset in restricted_fields.items():
            field = self.fields.get(field_name)
            if field is None:
                continue

            restricted_queryset = getattr(field, 'queryset', None)
            if restricted_queryset is None:
                continue

            current_objects = self._get_restricted_queryset_field_current_objects(field_name, original_queryset)
            if not current_objects:
                continue

            hidden_objects = self._hidden_restricted_objects(
                restricted_queryset, original_queryset, current_objects, user, action,
                declared_selector=field_name in self.restricted_related_selectors,
            )
            if not hidden_objects:
                continue

            if isinstance(field, forms.ModelMultipleChoiceField) and not field.disabled:
                self._prepare_restricted_multiple_field(
                    field_name, field, original_queryset, restricted_queryset, current_objects, hidden_objects
                )
            else:
                self._lock_restricted_queryset_field(field_name, field, current_objects, hidden_objects)

    def _lock_restricted_queryset_field(self, field_name, field, current_objects, hidden_objects):
        """
        Show only the current value(s) and make the whole field read-only for this request.

        Disabling the field makes Django ignore submitted data and clean the initial value instead. The queryset is
        narrowed to the current objects using their own model, so a GenericForeignKey value is preserved even when
        the submitted type field points at a different model. Controller fields declared for the selector
        (lock_fields) are locked too so construct_instance() and clean() cannot corrupt the preserved value.
        """
        multiple = isinstance(field, forms.ModelMultipleChoiceField)
        field.disabled = True
        field.required = False
        field.widget.is_required = False

        field.queryset = self._queryset_for_objects(current_objects)

        if multiple:
            initial = [field.prepare_value(obj) for obj in current_objects]
        else:
            initial = field.prepare_value(current_objects[0])
        field.initial = initial
        self.initial[field_name] = initial

        self._lock_controller_fields(field_name, hidden_objects)
        self._append_restricted_value_help_text(field)

    def _queryset_for_objects(self, objects):
        """
        Build a queryset over the objects' own model restricted to their PKs. A scalar selector holds one type at a
        time, so all objects share a model.
        """
        model = type(objects[0])
        return model.objects.filter(pk__in=[obj.pk for obj in objects])

    def _lock_controller_fields(self, field_name, hidden_objects):
        """
        Lock the controller fields declared for a selector (lock_fields) so a submitted value cannot corrupt the
        preserved assignment. A content type controller is pinned to the current object's own type; any other
        controller is pinned to the value stored on the instance.
        """
        selector = self.restricted_related_selectors.get(field_name) or {}
        for controller_name in selector.get('lock_fields', ()):
            controller = self.fields.get(controller_name)
            if controller is None:
                continue
            queryset = getattr(controller, 'queryset', None)
            if queryset is not None and issubclass(queryset.model, ContentType):
                content_type = ContentType.objects.get_for_model(type(hidden_objects[0]))
                controller.queryset = queryset.model.objects.filter(pk=content_type.pk)
                initial = content_type.pk
            else:
                initial = getattr(self.instance, controller_name, None)
                if isinstance(initial, Model):
                    initial = initial.pk
            controller.disabled = True
            controller.required = False
            controller.widget.is_required = False
            controller.initial = initial
            self.initial[controller_name] = initial

    def _prepare_restricted_multiple_field(
        self, field_name, field, original_queryset, restricted_queryset, current_objects, hidden_objects
    ):
        """
        Keep an editable multi-value field editable while rendering restricted current members as disabled options.

        The user can still add or remove permitted values. Restricted current members are added back to the
        queryset (so the current values validate and render selected) and shown as disabled options as a read-only
        hint. Preservation is enforced in clean(): the hidden members are merged back into the field value
        regardless of what the widget submits. Forged values are still rejected, because only the already-assigned
        restricted members are added to the queryset.
        """
        hidden_pks = [obj.pk for obj in hidden_objects]

        field.required = False
        field.widget.is_required = False

        # Allow the visible choices plus the already-assigned restricted members; expose nothing else. The two sides
        # are disjoint by PK (hidden members are exactly those absent from the restricted queryset), so no DISTINCT.
        hidden_queryset = original_queryset.filter(pk__in=hidden_pks)
        field.queryset = restricted_queryset | hidden_queryset

        # Show all current members selected on render.
        initial = [field.prepare_value(obj) for obj in current_objects]
        field.initial = initial
        self.initial[field_name] = initial

        # Render the restricted members as disabled options (a read-only hint; preservation is enforced server-side).
        self._mark_restricted_choice_labels_disabled(field, hidden_objects)

        # Preserve the hidden members on save without mutating submitted data.
        self._restricted_preserved_members[field_name] = hidden_objects

        self._append_restricted_value_help_text(field)

    def _mark_restricted_choice_labels_disabled(self, field, hidden_objects):
        """
        Wrap label_from_instance so the restricted members render as disabled options.
        """
        hidden_values = {str(field.prepare_value(obj)) for obj in hidden_objects}
        label_from_instance = field.label_from_instance

        def label_with_restricted_marker(obj):
            label = label_from_instance(obj)
            if str(field.prepare_value(obj)) in hidden_values:
                return RestrictedChoiceLabel(label)
            return label

        field.label_from_instance = label_with_restricted_marker

    def _append_restricted_value_help_text(self, field):
        if field.help_text:
            field.help_text = format_html('{} {}', field.help_text, self.restricted_value_help_text)
        else:
            field.help_text = self.restricted_value_help_text

    def _get_objects_from_queryset(self, queryset, pks):
        """
        Return objects for `pks` from `queryset`, preserving order. Used for selectors whose current PKs are known
        to belong to the queryset's model.
        """
        if not pks:
            return []
        objects_by_pk = {str(obj.pk): obj for obj in queryset.filter(pk__in=pks)}
        return [objects_by_pk[str(pk)] for pk in pks if str(pk) in objects_by_pk]

    def _hidden_restricted_objects(self, restricted_queryset, original_queryset, current_objects, user, action,
                                   declared_selector=False):
        """
        Return the subset of `current_objects` the user cannot view (and which were valid choices before
        restriction).

        Objects whose model matches the field are checked against the field's own restricted/original querysets in a
        single pair of queries. Objects of a different model (a GenericForeignKey whose paired type field was changed,
        of which a selector holds at most one) are checked individually against their own model, so a same-PK object
        of another model is never mistaken for the current value.

        For a declared selector (`restricted_related_selectors`), the field queryset is derived from submitted
        controller data and may be empty (a blanked optional type field leaves the selector on its default `.none()`)
        or of the wrong model. The current value is read from the instance, so visibility is always judged against the
        object's own model, never the field queryset.
        """
        field_model = getattr(restricted_queryset, 'model', None)
        if declared_selector:
            same_model = []
            other_model = list(current_objects)
        else:
            same_model = [obj for obj in current_objects if field_model is not None and type(obj) is field_model]
            other_model = [obj for obj in current_objects if field_model is None or type(obj) is not field_model]

        hidden = []
        if same_model:
            pks = [obj.pk for obj in same_model]
            was_choice = set(original_queryset.filter(pk__in=pks).values_list('pk', flat=True))
            visible = set(restricted_queryset.filter(pk__in=pks).values_list('pk', flat=True))
            hidden += [obj for obj in same_model if obj.pk in was_choice and obj.pk not in visible]

        for obj in other_model:
            manager = type(obj).objects
            if user is not None and hasattr(manager, 'restrict'):
                if not manager.restrict(user, action).filter(pk=obj.pk).exists():
                    hidden.append(obj)
            else:
                # Without a user we cannot re-check visibility for a different model, so preserve to avoid data loss.
                hidden.append(obj)

        return hidden

    def _get_restricted_queryset_field_current_objects(self, field_name, original_queryset):
        """
        Return the current assigned objects for a restricted form field, read from the instance (never submitted
        data). Objects carry their true model, so a GenericForeignKey value is never looked up against a model
        chosen from submitted data.
        """
        if selector := self.restricted_related_selectors.get(field_name):
            return self._get_restricted_selector_current_objects(selector)

        if field_name in getattr(self, 'custom_fields', {}):
            pks = self._get_restricted_custom_field_current_pks(field_name)
            return self._get_objects_from_queryset(original_queryset, pks)

        return self._get_current_objects_from_instance(field_name)

    def _get_restricted_selector_current_objects(self, selector):
        """
        Resolve a declared selector's current value by walking its dotted path from the instance. When the
        declaration names a model, a value of any other model belongs to a sibling selector and is skipped.
        """
        obj = self.instance
        for attr in selector['path'].split('.'):
            obj = getattr(obj, attr, None)
            if obj is None:
                return []
        model = selector.get('model')
        if model is not None and type(obj) is not model:
            return []
        return [obj]

    def _get_current_objects_from_instance(self, field_name):
        """
        Resolve current assigned objects from the instance for forward/reverse M2M, FK/O2O, and same-named
        GenericForeignKey fields. Returns model instances of their true type.
        """
        try:
            model_field = self.instance._meta.get_field(field_name)
        except FieldDoesNotExist:
            model_field = None

        # Forward many-to-many (includes django-taggit tags).
        if model_field is not None and getattr(model_field, 'many_to_many', False):
            return list(getattr(self.instance, field_name).all())

        attr = getattr(self.instance, field_name, None)

        # Reverse many-to-many exposed directly on a form.
        if hasattr(attr, 'all') and hasattr(attr, 'values_list'):
            return list(attr.all())

        # Forward FK/O2O or a same-named GenericForeignKey: a single related object.
        if isinstance(attr, Model):
            return [attr]

        return []

    def _get_restricted_custom_field_current_pks(self, field_name):
        """
        Return current serialized PKs for object and multi-object custom fields.
        """
        customfield = self.custom_fields[field_name]
        value = self.instance.custom_field_data.get(customfield.name)

        if customfield.type == CustomFieldTypeChoices.TYPE_OBJECT:
            if value is None:
                return []
            return [value.pk if isinstance(value, Model) else value]

        if customfield.type == CustomFieldTypeChoices.TYPE_MULTIOBJECT:
            return [
                obj.pk if isinstance(obj, Model) else obj
                for obj in value or []
            ]

        return []

    def _merge_restricted_preserved_members(self):
        for field_name, objects in getattr(self, '_restricted_preserved_members', {}).items():
            if field_name not in self.cleaned_data:
                continue
            existing = list(self.cleaned_data[field_name])
            existing_pks = {obj.pk for obj in existing}
            self.cleaned_data[field_name] = existing + [obj for obj in objects if obj.pk not in existing_pks]
