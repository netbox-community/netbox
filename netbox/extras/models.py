from collections import OrderedDict
from datetime import date

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.validators import ValidationError
from django.db import models
from django.db.models import F, Q
from django.http import HttpResponse
from django.template import Template, Context
from django.urls import reverse
import graphviz
from jinja2 import Environment
from taggit.models import TagBase, GenericTaggedItemBase

from dcim.constants import CONNECTION_STATUS_CONNECTED
from utilities.fields import ColorField
from utilities.utils import deepmerge, foreground_color, model_names_to_filter_dict
from .constants import *
from .querysets import ConfigContextQuerySet


#
# Webhooks
#

def get_webhook_models():
    return model_names_to_filter_dict(WEBHOOK_MODELS)


class Webhook(models.Model):
    """
    A Webhook defines a request that will be sent to a remote application when an object is created, updated, and/or
    delete in NetBox. The request will contain a representation of the object, which the remote application can act on.
    Each Webhook can be limited to firing only on certain actions or certain object types.
    """

    obj_type = models.ManyToManyField(
        to=ContentType,
        related_name='webhooks',
        verbose_name='Object types',
        limit_choices_to=get_webhook_models,
        help_text="The object(s) to which this Webhook applies."
    )
    name = models.CharField(
        max_length=150,
        unique=True
    )
    type_create = models.BooleanField(
        default=False,
        help_text="Call this webhook when a matching object is created."
    )
    type_update = models.BooleanField(
        default=False,
        help_text="Call this webhook when a matching object is updated."
    )
    type_delete = models.BooleanField(
        default=False,
        help_text="Call this webhook when a matching object is deleted."
    )
    payload_url = models.CharField(
        max_length=500,
        verbose_name='URL',
        help_text="A POST will be sent to this URL when the webhook is called."
    )
    http_content_type = models.PositiveSmallIntegerField(
        choices=WEBHOOK_CT_CHOICES,
        default=WEBHOOK_CT_JSON,
        verbose_name='HTTP content type'
    )
    secret = models.CharField(
        max_length=255,
        blank=True,
        help_text="When provided, the request will include a 'X-Hook-Signature' "
                  "header containing a HMAC hex digest of the payload body using "
                  "the secret as the key. The secret is not transmitted in "
                  "the request."
    )
    enabled = models.BooleanField(
        default=True
    )
    ssl_verification = models.BooleanField(
        default=True,
        verbose_name='SSL verification',
        help_text="Enable SSL certificate verification. Disable with caution!"
    )

    class Meta:
        unique_together = ('payload_url', 'type_create', 'type_update', 'type_delete',)

    def __str__(self):
        return self.name

    def clean(self):
        """
        Validate model
        """
        if not self.type_create and not self.type_delete and not self.type_update:
            raise ValidationError(
                "You must select at least one type: create, update, and/or delete."
            )


#
# Custom fields
#

class CustomFieldModel(models.Model):
    _cf = None

    class Meta:
        abstract = True

    @property
    def cf(self):
        """
        Name-based CustomFieldValue accessor for use in templates
        """
        if self._cf is None:
            # Cache all custom field values for this instance
            self._cf = {
                field.name: value for field, value in self.get_custom_fields().items()
            }
        return self._cf

    def get_custom_fields(self):
        """
        Return a dictionary of custom fields for a single object in the form {<field>: value}.
        """

        # Find all custom fields applicable to this type of object
        content_type = ContentType.objects.get_for_model(self)
        fields = CustomField.objects.filter(obj_type=content_type)

        # If the object exists, populate its custom fields with values
        if hasattr(self, 'pk'):
            values = self.custom_field_values.all()
            values_dict = {cfv.field_id: cfv.value for cfv in values}
            return OrderedDict([(field, values_dict.get(field.pk)) for field in fields])
        else:
            return OrderedDict([(field, None) for field in fields])


def get_custom_field_models():
    return model_names_to_filter_dict(CUSTOMFIELD_MODELS)


