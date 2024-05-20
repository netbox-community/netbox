import logging
import uuid
from functools import cached_property
from hashlib import sha256
from urllib.parse import urlencode

import feedparser
import requests
from django import forms
from django.conf import settings
from django.core.cache import cache
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, resolve, reverse
from django.utils.translation import gettext as _

from core.models import ObjectType
from extras.choices import BookmarkOrderingChoices
from netbox.choices import ButtonColorChoices
from utilities.object_types import object_type_identifier, object_type_name
from utilities.permissions import get_permission_for_model
from utilities.querydict import dict_to_querydict
from utilities.templatetags.builtins.filters import render_markdown
from utilities.views import get_viewname
from .utils import register_widget

__all__ = (
    'BookmarksWidget',
    'DashboardWidget',
    'NoteWidget',
    'ObjectCountsWidget',
    'ObjectListWidget',
    'RSSFeedWidget',
    'WidgetConfigForm',
)

logger = logging.getLogger('netbox.data_backends')


def get_object_type_choices():
    return [
        (object_type_identifier(ot), object_type_name(ot))
        for ot in ObjectType.objects.public().order_by('app_label', 'model')
    ]


def get_bookmarks_object_type_choices():
    return [
        (object_type_identifier(ot), object_type_name(ot))
        for ot in ObjectType.objects.with_feature('bookmarks').order_by('app_label', 'model')
    ]


def get_models_from_content_types(content_types):
    """
    Return a list of models corresponding to the given content types, identified by natural key.
    """
    models = []
    for content_type_id in content_types:
        app_label, model_name = content_type_id.split('.')
        try:
            content_type = ObjectType.objects.get_by_natural_key(app_label, model_name)
            if content_type.model_class():
                models.append(content_type.model_class())
            else:
                logger.debug(f"Dashboard Widget model_class not found: {app_label}:{model_name}")
        except ObjectType.DoesNotExist:
            logger.debug(f"Dashboard Widget ObjectType not found: {app_label}:{model_name}")

    return models


class WidgetConfigForm(forms.Form):
    pass


