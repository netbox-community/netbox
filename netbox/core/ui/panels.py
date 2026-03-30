from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs, panels


class DataSourcePanel(panels.ObjectAttributesPanel):
    title = _('Data Source')
    name = attrs.TextAttr('name')
    type = attrs.ChoiceAttr('type')
    enabled = attrs.BooleanAttr('enabled')
    status = attrs.ChoiceAttr('status')
    sync_interval = attrs.ChoiceAttr('sync_interval', label=_('Sync interval'))
    last_synced = attrs.DateTimeAttr('last_synced', label=_('Last synced'))
    description = attrs.TextAttr('description')
    source_url = attrs.TemplatedAttr(
        'source_url',
        label=_('URL'),
        template_name='core/datasource/attrs/source_url.html',
    )
    ignore_rules = attrs.TemplatedAttr(
        'ignore_rules',
        label=_('Ignore rules'),
        template_name='core/datasource/attrs/ignore_rules.html',
    )


class DataSourceBackendPanel(panels.ObjectPanel):
    template_name = 'core/panels/datasource_backend.html'
    title = _('Backend')


class DataFilePanel(panels.ObjectAttributesPanel):
    title = _('Data File')
    source = attrs.RelatedObjectAttr('source', linkify=True)
    path = attrs.TextAttr('path', style='font-monospace', copy_button=True)
    last_updated = attrs.DateTimeAttr('last_updated')
    size = attrs.TemplatedAttr('size', template_name='core/datafile/attrs/size.html')
    hash = attrs.TextAttr('hash', label=_('SHA256 hash'), style='font-monospace', copy_button=True)


class DataFileContentPanel(panels.ObjectPanel):
    template_name = 'core/panels/datafile_content.html'
    title = _('Content')


class JobPanel(panels.ObjectAttributesPanel):
    title = _('Job')
    object_type = attrs.TemplatedAttr(
        'object_type',
        label=_('Object type'),
        template_name='core/job/attrs/object_type.html',
    )
    name = attrs.TextAttr('name')
    status = attrs.ChoiceAttr('status')
    error = attrs.TextAttr('error')
    user = attrs.TextAttr('user', label=_('Created by'))


class JobSchedulingPanel(panels.ObjectAttributesPanel):
    title = _('Scheduling')
    created = attrs.DateTimeAttr('created')
    scheduled = attrs.TemplatedAttr('scheduled', template_name='core/job/attrs/scheduled.html')
    started = attrs.DateTimeAttr('started')
    completed = attrs.DateTimeAttr('completed')
    queue = attrs.TextAttr('queue_name', label=_('Queue'))


class ObjectChangePanel(panels.ObjectAttributesPanel):
    title = _('Change')
    time = attrs.DateTimeAttr('time')
    user = attrs.TemplatedAttr(
        'user_name',
        label=_('User'),
        template_name='core/objectchange/attrs/user.html',
    )
    action = attrs.ChoiceAttr('action')
    changed_object_type = attrs.TextAttr(
        'changed_object_type',
        label=_('Object type'),
    )
    changed_object = attrs.TemplatedAttr(
        'object_repr',
        label=_('Object'),
        template_name='core/objectchange/attrs/changed_object.html',
    )
    message = attrs.TextAttr('message')
    request_id = attrs.TemplatedAttr(
        'request_id',
        label=_('Request ID'),
        template_name='core/objectchange/attrs/request_id.html',
    )
