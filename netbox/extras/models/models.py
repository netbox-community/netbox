import json
import urllib.parse
from pathlib import Path

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.validators import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from rest_framework.utils.encoders import JSONEncoder

from extras.choices import *
from extras.conditions import ConditionSet, InvalidCondition
from extras.constants import *
from extras.models.mixins import RenderTemplateMixin
from extras.utils import image_upload
from netbox.config import get_config
from netbox.events import get_event_type_choices
from netbox.models import ChangeLoggedModel
from netbox.models.features import (
    CloningMixin, CustomFieldsMixin, CustomLinksMixin, ExportTemplatesMixin, SyncedDataMixin, TagsMixin, has_feature
)
from utilities.html import clean_html
from utilities.jinja2 import render_jinja2
from utilities.querydict import dict_to_querydict
from utilities.querysets import RestrictedQuerySet
from utilities.tables import get_table_for_model

__all__ = (
    'Bookmark',
    'CustomLink',
    'EventRule',
    'ExportTemplate',
    'ImageAttachment',
    'JournalEntry',
    'SavedFilter',
    'TableConfig',
    'Webhook',
)


class EventRule(CustomFieldsMixin, ExportTemplatesMixin, TagsMixin, ChangeLoggedModel):
    """
    An EventRule defines an action to be taken automatically in response to a specific set of events, such as when a
    specific type of object is created, modified, or deleted. The action to be taken might entail transmitting a
    webhook or executing a custom script.
    """
    object_types = models.ManyToManyField(
        to='contenttypes.ContentType',
        related_name='event_rules',
        verbose_name=_('object types'),
        help_text=_("The object(s) to which this rule applies.")
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=150,
        unique=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    event_types = ArrayField(
        base_field=models.CharField(max_length=50, choices=get_event_type_choices),
        help_text=_("The types of event which will trigger this rule.")
    )
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True
    )
    conditions = models.JSONField(
        verbose_name=_('conditions'),
        blank=True,
        null=True,
        help_text=_("A set of conditions which determine whether the event will be generated.")
    )

    # Action to take
    action_type = models.CharField(
        max_length=30,
        choices=EventRuleActionChoices,
        default=EventRuleActionChoices.WEBHOOK,
        verbose_name=_('action type')
    )
    action_object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        related_name='eventrule_actions',
        on_delete=models.CASCADE
    )
    action_object_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    action_object = GenericForeignKey(
        ct_field='action_object_type',
        fk_field='action_object_id'
    )
    action_data = models.JSONField(
        verbose_name=_('data'),
        blank=True,
        null=True,
        help_text=_("Additional data to pass to the action object")
    )
    comments = models.TextField(
        verbose_name=_('comments'),
        blank=True
    )

    class Meta:
        ordering = ('name',)
        indexes = (
            models.Index(fields=('action_object_type', 'action_object_id')),
        )
        verbose_name = _('event rule')
        verbose_name_plural = _('event rules')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:eventrule', args=[self.pk])

    def clean(self):
        super().clean()

        # Validate that any conditions are in the correct format
        if self.conditions:
            try:
                ConditionSet(self.conditions)
            except ValueError as e:
                raise ValidationError({'conditions': e})

    def eval_conditions(self, data):
        """
        Test whether the given data meets the conditions of the event rule (if any). Return True
        if met or no conditions are specified.
        """
        if not self.conditions:
            return True

        logger = logging.getLogger('netbox.event_rules')

        try:
            result = ConditionSet(self.conditions).eval(data)
            logger.debug(f'{self.name}: Evaluated as {result}')
            return result
        except InvalidCondition as e:
            logger.error(f"{self.name}: Evaluation failed. {e}")
            return False