class DashboardWidget:
    """
    Base class for custom dashboard widgets.

    Attributes:
        description: A brief, user-friendly description of the widget's function
        default_title: The string to show for the widget's title when none has been specified.
        default_config: Default configuration parameters, as a dictionary mapping
        width: The widget's default width (1 to 12)
        height: The widget's default height; the number of rows it consumes
    """
    description = None
    default_title = None
    default_config = {}
    width = 4
    height = 3

    class ConfigForm(WidgetConfigForm):
        """
        The widget's configuration form.
        """
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
        self.width = grid_item.get('w', 1)
        self.height = grid_item.get('h', 1)
        self.x = grid_item.get('x')
        self.y = grid_item.get('y')

    def render(self, request):
        """
        This method is called to render the widget's content.

        Params:
            request: The current request
        """
        raise NotImplementedError(_("{class_name} must define a render() method.").format(
            class_name=self.__class__
        ))

    @property
    def name(self):
        return f'{self.__class__.__module__.split(".")[0]}.{self.__class__.__name__}'

    @property
    def fg_color(self):
        """
        Return the appropriate foreground (text) color for the widget's color.
        """
        if self.color in (
            ButtonColorChoices.CYAN,
            ButtonColorChoices.GRAY,
            ButtonColorChoices.GREY,
            ButtonColorChoices.TEAL,
            ButtonColorChoices.WHITE,
            ButtonColorChoices.YELLOW,
        ):
            return ButtonColorChoices.BLACK
        return ButtonColorChoices.WHITE

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

    class ConfigForm(WidgetConfigForm):
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

    class ConfigForm(WidgetConfigForm):
        models = forms.MultipleChoiceField(
            choices=get_object_type_choices
        )
        filters = forms.JSONField(
            required=False,
            label='Object filters',
            help_text=_("Filters to apply when counting the number of objects")
        )

        def clean_filters(self):
            if data := self.cleaned_data['filters']:
                try:
                    dict(data)
                except TypeError:
                    raise forms.ValidationError(_("Invalid format. Object filters must be passed as a dictionary."))
            return data

    def render(self, request):
        counts = []
        for model in get_models_from_content_types(self.config['models']):
            permission = get_permission_for_model(model, 'view')
            if request.user.has_perm(permission):
                url = reverse(get_viewname(model, 'list'))
                qs = model.objects.restrict(request.user, 'view')
                # Apply any specified filters
                if filters := self.config.get('filters'):
                    params = dict_to_querydict(filters)
                    filterset = getattr(resolve(url).func.view_class, 'filterset', None)
                    qs = filterset(params, qs).qs
                    url = f'{url}?{params.urlencode()}'
                object_count = qs.count
                counts.append((model, object_count, url))
            else:
                counts.append((model, None, None))

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

    class ConfigForm(WidgetConfigForm):
        model = forms.ChoiceField(
            choices=get_object_type_choices
        )
        page_size = forms.IntegerField(
            required=False,
            min_value=1,
            max_value=100,
            help_text=_('The default number of objects to display')
        )
        url_params = forms.JSONField(
            required=False,
            label='URL parameters'
        )

        def clean_url_params(self):
            if data := self.cleaned_data['url_params']:
                try:
                    urlencode(data)
                except (TypeError, ValueError):
                    raise forms.ValidationError(_("Invalid format. URL parameters must be passed as a dictionary."))
            return data

    def render(self, request):
        app_label, model_name = self.config['model'].split('.')
        model = ObjectType.objects.get_by_natural_key(app_label, model_name).model_class()
        viewname = get_viewname(model, action='list')

        # Evaluate user's permission. Note that this controls only whether the HTMX element is
        # embedded on the page: The view itself will also evaluate permissions separately.
        permission = get_permission_for_model(model, 'view')
        has_permission = request.user.has_perm(permission)

        try:
            htmx_url = reverse(viewname)
        except NoReverseMatch:
            htmx_url = None
        parameters = self.config.get('url_params') or {}
        if page_size := self.config.get('page_size'):
            parameters['per_page'] = page_size

        if parameters:
            try:
                htmx_url = f'{htmx_url}?{urlencode(parameters, doseq=True)}'
            except ValueError:
                pass
        return render_to_string(self.template_name, {
            'viewname': viewname,
            'has_permission': has_permission,
            'htmx_url': htmx_url,
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

    class ConfigForm(WidgetConfigForm):
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
        return render_to_string(self.template_name, {
            'url': self.config['feed_url'],
            **self.get_feed()
        })

    @cached_property
    def cache_key(self):
        url = self.config['feed_url']
        url_checksum = sha256(url.encode('utf-8')).hexdigest()
        return f'dashboard_rss_{url_checksum}'

    def get_feed(self):
        # Fetch RSS content from cache if available
        if feed_content := cache.get(self.cache_key):
            return {
                'feed': feedparser.FeedParserDict(feed_content),
            }

        # Fetch feed content from remote server
        try:
            response = requests.get(
                url=self.config['feed_url'],
                headers={'User-Agent': f'NetBox/{settings.VERSION}'},
                proxies=settings.HTTP_PROXIES,
                timeout=3
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {
                'error': e,
            }

        # Parse feed content
        feed = feedparser.parse(response.content)
        if not feed.bozo:
            # Cap number of entries
            max_entries = self.config.get('max_entries')
            feed['entries'] = feed['entries'][:max_entries]
            # Cache the feed content
            cache.set(self.cache_key, dict(feed), self.config.get('cache_timeout'))

        return {
            'feed': feed,
        }


@register_widget
class BookmarksWidget(DashboardWidget):
    default_title = _('Bookmarks')
    default_config = {
        'order_by': BookmarkOrderingChoices.ORDERING_NEWEST,
    }
    description = _('Show your personal bookmarks')
    template_name = 'extras/dashboard/widgets/bookmarks.html'

    class ConfigForm(WidgetConfigForm):
        object_types = forms.MultipleChoiceField(
            choices=get_bookmarks_object_type_choices,
            required=False
        )
        order_by = forms.ChoiceField(
            choices=BookmarkOrderingChoices
        )
        max_items = forms.IntegerField(
            min_value=1,
            required=False
        )

    def render(self, request):
        from extras.models import Bookmark

        if request.user.is_anonymous:
            bookmarks = list()
        else:
            bookmarks = Bookmark.objects.filter(user=request.user).order_by(self.config['order_by'])
            if object_types := self.config.get('object_types'):
                models = get_models_from_content_types(object_types)
                conent_types = ObjectType.objects.get_for_models(*models).values()
                bookmarks = bookmarks.filter(object_type__in=conent_types)
            if max_items := self.config.get('max_items'):
                bookmarks = bookmarks[:max_items]

        return render_to_string(self.template_name, {
            'bookmarks': bookmarks,
        })
