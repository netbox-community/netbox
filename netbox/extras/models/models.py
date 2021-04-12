import json
import uuid
from collections import OrderedDict

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import ValidationError
from django.db import models
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from rest_framework.utils.encoders import JSONEncoder

from extras.choices import *
from extras.constants import *
from extras.models import ChangeLoggedModel
from extras.querysets import ConfigContextQuerySet
from extras.utils import extras_features, FeatureQuery, image_upload
from utilities.querysets import RestrictedQuerySet
from utilities.utils import deepmerge, render_jinja2


#
# Webhooks
#

class Webhook(models.Model):
    """
    A Webhook defines a request that will be sent to a remote application when an object is created, updated, and/or
    delete in NetBox. The request will contain a representation of the object, which the remote application can act on.
    Each Webhook can be limited to firing only on certain actions or certain object types.
    """
    content_types = models.ManyToManyField(
        to=ContentType,
        related_name='webhooks',
        verbose_name='Object types',
        limit_choices_to=FeatureQuery('webhooks'),
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
    enabled = models.BooleanField(
        default=True
    )
    http_method = models.CharField(
        max_length=30,
        choices=WebhookHttpMethodChoices,
        default=WebhookHttpMethodChoices.METHOD_POST,
        verbose_name='HTTP method'
    )
    http_content_type = models.CharField(
        max_length=100,
        default=HTTP_CONTENT_TYPE_JSON,
        verbose_name='HTTP content type',
        help_text='The complete list of official content types is available '
                  '<a href="https://www.iana.org/assignments/media-types/media-types.xhtml">here</a>.'
    )
    additional_headers = models.TextField(
        blank=True,
        help_text="User-supplied HTTP headers to be sent with the request in addition to the HTTP content type. "
                  "Headers should be defined in the format <code>Name: Value</code>. Jinja2 template processing is "
                  "support with the same context as the request body (below)."
    )
    body_template = models.TextField(
        blank=True,
        help_text='Jinja2 template for a custom request body. If blank, a JSON object representing the change will be '
                  'included. Available context data includes: <code>event</code>, <code>model</code>, '
                  '<code>timestamp</code>, <code>username</code>, <code>request_id</code>, and <code>data</code>.'
    )
    secret = models.CharField(
        max_length=255,
        blank=True,
        help_text="When provided, the request will include a 'X-Hook-Signature' "
                  "header containing a HMAC hex digest of the payload body using "
                  "the secret as the key. The secret is not transmitted in "
                  "the request."
    )
    ssl_verification = models.BooleanField(
        default=True,
        verbose_name='SSL verification',
        help_text="Enable SSL certificate verification. Disable with caution!"
    )
    ca_file_path = models.CharField(
        max_length=4096,
        null=True,
        blank=True,
        verbose_name='CA File Path',
        help_text='The specific CA certificate file to use for SSL verification. '
                  'Leave blank to use the system defaults.'
    )

    class Meta:
        ordering = ('name',)
        unique_together = ('payload_url', 'type_create', 'type_update', 'type_delete',)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        # At least one action type must be selected
        if not self.type_create and not self.type_delete and not self.type_update:
            raise ValidationError(
                "You must select at least one type: create, update, and/or delete."
            )

        # CA file path requires SSL verification enabled
        if not self.ssl_verification and self.ca_file_path:
            raise ValidationError({
                'ca_file_path': 'Do not specify a CA certificate file if SSL verification is disabled.'
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


#
# Custom links
#

class CustomLink(models.Model):
    """
    A custom link to an external representation of a NetBox object. The link text and URL fields accept Jinja2 template
    code to be rendered with an object as context.
    """
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=FeatureQuery('custom_links')
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
        choices=CustomLinkButtonClassChoices,
        default=CustomLinkButtonClassChoices.CLASS_DEFAULT,
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
# Export templates
#

class ExportTemplate(models.Model):
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=FeatureQuery('export_templates')
    )
    name = models.CharField(
        max_length=100
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    template_code = models.TextField(
        help_text='The list of objects being exported is passed as a context variable named <code>queryset</code>.'
    )
    mime_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='MIME type',
        help_text='Defaults to <code>text/plain</code>'
    )
    file_extension = models.CharField(
        max_length=15,
        blank=True,
        help_text='Extension to append to the rendered filename'
    )

    objects = RestrictedQuerySet.as_manager()

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
        output = render_jinja2(self.template_code, context)

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
# Image attachments
#

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

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ('name', 'pk')  # name may be non-unique

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


#
# Config contexts
#

class ConfigContext(ChangeLoggedModel):
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
        max_length=200,
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
    cluster_groups = models.ManyToManyField(
        to='virtualization.ClusterGroup',
        related_name='+',
        blank=True
    )
    clusters = models.ManyToManyField(
        to='virtualization.Cluster',
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
    tags = models.ManyToManyField(
        to='extras.Tag',
        related_name='+',
        blank=True
    )
    data = models.JSONField()

    objects = ConfigContextQuerySet.as_manager()

    class Meta:
        ordering = ['weight', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('extras:configcontext', kwargs={'pk': self.pk})

    def clean(self):
        super().clean()

        # Verify that JSON data is provided as an object
        if type(self.data) is not dict:
            raise ValidationError(
                {'data': 'JSON data must be in object form. Example: {"foo": 123}'}
            )


class ConfigContextModel(models.Model):
    """
    A model which includes local configuration context data. This local data will override any inherited data from
    ConfigContexts.
    """
    local_context_data = models.JSONField(
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

        if not hasattr(self, 'config_context_data'):
            # The annotation is not available, so we fall back to manually querying for the config context objects
            config_context_data = ConfigContext.objects.get_for_object(self, aggregate_data=True)
        else:
            # The attribute may exist, but the annotated value could be None if there is no config context data
            config_context_data = self.config_context_data or []

        for context in config_context_data:
            data = deepmerge(data, context)

        # If the object has local config context data defined, merge it last
        if self.local_context_data:
            data = deepmerge(data, self.local_context_data)

        return data

    def clean(self):
        super().clean()

        # Verify that JSON data is provided as an object
        if self.local_context_data and type(self.local_context_data) is not dict:
            raise ValidationError(
                {'local_context_data': 'JSON data must be in object form. Example: {"foo": 123}'}
            )


#
# Custom scripts
#

@extras_features('job_results')
class Script(models.Model):
    """
    Dummy model used to generate permissions for custom scripts. Does not exist in the database.
    """
    class Meta:
        managed = False


#
# Reports
#

@extras_features('job_results')
class Report(models.Model):
    """
    Dummy model used to generate permissions for reports. Does not exist in the database.
    """
    class Meta:
        managed = False


#
# Job results
#

class JobResult(models.Model):
    """
    This model stores the results from running a user-defined report.
    """
    name = models.CharField(
        max_length=255
    )
    obj_type = models.ForeignKey(
        to=ContentType,
        related_name='job_results',
        verbose_name='Object types',
        limit_choices_to=FeatureQuery('job_results'),
        help_text="The object type to which this job result applies",
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    completed = models.DateTimeField(
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=30,
        choices=JobResultStatusChoices,
        default=JobResultStatusChoices.STATUS_PENDING
    )
    data = models.JSONField(
        null=True,
        blank=True
    )
    job_id = models.UUIDField(
        unique=True
    )

    class Meta:
        ordering = ['obj_type', 'name', '-created']

    def __str__(self):
        return str(self.job_id)

    @property
    def duration(self):
        if not self.completed:
            return None

        duration = self.completed - self.created
        minutes, seconds = divmod(duration.total_seconds(), 60)

        return f"{int(minutes)} minutes, {seconds:.2f} seconds"

    def set_status(self, status):
        """
        Helper method to change the status of the job result. If the target status is terminal, the  completion
        time is also set.
        """
        self.status = status
        if status in JobResultStatusChoices.TERMINAL_STATE_CHOICES:
            self.completed = timezone.now()

    @classmethod
    def enqueue_job(cls, func, name, obj_type, user, *args, **kwargs):
        """
        Create a JobResult instance and enqueue a job using the given callable

        func: The callable object to be enqueued for execution
        name: Name for the JobResult instance
        obj_type: ContentType to link to the JobResult instance obj_type
        user: User object to link to the JobResult instance
        args: additional args passed to the callable
        kwargs: additional kargs passed to the callable
        """
        job_result = cls.objects.create(
            name=name,
            obj_type=obj_type,
            user=user,
            job_id=uuid.uuid4()
        )

        func.delay(*args, job_id=str(job_result.job_id), job_result=job_result, **kwargs)

        return job_result
