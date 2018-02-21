from __future__ import unicode_literals

from django import template

from extras.models import ExportTemplate

register = template.Library()


@register.inclusion_tag('buttons/add.html')
def add_button(url):
    return {'add_url': url}


@register.inclusion_tag('buttons/import.html')
def import_button(url):
    return {'import_url': url}


@register.inclusion_tag('buttons/export.html', takes_context=True)
def export_button(context, content_type=None):
    export_templates = ExportTemplate.objects.filter(content_type=content_type)
    return {
        'url_params': context['request'].GET,
        'export_templates': export_templates,
    }