class CustomField(models.Model):
    obj_type = models.ManyToManyField(
        to=ContentType,
        related_name='custom_fields',
        verbose_name='Object(s)',
        limit_choices_to=get_custom_field_models,
        help_text='The object(s) to which this field applies.'
    )
    type = models.PositiveSmallIntegerField(
        choices=CUSTOMFIELD_TYPE_CHOICES,
        default=CF_TYPE_TEXT
    )
    name = models.CharField(
        max_length=50,
        unique=True
    )
    label = models.CharField(
        max_length=50,
        blank=True,
        help_text='Name of the field as displayed to users (if not provided, '
                  'the field\'s name will be used)'
    )
    description = models.CharField(
        max_length=100,
        blank=True
    )
    required = models.BooleanField(
        default=False,
        help_text='If true, this field is required when creating new objects '
                  'or editing an existing object.'
    )
    filter_logic = models.PositiveSmallIntegerField(
        choices=CF_FILTER_CHOICES,
        default=CF_FILTER_LOOSE,
        help_text='Loose matches any instance of a given string; exact '
                  'matches the entire field.'
    )
    default = models.CharField(
        max_length=100,
        blank=True,
        help_text='Default value for the field. Use "true" or "false" for booleans.'
    )
    weight = models.PositiveSmallIntegerField(
        default=100,
        help_text='Fields with higher weights appear lower in a form.'
    )

    class Meta:
        ordering = ['weight', 'name']

    def __str__(self):
        return self.label or self.name.replace('_', ' ').capitalize()

    def serialize_value(self, value):
        """
        Serialize the given value to a string suitable for storage as a CustomFieldValue
        """
        if value is None:
            return ''
        if self.type == CF_TYPE_BOOLEAN:
            return str(int(bool(value)))
        if self.type == CF_TYPE_DATE:
            # Could be date/datetime object or string
            try:
                return value.strftime('%Y-%m-%d')
            except AttributeError:
                return value
        if self.type == CF_TYPE_SELECT:
            # Could be ModelChoiceField or TypedChoiceField
            return str(value.id) if hasattr(value, 'id') else str(value)
        return value

    def deserialize_value(self, serialized_value):
        """
        Convert a string into the object it represents depending on the type of field
        """
        if serialized_value == '':
            return None
        if self.type == CF_TYPE_INTEGER:
            return int(serialized_value)
        if self.type == CF_TYPE_BOOLEAN:
            return bool(int(serialized_value))
        if self.type == CF_TYPE_DATE:
            # Read date as YYYY-MM-DD
            return date(*[int(n) for n in serialized_value.split('-')])
        if self.type == CF_TYPE_SELECT:
            return self.choices.get(pk=int(serialized_value))
        return serialized_value


class CustomFieldValue(models.Model):
    field = models.ForeignKey(
        to='extras.CustomField',
        on_delete=models.CASCADE,
        related_name='values'
    )
    obj_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.PROTECT,
        related_name='+'
    )
    obj_id = models.PositiveIntegerField()
    obj = GenericForeignKey(
        ct_field='obj_type',
        fk_field='obj_id'
    )
    serialized_value = models.CharField(
        max_length=255
    )

    class Meta:
        ordering = ['obj_type', 'obj_id']
        unique_together = ['field', 'obj_type', 'obj_id']

    def __str__(self):
        return '{} {}'.format(self.obj, self.field)

    @property
    def value(self):
        return self.field.deserialize_value(self.serialized_value)

    @value.setter
    def value(self, value):
        self.serialized_value = self.field.serialize_value(value)

    def save(self, *args, **kwargs):
        # Delete this object if it no longer has a value to store
        if self.pk and self.value is None:
            self.delete()
        else:
            super().save(*args, **kwargs)