class Webhook(CustomFieldsMixin, ExportTemplatesMixin, TagsMixin, ChangeLoggedModel):
    """
    A Webhook defines a request that will be sent to a remote application when an object is created, updated, and/or
    delete in NetBox. The request will contain a representation of the object, which the remote application can act on.
    Each Webhook can be limited to firing only on certain actions or certain object types.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=150,
        unique=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    payload_url = models.CharField(
        max_length=500,
        verbose_name=_('URL'),
        help_text=_(
            "This URL will be called using the HTTP method defined when the webhook is called. Jinja2 template "
            "processing is supported with the same context as the request body."
        )
    )
    http_method = models.CharField(
        max_length=30,
        choices=WebhookHttpMethodChoices,
        default=WebhookHttpMethodChoices.METHOD_POST,
        verbose_name=_('HTTP method')
    )
    http_content_type = models.CharField(
        max_length=100,
        default=HTTP_CONTENT_TYPE_JSON,
        verbose_name=_('HTTP content type'),
        help_text=_(
            'The complete list of official content types is available '
            '<a href="https://www.iana.org/assignments/media-types/media-types.xhtml">here</a>.'
        )
    )
    additional_headers = models.TextField(
        verbose_name=_('additional headers'),
        blank=True,
        help_text=_(
            "User-supplied HTTP headers to be sent with the request in addition to the HTTP content type. Headers "
            "should be defined in the format <code>Name: Value</code>. Jinja2 template processing is supported with "
            "the same context as the request body (below)."
        )
    )
    body_template = models.TextField(
        verbose_name=_('body template'),
        blank=True,
        help_text=_(
            "Jinja2 template for a custom request body. If blank, a JSON object representing the change will be "
            "included. Available context data includes: <code>event</code>, <code>model</code>, "
            "<code>timestamp</code>, <code>username</code>, <code>request_id</code>, and <code>data</code>."
        )
    )
    secret = models.CharField(
        verbose_name=_('secret'),
        max_length=255,
        blank=True,
        help_text=_(
            "When provided, the request will include a <code>X-Hook-Signature</code> header containing a HMAC hex "
            "digest of the payload body using the secret as the key. The secret is not transmitted in the request."
        )
    )
    ssl_verification = models.BooleanField(
        default=True,
        verbose_name=_('SSL verification'),
        help_text=_("Enable SSL certificate verification. Disable with caution!")
    )
    ca_file_path = models.CharField(
        max_length=4096,
        null=True,
        blank=True,
        verbose_name=_('CA File Path'),
        help_text=_(
            "The specific CA certificate file to use for SSL verification. Leave blank to use the system defaults."
        )
    )
    events = GenericRelation(
        EventRule,
        content_type_field='action_object_type',
        object_id_field='action_object_id'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('webhook')
        verbose_name_plural = _('webhooks')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:webhook', args=[self.pk])

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/extras/webhook/'

    def clean(self):
        super().clean()

        # CA file path requires SSL verification enabled
        if not self.ssl_verification and self.ca_file_path:
            raise ValidationError({
                'ca_file_path': _('Do not specify a CA certificate file if SSL verification is disabled.')
            })

    def render_headers(self, context):
        """
        Render additional_headers and return a dict of Header: Value pairs.
        """
        if not self.additional_headers:
            return {}
        ret = {}
        data = render_jinja2(self.additional_headers, context)
        for line in data.splitlines():
            header, value = line.split(':', 1)
            ret[header.strip()] = value.strip()
        return ret

    def render_body(self, context):
        """
        Render the body template, if defined. Otherwise, jump the context as a JSON object.
        """
        if self.body_template:
            return render_jinja2(self.body_template, context)
        else:
            return json.dumps(context, cls=JSONEncoder)

    def render_payload_url(self, context):
        """
        Render the payload URL.
        """
        return render_jinja2(self.payload_url, context)


class CustomLink(CloningMixin, ExportTemplatesMixin, ChangeLoggedModel):
    """
    A custom link to an external representation of a NetBox object. The link text and URL fields accept Jinja2 template
    code to be rendered with an object as context.
    """
    object_types = models.ManyToManyField(
        to='contenttypes.ContentType',
        related_name='custom_links',
        help_text=_('The object type(s) to which this link applies.')
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True
    )
    link_text = models.TextField(
        verbose_name=_('link text'),
        help_text=_("Jinja2 template code for link text")
    )
    link_url = models.TextField(
        verbose_name=_('link URL'),
        help_text=_("Jinja2 template code for link URL")
    )
    weight = models.PositiveSmallIntegerField(
        verbose_name=_('weight'),
        default=100
    )
    group_name = models.CharField(
        verbose_name=_('group name'),
        max_length=50,
        blank=True,
        help_text=_("Links with the same group will appear as a dropdown menu")
    )
    button_class = models.CharField(
        verbose_name=_('button class'),
        max_length=30,
        choices=CustomLinkButtonClassChoices,
        default=CustomLinkButtonClassChoices.DEFAULT,
        help_text=_("The class of the first link in a group will be used for the dropdown button")
    )
    new_window = models.BooleanField(
        verbose_name=_('new window'),
        default=False,
        help_text=_("Force link to open in a new window")
    )

    clone_fields = (
        'object_types', 'enabled', 'weight', 'group_name', 'button_class', 'new_window',
    )

    class Meta:
        ordering = ['group_name', 'weight', 'name']
        verbose_name = _('custom link')
        verbose_name_plural = _('custom links')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:customlink', args=[self.pk])

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/extras/customlink/'

    def render(self, context):
        """
        Render the CustomLink given the provided context, and return the text, link, and link_target.

        :param context: The context passed to Jinja2
        """
        text = render_jinja2(self.link_text, context).strip()
        if not text:
            return {}
        link = render_jinja2(self.link_url, context).strip()
        link_target = ' target="_blank"' if self.new_window else ''

        # Sanitize link text
        allowed_schemes = get_config().ALLOWED_URL_SCHEMES
        text = clean_html(text, allowed_schemes)

        # Sanitize link
        link = urllib.parse.quote(link, safe='/:?&=%+[]@#,;!')

        # Verify link scheme is allowed
        result = urllib.parse.urlparse(link)
        if result.scheme and result.scheme not in allowed_schemes:
            link = ""

        return {
            'text': text,
            'link': link,
            'link_target': link_target,
        }


class ExportTemplate(SyncedDataMixin, CloningMixin, ExportTemplatesMixin, ChangeLoggedModel, RenderTemplateMixin):
    object_types = models.ManyToManyField(
        to='contenttypes.ContentType',
        related_name='export_templates',
        help_text=_('The object type(s) to which this template applies.')
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )

    clone_fields = (
        'object_types', 'template_code', 'mime_type', 'file_name', 'file_extension', 'as_attachment',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('export template')
        verbose_name_plural = _('export templates')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:exporttemplate', args=[self.pk])

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/extras/exporttemplate/'

    def clean(self):
        super().clean()

        if self.name.lower() == 'table':
            raise ValidationError({
                'name': _('"{name}" is a reserved name. Please choose a different name.').format(name=self.name)
            })

    def sync_data(self):
        """
        Synchronize template content from the designated DataFile (if any).
        """
        self.template_code = self.data_file.data_as_string
    sync_data.alters_data = True

    def get_context(self, context=None, queryset=None):
        _context = {
            'queryset': queryset,
        }

        # Apply the provided context data, if any
        if context is not None:
            _context.update(context)

        return _context


class SavedFilter(CloningMixin, ExportTemplatesMixin, ChangeLoggedModel):
    """
    A set of predefined keyword parameters that can be reused to filter for specific objects.
    """
    object_types = models.ManyToManyField(
        to='contenttypes.ContentType',
        related_name='saved_filters',
        help_text=_('The object type(s) to which this filter applies.')
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=100,
        unique=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    weight = models.PositiveSmallIntegerField(
        verbose_name=_('weight'),
        default=100
    )
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True
    )
    shared = models.BooleanField(
        verbose_name=_('shared'),
        default=True
    )
    parameters = models.JSONField(
        verbose_name=_('parameters')
    )

    clone_fields = (
        'object_types', 'weight', 'enabled', 'parameters',
    )

    class Meta:
        ordering = ('weight', 'name')
        verbose_name = _('saved filter')
        verbose_name_plural = _('saved filters')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:savedfilter', args=[self.pk])

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/extras/savedfilter/'

    def clean(self):
        super().clean()

        # Verify that `parameters` is a JSON object
        if type(self.parameters) is not dict:
            raise ValidationError(
                {'parameters': _('Filter parameters must be stored as a dictionary of keyword arguments.')}
            )

    @property
    def url_params(self):
        qd = dict_to_querydict(self.parameters)
        return qd.urlencode()


class TableConfig(CloningMixin, ChangeLoggedModel):
    """
    A saved configuration of columns and ordering which applies to a specific table.
    """
    object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.CASCADE,
        related_name='table_configs',
        help_text=_("The table's object type"),
    )
    table = models.CharField(
        verbose_name=_('table'),
        max_length=100,
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True,
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    weight = models.PositiveSmallIntegerField(
        verbose_name=_('weight'),
        default=1000,
    )
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True
    )
    shared = models.BooleanField(
        verbose_name=_('shared'),
        default=True
    )
    columns = ArrayField(
        base_field=models.CharField(max_length=100),
    )
    ordering = ArrayField(
        base_field=models.CharField(max_length=100),
        blank=True,
        null=True,
    )

    clone_fields = ('object_type', 'table', 'enabled', 'shared', 'columns', 'ordering')

    class Meta:
        ordering = ('weight', 'name')
        verbose_name = _('table config')
        verbose_name_plural = _('table configs')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:tableconfig', args=[self.pk])

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/extras/tableconfig/'

    @property
    def table_class(self):
        return get_table_for_model(self.object_type.model_class(), name=self.table)

    @property
    def ordering_items(self):
        """
        Return a list of two-tuples indicating the column(s) by which the table is to be ordered and a boolean for each
        column indicating whether its ordering is ascending.
        """
        items = []
        for col in self.ordering or []:
            if col.startswith('-'):
                ascending = False
                col = col[1:]
            else:
                ascending = True
            items.append((col, ascending))
        return items

    def clean(self):
        super().clean()

        # Validate table
        if self.table_class is None:
            raise ValidationError({
                'table': _("Unknown table: {name}").format(name=self.table)
            })

        table = self.table_class([])

        # Validate ordering columns
        for name in self.ordering:
            if name.startswith('-'):
                name = name[1:]  # Strip leading hyphen
            if name not in table.columns:
                raise ValidationError({
                    'ordering': _('Unknown column: {name}').format(name=name)
                })

        # Validate selected columns
        for name in self.columns:
            if name not in table.columns:
                raise ValidationError({
                    'columns': _('Unknown column: {name}').format(name=name)
                })


class ImageAttachment(ChangeLoggedModel):
    """
    An uploaded image which is associated with an object.
    """
    object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.CASCADE
    )
    object_id = models.PositiveBigIntegerField()
    parent = GenericForeignKey(
        ct_field='object_type',
        fk_field='object_id'
    )
    image = models.ImageField(
        upload_to=image_upload,
        height_field='image_height',
        width_field='image_width'
    )
    image_height = models.PositiveSmallIntegerField(
        verbose_name=_('image height'),
    )
    image_width = models.PositiveSmallIntegerField(
        verbose_name=_('image width'),
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=50,
        blank=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    clone_fields = ('object_type', 'object_id')

    class Meta:
        ordering = ('name', 'pk')  # name may be non-unique
        indexes = (
            models.Index(fields=('object_type', 'object_id')),
        )
        verbose_name = _('image attachment')
        verbose_name_plural = _('image attachments')

    def __str__(self):
        return self.name or self.filename

    def get_absolute_url(self):
        return reverse('extras:imageattachment', args=[self.pk])

    def clean(self):
        super().clean()

        # Validate the assigned object type
        if not has_feature(self.object_type, 'image_attachments'):
            raise ValidationError(
                _("Image attachments cannot be assigned to this object type ({type}).").format(type=self.object_type)
            )

    def delete(self, *args, **kwargs):

        _name = self.image.name

        super().delete(*args, **kwargs)

        # Delete file from disk
        self.image.delete(save=False)

        # Deleting the file erases its name. We restore the image's filename here in case we still need to reference it
        # before the request finishes. (For example, to display a message indicating the ImageAttachment was deleted.)
        self.image.name = _name

    @property
    def filename(self):
        base_name = Path(self.image.name).name
        prefix = f"{self.object_type.model}_{self.object_id}_"
        return base_name.removeprefix(prefix)

    @property
    def html_tag(self):
        """
        Returns a complete <img> tag suitable for embedding in an HTML document.
        """
        return mark_safe('<img src="{url}" height="{height}" width="{width}" alt="{alt_text}" />'.format(
            url=self.image.url,
            height=self.image_height,
            width=self.image_width,
            alt_text=escape(self.description or self.name),
        ))

    @property
    def size(self):
        """
        Wrapper around `image.size` to suppress an OSError in case the file is inaccessible. Also opportunistically
        catch other exceptions that we know other storage back-ends to throw.
        """
        expected_exceptions = [OSError]

        try:
            from botocore.exceptions import ClientError
            expected_exceptions.append(ClientError)
        except ImportError:
            pass

        try:
            return self.image.size
        except tuple(expected_exceptions):
            return None

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.parent
        return objectchange


class JournalEntry(CustomFieldsMixin, CustomLinksMixin, TagsMixin, ExportTemplatesMixin, ChangeLoggedModel):
    """
    A historical remark concerning an object; collectively, these form an object's journal. The journal is used to
    preserve historical context around an object, and complements NetBox's built-in change logging. For example, you
    might record a new journal entry when a device undergoes maintenance, or when a prefix is expanded.
    """
    assigned_object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.CASCADE
    )
    assigned_object_id = models.PositiveBigIntegerField()
    assigned_object = GenericForeignKey(
        ct_field='assigned_object_type',
        fk_field='assigned_object_id'
    )
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    kind = models.CharField(
        verbose_name=_('kind'),
        max_length=30,
        choices=JournalEntryKindChoices,
        default=JournalEntryKindChoices.KIND_INFO
    )
    comments = models.TextField(
        verbose_name=_('comments'),
    )

    class Meta:
        ordering = ('-created',)
        indexes = (
            models.Index(fields=('assigned_object_type', 'assigned_object_id')),
        )
        verbose_name = _('journal entry')
        verbose_name_plural = _('journal entries')

    def __str__(self):
        created = timezone.localtime(self.created)
        return (
            f"{created.date().isoformat()} {created.time().isoformat(timespec='minutes')} "
            f"({self.get_kind_display()})"
        )

    def get_absolute_url(self):
        return reverse('extras:journalentry', args=[self.pk])

    def clean(self):
        super().clean()

        # Validate the assigned object type
        if not has_feature(self.assigned_object_type, 'journaling'):
            raise ValidationError(
                _("Journaling is not supported for this object type ({type}).").format(type=self.assigned_object_type)
            )

    def get_kind_color(self):
        return JournalEntryKindChoices.colors.get(self.kind)


class Bookmark(models.Model):
    """
    An object bookmarked by a User.
    """
    created = models.DateTimeField(
        verbose_name=_('created'),
        auto_now_add=True
    )
    object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.PROTECT
    )
    object_id = models.PositiveBigIntegerField()
    object = GenericForeignKey(
        ct_field='object_type',
        fk_field='object_id'
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ('created', 'pk')
        indexes = (
            models.Index(fields=('object_type', 'object_id')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('object_type', 'object_id', 'user'),
                name='%(app_label)s_%(class)s_unique_per_object_and_user'
            ),
        )
        verbose_name = _('bookmark')
        verbose_name_plural = _('bookmarks')

    def __str__(self):
        if self.object:
            return str(self.object)
        return super().__str__()

    def get_absolute_url(self):
        return reverse('account:bookmarks')

    def clean(self):
        super().clean()

        # Validate the assigned object type
        if not has_feature(self.object_type, 'bookmarks'):
            raise ValidationError(
                _("Bookmarks cannot be assigned to this object type ({type}).").format(type=self.object_type)
            )
