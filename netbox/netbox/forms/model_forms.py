import json

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Model
from django.db.models.fields.related import ManyToManyRel
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from extras.choices import *
from utilities.forms.fields import CommentField, SlugField
from utilities.forms.mixins import CheckLastUpdatedMixin

from .mixins import ChangelogMessageMixin, CustomFieldsMixin, OwnerMixin, TagsMixin

__all__ = (
    'NestedGroupModelForm',
    'NetBoxModelForm',
    'OrganizationalModelForm',
    'PrimaryModelForm',
)


class RestrictedChoiceLabel:
    """
    Wraps a choice label so widgets/select_option.html renders that single <option> as disabled. Used to identify a
    restricted current value as read-only in widgets which honor disabled options. Preservation itself is enforced
    server-side, not by the widget.
    """
    disabled = True

    def __init__(self, label):
        self.label = label

    def __str__(self):
        return str(self.label)


class NetBoxModelForm(
    ChangelogMessageMixin,
    CheckLastUpdatedMixin,
    CustomFieldsMixin,
    TagsMixin,
    forms.ModelForm
):
    """
    Base form for creating & editing NetBox models. Extends Django's ModelForm to add support for custom fields.

    Attributes:
        fieldsets: An iterable of FieldSets which define a name and set of fields to display per section of
            the rendered form (optional). If not defined, the all fields will be rendered as a single section.
    """
    fieldsets = ()

    restricted_value_help_text = _(
        'This field includes one or more restricted values that cannot be changed. '
        'They will be preserved when this form is saved.'
    )

    # Maps selector form fields whose current value is stored under a different instance attribute (e.g. a
    # GenericForeignKey). Keys are form field names; entries may declare:
    #   path: dotted attribute path on the instance holding the current value (read from the instance only)
    #   model: expected model class; set when several selector fields share one path (picks the matching field)
    #   lock_fields: controller field names locked alongside the selector when its current value is hidden
    # Subclasses override (not merge) this attribute.
    restricted_related_selectors = {}

    def _get_content_type(self):
        return ContentType.objects.get_for_model(self._meta.model)

    def _get_form_field(self, customfield):
        if self.instance.pk:
            form_field = customfield.to_form_field(set_initial=False)
            initial = self.instance.custom_field_data.get(customfield.name)
            if customfield.type == CustomFieldTypeChoices.TYPE_JSON:
                form_field.initial = json.dumps(initial)
            else:
                form_field.initial = initial
            return form_field

        return customfield.to_form_field()

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

            hidden_objects = [
                obj for obj in current_objects
                if self._restricted_value_is_hidden(field, restricted_queryset, original_queryset, obj, user, action)
            ]
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

    def _restricted_value_is_hidden(self, field, restricted_queryset, original_queryset, obj, user, action):
        """
        Return True if `obj` is an assigned value the user cannot view (and was a valid choice before restriction).

        Objects whose model matches the field are checked against the field's own restricted/original querysets.
        Objects of a different model (a GenericForeignKey whose paired type field was changed) are checked against
        their own model, so a same-PK object of another model is never mistaken for the current value.
        """
        field_model = getattr(restricted_queryset, 'model', None)
        if field_model is not None and type(obj) is field_model:
            was_choice = original_queryset.filter(pk=obj.pk).exists()
            is_visible = restricted_queryset.filter(pk=obj.pk).exists()
            return was_choice and not is_visible

        manager = type(obj).objects
        if user is not None and hasattr(manager, 'restrict'):
            return not manager.restrict(user, action).filter(pk=obj.pk).exists()
        # Without a user we cannot re-check visibility for a different model, so preserve to avoid data loss.
        return True

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

    def clean(self):
        # Merge restricted current members the user could not see back into multi-value fields so they survive on
        # save (their options are disabled in the widget and so are not submitted).
        self._merge_restricted_preserved_members()

        # Save custom field data on instance
        for cf_name, customfield in self.custom_fields.items():
            if cf_name not in self.fields:
                # Custom fields may be absent when performing bulk updates via import
                continue
            key = cf_name[3:]  # Strip "cf_" from field name
            value = self.cleaned_data.get(cf_name)

            # Convert "empty" values to null
            if value in self.fields[cf_name].empty_values:
                self.instance.custom_field_data[key] = None
            else:
                if customfield.type == CustomFieldTypeChoices.TYPE_JSON and type(value) is str:
                    value = json.loads(value)
                self.instance.custom_field_data[key] = customfield.serialize(value)

        return super().clean()

    def _post_clean(self):
        """
        Override BaseModelForm's _post_clean() to store many-to-many field values on the model instance.
        Handles both forward and reverse M2M relationships, and supports both simple (single field)
        and add/remove (dual field) modes.
        """
        self.instance._m2m_values = {}

        # Collect names to process: local M2M fields (includes TaggableManager from django-taggit)
        # plus reverse M2M relations (ManyToManyRel).
        names = [field.name for field in self.instance._meta.local_many_to_many]
        names += [
            field.get_accessor_name()
            for field in self.instance._meta.get_fields()
            if isinstance(field, ManyToManyRel)
        ]

        for name in names:
            if name in self.cleaned_data:
                # Simple mode: single multi-select field
                self.instance._m2m_values[name] = list(self.cleaned_data[name])
            elif f'add_{name}' in self.cleaned_data or f'remove_{name}' in self.cleaned_data:
                # Add/remove mode: compute the effective set
                current = set(getattr(self.instance, name).values_list('pk', flat=True)) \
                    if self.instance.pk else set()
                add_values = set(
                    v.pk for v in self.cleaned_data.get(f'add_{name}', [])
                )
                remove_values = set(
                    v.pk for v in self.cleaned_data.get(f'remove_{name}', [])
                )
                self.instance._m2m_values[name] = list((current | add_values) - remove_values)

        return super()._post_clean()

    def _save_m2m(self):
        """
        Save many-to-many field values that were computed in _post_clean(). This handles M2M fields
        not included in Meta.fields (e.g. those managed via M2MAddRemoveFields).
        """
        super()._save_m2m()
        meta_fields = self._meta.fields
        for field_name, values in self.instance._m2m_values.items():
            if not meta_fields or field_name not in meta_fields:
                getattr(self.instance, field_name).set(values)


class PrimaryModelForm(OwnerMixin, NetBoxModelForm):
    """
    Form for models which inherit from PrimaryModel.
    """
    comments = CommentField()


class OrganizationalModelForm(OwnerMixin, NetBoxModelForm):
    """
    Form for models which inherit from OrganizationalModel.
    """
    slug = SlugField()
    comments = CommentField()


class NestedGroupModelForm(OwnerMixin, NetBoxModelForm):
    """
    Form for models which inherit from NestedGroupModel.
    """
    slug = SlugField()
    comments = CommentField()