class CustomFieldChoice(models.Model):
    field = models.ForeignKey(
        to='extras.CustomField',
        on_delete=models.CASCADE,
        related_name='choices',
        limit_choices_to={'type': CF_TYPE_SELECT}
    )
    value = models.CharField(
        max_length=100
    )
    weight = models.PositiveSmallIntegerField(
        default=100,
        help_text='Higher weights appear lower in the list'
    )

    class Meta:
        ordering = ['field', 'weight', 'value']
        unique_together = ['field', 'value']

    def __str__(self):
        return self.value

    def clean(self):
        if self.field.type != CF_TYPE_SELECT:
            raise ValidationError("Custom field choices can only be assigned to selection fields.")

    def delete(self, using=None, keep_parents=False):
        # When deleting a CustomFieldChoice, delete all CustomFieldValues which point to it
        pk = self.pk
        super().delete(using, keep_parents)
        CustomFieldValue.objects.filter(field__type=CF_TYPE_SELECT, serialized_value=str(pk)).delete()


#
# Custom links
#

def get_custom_link_models():
    return model_names_to_filter_dict(CUSTOMLINK_MODELS)


class CustomLink(models.Model):
    """
    A custom link to an external representation of a NetBox object. The link text and URL fields accept Jinja2 template
    code to be rendered with an object as context.
    """
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=get_custom_link_models
    )
    name = models.CharField(
        max_length=100,
        unique=True
    )
    text = models.CharField(
        max_length=500,
        help_text="Jinja2 template code for link text"
    )
    url = models.CharField(
        max_length=500,
        verbose_name='URL',
        help_text="Jinja2 template code for link URL"
    )
    weight = models.PositiveSmallIntegerField(
        default=100
    )
    group_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Links with the same group will appear as a dropdown menu"
    )
    button_class = models.CharField(
        max_length=30,
        choices=BUTTON_CLASS_CHOICES,
        default=BUTTON_CLASS_DEFAULT,
        help_text="The class of the first link in a group will be used for the dropdown button"
    )
    new_window = models.BooleanField(
        help_text="Force link to open in a new window"
    )

    class Meta:
        ordering = ['group_name', 'weight', 'name']

    def __str__(self):
        return self.name


#
# Graphs
#

class Graph(models.Model):
    type = models.PositiveSmallIntegerField(
        choices=GRAPH_TYPE_CHOICES
    )
    weight = models.PositiveSmallIntegerField(
        default=1000
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Name'
    )
    source = models.CharField(
        max_length=500,
        verbose_name='Source URL'
    )
    link = models.URLField(
        blank=True,
        verbose_name='Link URL'
    )

    class Meta:
        ordering = ['type', 'weight', 'name']

    def __str__(self):
        return self.name

    def embed_url(self, obj):
        template = Template(self.source)
        return template.render(Context({'obj': obj}))

    def embed_link(self, obj):
        if self.link is None:
            return ''
        template = Template(self.link)
        return template.render(Context({'obj': obj}))


#
# Export templates
#

def get_export_template_models():
    return model_names_to_filter_dict(EXPORTTEMPLATE_MODELS)


