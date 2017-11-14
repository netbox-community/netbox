from __future__ import unicode_literals

from collections import OrderedDict
from datetime import date

import graphviz
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.validators import ValidationError
from django.db import models
from django.db.models import Q
from django.http import HttpResponse
from django.template import Template, Context
from django.utils.encoding import python_2_unicode_compatible
from django.utils.safestring import mark_safe

from utilities.utils import foreground_color
from .constants import *


#
# Custom fields
#

class CustomFieldModel(object):

    def cf(self):
        """
        Name-based CustomFieldValue accessor for use in templates
        """
        if not hasattr(self, 'get_custom_fields'):
            return dict()
        return {field.name: value for field, value in self.get_custom_fields().items()}

    def get_custom_fields(self):
        """
        Return a dictionary of custom fields for a single object in the form {<field>: value}.
        """

        # Find all custom fields applicable to this type of object
        content_type = ContentType.objects.get_for_model(self)
        fields = CustomField.objects.filter(obj_type=content_type)

        # If the object exists, populate its custom fields with values
        if hasattr(self, 'pk'):
            values = CustomFieldValue.objects.filter(obj_type=content_type, obj_id=self.pk).select_related('field')
            values_dict = {cfv.field_id: cfv.value for cfv in values}
            return OrderedDict([(field, values_dict.get(field.pk)) for field in fields])
        else:
            return OrderedDict([(field, None) for field in fields])


@python_2_unicode_compatible
class CustomField(models.Model):
    obj_type = models.ManyToManyField(ContentType, related_name='custom_fields', verbose_name='Object(s)',
                                      limit_choices_to={'model__in': CUSTOMFIELD_MODELS},
                                      help_text="The object(s) to which this field applies.")
    type = models.PositiveSmallIntegerField(choices=CUSTOMFIELD_TYPE_CHOICES, default=CF_TYPE_TEXT)
    name = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=50, blank=True, help_text="Name of the field as displayed to users (if not "
                                                                  "provided, the field's name will be used)")
    description = models.CharField(max_length=100, blank=True)
    required = models.BooleanField(default=False, help_text="Determines whether this field is required when creating "
                                                            "new objects or editing an existing object.")
    is_filterable = models.BooleanField(default=True, help_text="This field can be used to filter objects.")
    default = models.CharField(max_length=100, blank=True, help_text="Default value for the field. Use \"true\" or "
                                                                     "\"false\" for booleans. N/A for selection "
                                                                     "fields.")
    weight = models.PositiveSmallIntegerField(default=100, help_text="Fields with higher weights appear lower in a "
                                                                     "form")

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
        if serialized_value is '':
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


@python_2_unicode_compatible
class CustomFieldValue(models.Model):
    field = models.ForeignKey('CustomField', related_name='values', on_delete=models.CASCADE)
    obj_type = models.ForeignKey(ContentType, related_name='+', on_delete=models.PROTECT)
    obj_id = models.PositiveIntegerField()
    obj = GenericForeignKey('obj_type', 'obj_id')
    serialized_value = models.CharField(max_length=255)

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
            super(CustomFieldValue, self).save(*args, **kwargs)


