from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import HttpResponse
from django.template import Template, Context
from django.utils.safestring import mark_safe

from dcim.models import Site


GRAPH_TYPE_INTERFACE = 100
GRAPH_TYPE_PROVIDER = 200
GRAPH_TYPE_SITE = 300
GRAPH_TYPE_CHOICES = (
    (GRAPH_TYPE_INTERFACE, 'Interface'),
    (GRAPH_TYPE_PROVIDER, 'Provider'),
    (GRAPH_TYPE_SITE, 'Site'),
)

EXPORTTEMPLATE_MODELS = [
    'site', 'rack', 'device', 'consoleport', 'powerport', 'interfaceconnection',
    'aggregate', 'prefix', 'ipaddress', 'vlan',
    'provider', 'circuit'
]

ACTION_CREATE = 1
ACTION_IMPORT = 2
ACTION_EDIT = 3
ACTION_BULK_EDIT = 4
ACTION_DELETE = 5
ACTION_BULK_DELETE = 6
ACTION_CHOICES = (
    (ACTION_CREATE, 'created'),
    (ACTION_IMPORT, 'imported'),
    (ACTION_EDIT, 'modified'),
    (ACTION_BULK_EDIT, 'bulk edited'),
    (ACTION_DELETE, 'deleted'),
    (ACTION_BULK_DELETE, 'bulk deleted')
)


class Graph(models.Model):
    type = models.PositiveSmallIntegerField(choices=GRAPH_TYPE_CHOICES)
    weight = models.PositiveSmallIntegerField(default=1000)
    name = models.CharField(max_length=100, verbose_name='Name')
    source = models.CharField(max_length=500, verbose_name='Source URL')
    link = models.URLField(verbose_name='Link URL', blank=True)

    class Meta:
        ordering = ['type', 'weight', 'name']

    def __unicode__(self):
        return self.name

    def embed_url(self, obj):
        template = Template(self.source)
        return template.render(Context({'obj': obj}))

    def embed_link(self, obj):
        if self.link is None:
            return ''
        template = Template(self.link)
        return template.render(Context({'obj': obj}))


class ExportTemplate(models.Model):
    content_type = models.ForeignKey(ContentType, limit_choices_to={'model__in': EXPORTTEMPLATE_MODELS})
    name = models.CharField(max_length=200)
    template_code = models.TextField()
    mime_type = models.CharField(max_length=15, blank=True)
    file_extension = models.CharField(max_length=15, blank=True)

    class Meta:
        ordering = ['content_type', 'name']
        unique_together = [
            ['content_type', 'name']
        ]

    def __unicode__(self):
        return "{}: {}".format(self.content_type, self.name)

    def to_response(self, context_dict, filename):
        """
        Render the template to an HTTP response, delivered as a named file attachment
        """
        template = Template(self.template_code)
        mime_type = 'text/plain' if not self.mime_type else self.mime_type
        response = HttpResponse(
            template.render(Context(context_dict)),
            content_type=mime_type
        )
        if self.file_extension:
            filename += '.{}'.format(self.file_extension)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response


class TopologyMap(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    site = models.ForeignKey(Site, related_name='topology_maps', blank=True, null=True)
    device_patterns = models.TextField(help_text="Identify devices to include in the diagram using regular expressions,"
                                                 "one per line. Each line will result in a new tier of the drawing. "
                                                 "Separate multiple regexes on a line using commas. Devices will be "
                                                 "rendered in the order they are defined.")
    description = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @property
    def device_sets(self):
        if not self.device_patterns:
            return None
        return [line.strip() for line in self.device_patterns.split('\n')]


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

    def log_bulk_edit(self, user, content_type, message=''):
        self.log_bulk_action(user, content_type, ACTION_BULK_EDIT, message)

    def log_bulk_delete(self, user, content_type, message=''):
        self.log_bulk_action(user, content_type, ACTION_BULK_DELETE, message)


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

    def __unicode__(self):
        if self.message:
            return u'{} {}'.format(self.user, self.message)
        return u'{} {} {}'.format(self.user, self.get_action_display(), self.content_type)

    def icon(self):
        if self.action in [ACTION_CREATE, ACTION_IMPORT]:
            return mark_safe('<i class="glyphicon glyphicon-plus text-success"></i>')
        elif self.action in [ACTION_EDIT, ACTION_BULK_EDIT]:
            return mark_safe('<i class="glyphicon glyphicon-pencil text-warning"></i>')
        elif self.action in [ACTION_DELETE, ACTION_BULK_DELETE]:
            return mark_safe('<i class="glyphicon glyphicon-remove text-danger"></i>')
        else:
            return ''
