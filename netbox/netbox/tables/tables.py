import django_tables2 as tables
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.related import RelatedField
from django_tables2.data import TableQuerysetData

from extras.models import CustomField, CustomLink
from netbox.tables import columns

__all__ = (
    'BaseTable',
)


class BaseTable(tables.Table):
    """
    Default table for object lists

    :param user: Personalize table display for the given user (optional). Has no effect if AnonymousUser is passed.
    """
    id = tables.Column(
        linkify=True,
        verbose_name='ID'
    )
    actions = columns.ActionsColumn()

    class Meta:
        attrs = {
            'class': 'table table-hover object-list',
        }

    def __init__(self, *args, user=None, extra_columns=None, **kwargs):
        if extra_columns is None:
            extra_columns = []

        # Add custom field & custom link columns
        content_type = ContentType.objects.get_for_model(self._meta.model)
        custom_fields = CustomField.objects.filter(content_types=content_type)
        extra_columns.extend([
            (f'cf_{cf.name}', columns.CustomFieldColumn(cf)) for cf in custom_fields
        ])
        custom_links = CustomLink.objects.filter(content_type=content_type, enabled=True)
        extra_columns.extend([
            (f'cl_{cl.name}', columns.CustomLinkColumn(cl)) for cl in custom_links
        ])

        super().__init__(*args, extra_columns=extra_columns, **kwargs)

        # Set default empty_text if none was provided
        if self.empty_text is None:
            self.empty_text = f"No {self._meta.model._meta.verbose_name_plural} found"

        # Hide non-default columns (except for actions)
        default_columns = [*getattr(self.Meta, 'default_columns', self.Meta.fields), 'actions']
        for column in self.columns:
            if column.name not in default_columns:
                self.columns.hide(column.name)

        # Apply custom column ordering for user
        if user is not None and not isinstance(user, AnonymousUser):
            selected_columns = user.config.get(f"tables.{self.__class__.__name__}.columns")
            if selected_columns:

                # Show only persistent or selected columns
                for name, column in self.columns.items():
                    if name in ['pk', 'actions', *selected_columns]:
                        self.columns.show(name)
                    else:
                        self.columns.hide(name)

                # Rearrange the sequence to list selected columns first, followed by all remaining columns
                # TODO: There's probably a more clever way to accomplish this
                self.sequence = [
                    *[c for c in selected_columns if c in self.columns.names()],
                    *[c for c in self.columns.names() if c not in selected_columns]
                ]

                # PK column should always come first
                if 'pk' in self.sequence:
                    self.sequence.remove('pk')
                    self.sequence.insert(0, 'pk')

                # Actions column should always come last
                if 'actions' in self.sequence:
                    self.sequence.remove('actions')
                    self.sequence.append('actions')

        # Dynamically update the table's QuerySet to ensure related fields are pre-fetched
        if isinstance(self.data, TableQuerysetData):

            prefetch_fields = []
            for column in self.columns:
                if column.visible:
                    model = getattr(self.Meta, 'model')
                    accessor = column.accessor
                    prefetch_path = []
                    for field_name in accessor.split(accessor.SEPARATOR):
                        try:
                            field = model._meta.get_field(field_name)
                        except FieldDoesNotExist:
                            break
                        if isinstance(field, RelatedField):
                            # Follow ForeignKeys to the related model
                            prefetch_path.append(field_name)
                            model = field.remote_field.model
                        elif isinstance(field, GenericForeignKey):
                            # Can't prefetch beyond a GenericForeignKey
                            prefetch_path.append(field_name)
                            break
                    if prefetch_path:
                        prefetch_fields.append('__'.join(prefetch_path))
            self.data.data = self.data.data.prefetch_related(None).prefetch_related(*prefetch_fields)

    def _get_columns(self, visible=True):
        columns = []
        for name, column in self.columns.items():
            if column.visible == visible and name not in ['pk', 'actions']:
                columns.append((name, column.verbose_name))
        return columns

    @property
    def available_columns(self):
        return self._get_columns(visible=False)

    @property
    def selected_columns(self):
        return self._get_columns(visible=True)

    @property
    def objects_count(self):
        """
        Return the total number of real objects represented by the Table. This is useful when dealing with
        prefixes/IP addresses/etc., where some table rows may represent available address space.
        """
        if not hasattr(self, '_objects_count'):
            self._objects_count = sum(1 for obj in self.data if hasattr(obj, 'pk'))
        return self._objects_count
