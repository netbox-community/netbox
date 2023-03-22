import uuid
from functools import cached_property
from hashlib import sha256

import feedparser
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext as _

from utilities.forms import BootstrapMixin
from utilities.templatetags.builtins.filters import render_markdown
from utilities.utils import content_type_identifier, content_type_name, get_viewname
from .utils import register_widget

__all__ = (
    'DashboardWidget',
    'NoteWidget',
    'ObjectCountsWidget',
    'ObjectListWidget',
    'RSSFeedWidget',
)


def get_content_type_labels():
    return [
        (content_type_identifier(ct), content_type_name(ct))
        for ct in ContentType.objects.order_by('app_label', 'model')
    ]


class DashboardWidget:
    default_title = None
    default_config = {}
    description = None
    width = 4
    height = 3

    class ConfigForm(forms.Form):
        pass

    def __init__(self, id=None, title=None, color=None, config=None, width=None, height=None, x=None, y=None):
        self.id = id or str(uuid.uuid4())
        self.config = config or self.default_config
        self.title = title or self.default_title
        self.color = color
        if width:
            self.width = width
        if height:
            self.height = height
        self.x, self.y = x, y

    def __str__(self):
        return self.title or self.__class__.__name__

    def set_layout(self, grid_item):
        self.width = grid_item['w']
        self.height = grid_item['h']
        self.x = grid_item.get('x')
        self.y = grid_item.get('y')

    def render(self, request):
        raise NotImplementedError(f"{self.__class__} must define a render() method.")

    @property
    def name(self):
        return f'{self.__class__.__module__.split(".")[0]}.{self.__class__.__name__}'

    @property
    def form_data(self):
        return {
            'title': self.title,
            'color': self.color,
            'config': self.config,
        }


@register_widget
class NoteWidget(DashboardWidget):
    default_title = _('Note')
    description = _('Display some arbitrary custom content. Markdown is supported.')

    class ConfigForm(BootstrapMixin, forms.Form):
        content = forms.CharField(
            widget=forms.Textarea()
        )

    def render(self, request):
        return render_markdown(self.config.get('content'))


@register_widget
class ObjectCountsWidget(DashboardWidget):
    default_title = _('Object Counts')
    description = _('Display a set of NetBox models and the number of objects created for each type.')
    template_name = 'extras/dashboard/widgets/objectcounts.html'

    class ConfigForm(BootstrapMixin, forms.Form):
        models = forms.MultipleChoiceField(
            choices=get_content_type_labels
        )

    def render(self, request):
        counts = []
        for content_type_id in self.config['models']:
            app_label, model_name = content_type_id.split('.')
            model = ContentType.objects.get_by_natural_key(app_label, model_name).model_class()
            object_count = model.objects.restrict(request.user, 'view').count
            counts.append((model, object_count))

        return render_to_string(self.template_name, {
            'counts': counts,
        })


@register_widget
class ObjectListWidget(DashboardWidget):
    default_title = _('Object List')
    description = _('Display an arbitrary list of objects.')
    template_name = 'extras/dashboard/widgets/objectlist.html'
    width = 12
    height = 4

    class ConfigForm(BootstrapMixin, forms.Form):
        model = forms.ChoiceField(
            choices=get_content_type_labels
        )
        page_size = forms.IntegerField(
            required=False,
            min_value=1,
            max_value=100,
            help_text=_('The default number of objects to display')
        )

    def render(self, request):
        app_label, model_name = self.config['model'].split('.')
        content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
        viewname = get_viewname(content_type.model_class(), action='list')
        try:
            htmx_url = reverse(viewname)
        except NoReverseMatch:
            htmx_url = None

        return render_to_string(self.template_name, {
            'viewname': viewname,
            'htmx_url': htmx_url,
            'page_size': self.config.get('page_size'),
        })


@register_widget
class RSSFeedWidget(DashboardWidget):
    default_title = _('RSS Feed')
    default_config = {
        'max_entries': 10,
        'cache_timeout': 3600,  # seconds
    }
    description = _('Embed an RSS feed from an external website.')
    template_name = 'extras/dashboard/widgets/rssfeed.html'
    width = 6
    height = 4

    class ConfigForm(BootstrapMixin, forms.Form):
        feed_url = forms.URLField(
            label=_('Feed URL')
        )
        max_entries = forms.IntegerField(
            min_value=1,
            max_value=1000,
            help_text=_('The maximum number of objects to display')
        )
        cache_timeout = forms.IntegerField(
            min_value=600,  # 10 minutes
            max_value=86400,  # 24 hours
            help_text=_('How long to stored the cached content (in seconds)')
        )

    def render(self, request):
        url = self.config['feed_url']
        feed = self.get_feed()

        return render_to_string(self.template_name, {
            'url': url,
            'feed': feed,
        })

    @cached_property
    def cache_key(self):
        url = self.config['feed_url']
        url_checksum = sha256(url.encode('utf-8')).hexdigest()
        return f'dashboard_rss_{url_checksum}'

    def get_feed(self):
        # Fetch RSS content from cache
        if feed_content := cache.get(self.cache_key):
            feed = feedparser.FeedParserDict(feed_content)
        else:
            feed = feedparser.parse(self.config['feed_url'])
            # Cap number of entries
            max_entries = self.config.get('max_entries')
            feed['entries'] = feed['entries'][:max_entries]
            cache.set(self.cache_key, dict(feed), self.config.get('cache_timeout'))

        return feed