class ExportTemplate(models.Model):
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=get_export_template_models
    )
    name = models.CharField(
        max_length=100
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    template_language = models.PositiveSmallIntegerField(
        choices=TEMPLATE_LANGUAGE_CHOICES,
        default=TEMPLATE_LANGUAGE_JINJA2
    )
    template_code = models.TextField()
    mime_type = models.CharField(
        max_length=50,
        blank=True
    )
    file_extension = models.CharField(
        max_length=15,
        blank=True
    )

    class Meta:
        ordering = ['content_type', 'name']
        unique_together = [
            ['content_type', 'name']
        ]

    def __str__(self):
        return '{}: {}'.format(self.content_type, self.name)

    def render(self, queryset):
        """
        Render the contents of the template.
        """
        context = {
            'queryset': queryset
        }

        if self.template_language == TEMPLATE_LANGUAGE_DJANGO:
            template = Template(self.template_code)
            output = template.render(Context(context))

        elif self.template_language == TEMPLATE_LANGUAGE_JINJA2:
            template = Environment().from_string(source=self.template_code)
            output = template.render(**context)

        else:
            return None

        # Replace CRLF-style line terminators
        output = output.replace('\r\n', '\n')

        return output

    def render_to_response(self, queryset):
        """
        Render the template to an HTTP response, delivered as a named file attachment
        """
        output = self.render(queryset)
        mime_type = 'text/plain' if not self.mime_type else self.mime_type

        # Build the response
        response = HttpResponse(output, content_type=mime_type)
        filename = 'netbox_{}{}'.format(
            queryset.model._meta.verbose_name_plural,
            '.{}'.format(self.file_extension) if self.file_extension else ''
        )
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

        return response


#
# Topology maps
#

class TopologyMap(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )
    type = models.PositiveSmallIntegerField(
        choices=TOPOLOGYMAP_TYPE_CHOICES,
        default=TOPOLOGYMAP_TYPE_NETWORK
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.CASCADE,
        related_name='topology_maps',
        blank=True,
        null=True
    )
    device_patterns = models.TextField(
        help_text='Identify devices to include in the diagram using regular '
                  'expressions, one per line. Each line will result in a new '
                  'tier of the drawing. Separate multiple regexes within a '
                  'line using semicolons. Devices will be rendered in the '
                  'order they are defined.'
    )
    description = models.CharField(
        max_length=100,
        blank=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def device_sets(self):
        if not self.device_patterns:
            return None
        return [line.strip() for line in self.device_patterns.split('\n')]

    def render(self, img_format='png'):

        from dcim.models import Device

        # Construct the graph
        if self.type == TOPOLOGYMAP_TYPE_NETWORK:
            G = graphviz.Graph
        else:
            G = graphviz.Digraph
        self.graph = G()
        self.graph.graph_attr['ranksep'] = '1'
        seen = set()
        for i, device_set in enumerate(self.device_sets):

            subgraph = G(name='sg{}'.format(i))
            subgraph.graph_attr['rank'] = 'same'
            subgraph.graph_attr['directed'] = 'true'

            # Add a pseudonode for each device_set to enforce hierarchical layout
            subgraph.node('set{}'.format(i), label='', shape='none', width='0')
            if i:
                self.graph.edge('set{}'.format(i - 1), 'set{}'.format(i), style='invis')

            # Add each device to the graph
            devices = []
            for query in device_set.strip(';').split(';'):  # Split regexes on semicolons
                devices += Device.objects.filter(name__regex=query).select_related('device_role')
            # Remove duplicate devices
            devices = [d for d in devices if d.id not in seen]
            seen.update([d.id for d in devices])
            for d in devices:
                bg_color = '#{}'.format(d.device_role.color)
                fg_color = '#{}'.format(foreground_color(d.device_role.color))
                subgraph.node(d.name, style='filled', fillcolor=bg_color, fontcolor=fg_color, fontname='sans')

            # Add an invisible connection to each successive device in a set to enforce horizontal order
            for j in range(0, len(devices) - 1):
                subgraph.edge(devices[j].name, devices[j + 1].name, style='invis')

            self.graph.subgraph(subgraph)

        # Compile list of all devices
        device_superset = Q()
        for device_set in self.device_sets:
            for query in device_set.split(';'):  # Split regexes on semicolons
                device_superset = device_superset | Q(name__regex=query)
        devices = Device.objects.filter(*(device_superset,))

        # Draw edges depending on graph type
        if self.type == TOPOLOGYMAP_TYPE_NETWORK:
            self.add_network_connections(devices)
        elif self.type == TOPOLOGYMAP_TYPE_CONSOLE:
            self.add_console_connections(devices)
        elif self.type == TOPOLOGYMAP_TYPE_POWER:
            self.add_power_connections(devices)

        return self.graph.pipe(format=img_format)

    def add_network_connections(self, devices):

        from circuits.models import CircuitTermination
        from dcim.models import Interface

        # Add all interface connections to the graph
        connected_interfaces = Interface.objects.select_related(
            '_connected_interface__device'
        ).filter(
            Q(device__in=devices) | Q(_connected_interface__device__in=devices),
            _connected_interface__isnull=False,
            pk__lt=F('_connected_interface')
        )
        for interface in connected_interfaces:
            style = 'solid' if interface.connection_status == CONNECTION_STATUS_CONNECTED else 'dashed'
            self.graph.edge(interface.device.name, interface.connected_endpoint.device.name, style=style)

        # Add all circuits to the graph
        for termination in CircuitTermination.objects.filter(term_side='A', connected_endpoint__device__in=devices):
            peer_termination = termination.get_peer_termination()
            if (peer_termination is not None and peer_termination.interface is not None and
                    peer_termination.interface.device in devices):
                self.graph.edge(termination.interface.device.name, peer_termination.interface.device.name, color='blue')

    def add_console_connections(self, devices):

        from dcim.models import ConsolePort

        # Add all console connections to the graph
        for cp in ConsolePort.objects.filter(device__in=devices, connected_endpoint__device__in=devices):
            style = 'solid' if cp.connection_status == CONNECTION_STATUS_CONNECTED else 'dashed'
            self.graph.edge(cp.connected_endpoint.device.name, cp.device.name, style=style)

    def add_power_connections(self, devices):

        from dcim.models import PowerPort

        # Add all power connections to the graph
        for pp in PowerPort.objects.filter(device__in=devices, _connected_poweroutlet__device__in=devices):
            style = 'solid' if pp.connection_status == CONNECTION_STATUS_CONNECTED else 'dashed'
            self.graph.edge(pp.connected_endpoint.device.name, pp.device.name, style=style)


#
# Image attachments
#

def image_upload(instance, filename):

    path = 'image-attachments/'

    # Rename the file to the provided name, if any. Attempt to preserve the file extension.
    extension = filename.rsplit('.')[-1].lower()
    if instance.name and extension in ['bmp', 'gif', 'jpeg', 'jpg', 'png']:
        filename = '.'.join([instance.name, extension])
    elif instance.name:
        filename = instance.name

    return '{}{}_{}_{}'.format(path, instance.content_type.name, instance.object_id, filename)


class ImageAttachment(models.Model):
    """
    An uploaded image which is associated with an object.
    """
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    parent = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id'
    )
    image = models.ImageField(
        upload_to=image_upload,
        height_field='image_height',
        width_field='image_width'
    )
    image_height = models.PositiveSmallIntegerField()
    image_width = models.PositiveSmallIntegerField()
    name = models.CharField(
        max_length=50,
        blank=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        if self.name:
            return self.name
        filename = self.image.name.rsplit('/', 1)[-1]
        return filename.split('_', 2)[2]

    def delete(self, *args, **kwargs):

        _name = self.image.name

        super().delete(*args, **kwargs)

        # Delete file from disk
        self.image.delete(save=False)

        # Deleting the file erases its name. We restore the image's filename here in case we still need to reference it
        # before the request finishes. (For example, to display a message indicating the ImageAttachment was deleted.)
        self.image.name = _name

    @property
    def size(self):
        """
        Wrapper around `image.size` to suppress an OSError in case the file is inaccessible.
        """
        try:
            return self.image.size
        except OSError:
            return None


#
# Config contexts
#

class ConfigContext(models.Model):
    """
    A ConfigContext represents a set of arbitrary data available to any Device or VirtualMachine matching its assigned
    qualifiers (region, site, etc.). For example, the data stored in a ConfigContext assigned to site A and tenant B
    will be available to a Device in site A assigned to tenant B. Data is stored in JSON format.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    weight = models.PositiveSmallIntegerField(
        default=1000
    )
    description = models.CharField(
        max_length=100,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
    )
    regions = models.ManyToManyField(
        to='dcim.Region',
        related_name='+',
        blank=True
    )
    sites = models.ManyToManyField(
        to='dcim.Site',
        related_name='+',
        blank=True
    )
    roles = models.ManyToManyField(
        to='dcim.DeviceRole',
        related_name='+',
        blank=True
    )
    platforms = models.ManyToManyField(
        to='dcim.Platform',
        related_name='+',
        blank=True
    )
    tenant_groups = models.ManyToManyField(
        to='tenancy.TenantGroup',
        related_name='+',
        blank=True
    )
    tenants = models.ManyToManyField(
        to='tenancy.Tenant',
        related_name='+',
        blank=True
    )
    data = JSONField()

    objects = ConfigContextQuerySet.as_manager()

    class Meta:
        ordering = ['weight', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:configcontext', kwargs={'pk': self.pk})

    def clean(self):

        # Verify that JSON data is provided as an object
        if type(self.data) is not dict:
            raise ValidationError(
                {'data': 'JSON data must be in object form. Example: {"foo": 123}'}
            )


class ConfigContextModel(models.Model):

    local_context_data = JSONField(
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

    def get_config_context(self):
        """
        Return the rendered configuration context for a device or VM.
        """

        # Compile all config data, overwriting lower-weight values with higher-weight values where a collision occurs
        data = OrderedDict()
        for context in ConfigContext.objects.get_for_object(self):
            data = deepmerge(data, context.data)

        # If the object has local config context data defined, merge it last
        if self.local_context_data:
            data = deepmerge(data, self.local_context_data)

        return data


#
# Report results
#

class ReportResult(models.Model):
    """
    This model stores the results from running a user-defined report.
    """
    report = models.CharField(
        max_length=255,
        unique=True
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    failed = models.BooleanField()
    data = JSONField()

    class Meta:
        ordering = ['report']


#
# Change logging
#

class ObjectChange(models.Model):
    """
    Record a change to an object and the user account associated with that change. A change record may optionally
    indicate an object related to the one being changed. For example, a change to an interface may also indicate the
    parent device. This will ensure changes made to component models appear in the parent model's changelog.
    """
    time = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        related_name='changes',
        blank=True,
        null=True
    )
    user_name = models.CharField(
        max_length=150,
        editable=False
    )
    request_id = models.UUIDField(
        editable=False
    )
    action = models.PositiveSmallIntegerField(
        choices=OBJECTCHANGE_ACTION_CHOICES
    )
    changed_object_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.PROTECT,
        related_name='+'
    )
    changed_object_id = models.PositiveIntegerField()
    changed_object = GenericForeignKey(
        ct_field='changed_object_type',
        fk_field='changed_object_id'
    )
    related_object_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    related_object_id = models.PositiveIntegerField(
        blank=True,
        null=True
    )
    related_object = GenericForeignKey(
        ct_field='related_object_type',
        fk_field='related_object_id'
    )
    object_repr = models.CharField(
        max_length=200,
        editable=False
    )
    object_data = JSONField(
        editable=False
    )

    csv_headers = [
        'time', 'user', 'user_name', 'request_id', 'action', 'changed_object_type', 'changed_object_id',
        'related_object_type', 'related_object_id', 'object_repr', 'object_data',
    ]

    class Meta:
        ordering = ['-time']

    def __str__(self):
        return '{} {} {} by {}'.format(
            self.changed_object_type,
            self.object_repr,
            self.get_action_display().lower(),
            self.user_name
        )

    def save(self, *args, **kwargs):

        # Record the user's name and the object's representation as static strings
        self.user_name = self.user.username
        self.object_repr = str(self.changed_object)

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('extras:objectchange', args=[self.pk])

    def to_csv(self):
        return (
            self.time,
            self.user,
            self.user_name,
            self.request_id,
            self.get_action_display(),
            self.changed_object_type,
            self.changed_object_id,
            self.related_object_type,
            self.related_object_id,
            self.object_repr,
            self.object_data,
        )


#
# Tags
#

# TODO: figure out a way around this circular import for ObjectChange
from utilities.models import ChangeLoggedModel  # noqa: E402


class Tag(TagBase, ChangeLoggedModel):
    color = ColorField(
        default='9e9e9e'
    )
    comments = models.TextField(
        blank=True,
        default=''
    )

    def get_absolute_url(self):
        return reverse('extras:tag', args=[self.slug])


class TaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(
        to=Tag,
        related_name="%(app_label)s_%(class)s_items",
        on_delete=models.CASCADE
    )

    class Meta:
        index_together = (
            ("content_type", "object_id")
        )