@python_2_unicode_compatible
class CustomFieldChoice(models.Model):
    field = models.ForeignKey('CustomField', related_name='choices', limit_choices_to={'type': CF_TYPE_SELECT},
                              on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    weight = models.PositiveSmallIntegerField(default=100, help_text="Higher weights appear lower in the list")

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
        super(CustomFieldChoice, self).delete(using, keep_parents)
        CustomFieldValue.objects.filter(field__type=CF_TYPE_SELECT, serialized_value=str(pk)).delete()


#
# Graphs
#

@python_2_unicode_compatible
class Graph(models.Model):
    type = models.PositiveSmallIntegerField(choices=GRAPH_TYPE_CHOICES)
    weight = models.PositiveSmallIntegerField(default=1000)
    name = models.CharField(max_length=100, verbose_name='Name')
    source = models.CharField(max_length=500, verbose_name='Source URL')
    link = models.URLField(verbose_name='Link URL', blank=True)

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

@python_2_unicode_compatible
class ExportTemplate(models.Model):
    content_type = models.ForeignKey(
        ContentType, limit_choices_to={'model__in': EXPORTTEMPLATE_MODELS}, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    template_code = models.TextField()
    mime_type = models.CharField(max_length=15, blank=True)
    file_extension = models.CharField(max_length=15, blank=True)

    class Meta:
        ordering = ['content_type', 'name']
        unique_together = [
            ['content_type', 'name']
        ]

    def __str__(self):
        return '{}: {}'.format(self.content_type, self.name)

    def to_response(self, context_dict, filename):
        """
        Render the template to an HTTP response, delivered as a named file attachment
        """
        template = Template(self.template_code)
        mime_type = 'text/plain' if not self.mime_type else self.mime_type
        output = template.render(Context(context_dict))
        # Replace CRLF-style line terminators
        output = output.replace('\r\n', '\n')
        response = HttpResponse(output, content_type=mime_type)
        if self.file_extension:
            filename += '.{}'.format(self.file_extension)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response


#
# Topology maps
#

@python_2_unicode_compatible
class TopologyMap(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    site = models.ForeignKey('dcim.Site', related_name='topology_maps', blank=True, null=True, on_delete=models.CASCADE)
    device_patterns = models.TextField(
        help_text="Identify devices to include in the diagram using regular expressions, one per line. Each line will "
                  "result in a new tier of the drawing. Separate multiple regexes within a line using semicolons. "
                  "Devices will be rendered in the order they are defined."
    )
    description = models.CharField(max_length=100, blank=True)

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

        from circuits.models import CircuitTermination
        from dcim.models import CONNECTION_STATUS_CONNECTED, Device, InterfaceConnection

        # Construct the graph
        graph = graphviz.Graph()
        graph.graph_attr['ranksep'] = '1'
        seen = set()
        for i, device_set in enumerate(self.device_sets):

            subgraph = graphviz.Graph(name='sg{}'.format(i))
            subgraph.graph_attr['rank'] = 'same'

            # Add a pseudonode for each device_set to enforce hierarchical layout
            subgraph.node('set{}'.format(i), label='', shape='none', width='0')
            if i:
                graph.edge('set{}'.format(i - 1), 'set{}'.format(i), style='invis')

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

            graph.subgraph(subgraph)

        # Compile list of all devices
        device_superset = Q()
        for device_set in self.device_sets:
            for query in device_set.split(';'):  # Split regexes on semicolons
                device_superset = device_superset | Q(name__regex=query)

        # Add all interface connections to the graph
        devices = Device.objects.filter(*(device_superset,))
        connections = InterfaceConnection.objects.filter(
            interface_a__device__in=devices, interface_b__device__in=devices
        )
        for c in connections:
            style = 'solid' if c.connection_status == CONNECTION_STATUS_CONNECTED else 'dashed'
            graph.edge(c.interface_a.device.name, c.interface_b.device.name, style=style)

        # Add all circuits to the graph
        for termination in CircuitTermination.objects.filter(term_side='A', interface__device__in=devices):
            peer_termination = termination.get_peer_termination()
            if (peer_termination is not None and peer_termination.interface is not None and
                    peer_termination.interface.device in devices):
                graph.edge(termination.interface.device.name, peer_termination.interface.device.name, color='blue')

        return graph.pipe(format=img_format)


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


@python_2_unicode_compatible
class ImageAttachment(models.Model):
    """
    An uploaded image which is associated with an object.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    parent = GenericForeignKey('content_type', 'object_id')
    image = models.ImageField(upload_to=image_upload, height_field='image_height', width_field='image_width')
    image_height = models.PositiveSmallIntegerField()
    image_width = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=50, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        if self.name:
            return self.name
        filename = self.image.name.rsplit('/', 1)[-1]
        return filename.split('_', 2)[2]

    def delete(self, *args, **kwargs):

        _name = self.image.name

        super(ImageAttachment, self).delete(*args, **kwargs)

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
# Report results
#

class ReportResult(models.Model):
    """
    This model stores the results from running a user-defined report.
    """
    report = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='+', blank=True, null=True)
    failed = models.BooleanField()
    data = JSONField()

    class Meta:
        ordering = ['report']


#
# User actions
#

class UserActionManager(models.Manager):

    # Actions affecting a single object
    def log_action(self, user, obj, action, message):
        self.model.objects.create(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.pk,
            user=user,
            action=action,
            message=message,
        )

    def log_create(self, user, obj, message=''):
        self.log_action(user, obj, ACTION_CREATE, message)

    def log_edit(self, user, obj, message=''):
        self.log_action(user, obj, ACTION_EDIT, message)

    def log_delete(self, user, obj, message=''):
        self.log_action(user, obj, ACTION_DELETE, message)

    # Actions affecting multiple objects
    def log_bulk_action(self, user, content_type, action, message):
        self.model.objects.create(
            content_type=content_type,
            user=user,
            action=action,
            message=message,
        )

    def log_import(self, user, content_type, message=''):
        self.log_bulk_action(user, content_type, ACTION_IMPORT, message)

    def log_bulk_create(self, user, content_type, message=''):
        self.log_bulk_action(user, content_type, ACTION_BULK_CREATE, message)

    def log_bulk_edit(self, user, content_type, message=''):
        self.log_bulk_action(user, content_type, ACTION_BULK_EDIT, message)

    def log_bulk_delete(self, user, content_type, message=''):
        self.log_bulk_action(user, content_type, ACTION_BULK_DELETE, message)


@python_2_unicode_compatible
class UserAction(models.Model):
    """
    A record of an action (add, edit, or delete) performed on an object by a User.
    """
    time = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, related_name='actions', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    action = models.PositiveSmallIntegerField(choices=ACTION_CHOICES)
    message = models.TextField(blank=True)

    objects = UserActionManager()

    class Meta:
        ordering = ['-time']

    def __str__(self):
        if self.message:
            return '{} {}'.format(self.user, self.message)
        return '{} {} {}'.format(self.user, self.get_action_display(), self.content_type)

    def icon(self):
        if self.action in [ACTION_CREATE, ACTION_BULK_CREATE, ACTION_IMPORT]:
            return mark_safe('<i class="glyphicon glyphicon-plus text-success"></i>')
        elif self.action in [ACTION_EDIT, ACTION_BULK_EDIT]:
            return mark_safe('<i class="glyphicon glyphicon-pencil text-warning"></i>')
        elif self.action in [ACTION_DELETE, ACTION_BULK_DELETE]:
            return mark_safe('<i class="glyphicon glyphicon-remove text-danger"></i>')
        else:
            return ''
