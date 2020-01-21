from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dcim.models import Site
from extras.choices import TemplateLanguageChoices
from extras.models import Graph, Tag


class GraphTest(TestCase):

    def setUp(self):

        self.site = Site(name='Site 1', slug='site-1')

    def test_graph_render_django(self):

        # Using the pluralize filter as a sanity check (it's only available in Django)
        TEMPLATE_TEXT = "{{ obj.name|lower }} thing{{ 2|pluralize }}"
        RENDERED_TEXT = "site 1 things"

        graph = Graph(
            type=ContentType.objects.get(app_label='dcim', model='site'),
            name='Graph 1',
            template_language=TemplateLanguageChoices.LANGUAGE_DJANGO,
            source=TEMPLATE_TEXT,
            link=TEMPLATE_TEXT
        )

        self.assertEqual(graph.embed_url(self.site), RENDERED_TEXT)
        self.assertEqual(graph.embed_link(self.site), RENDERED_TEXT)

    def test_graph_render_jinja2(self):

        TEMPLATE_TEXT = "{{ [obj.name, obj.slug]|join(',') }}"
        RENDERED_TEXT = "Site 1,site-1"

        graph = Graph(
            type=ContentType.objects.get(app_label='dcim', model='site'),
            name='Graph 1',
            template_language=TemplateLanguageChoices.LANGUAGE_JINJA2,
            source=TEMPLATE_TEXT,
            link=TEMPLATE_TEXT
        )

        self.assertEqual(graph.embed_url(self.site), RENDERED_TEXT)
        self.assertEqual(graph.embed_link(self.site), RENDERED_TEXT)


class TagTest(TestCase):

    def test_create_tag_unicode(self):
        tag = Tag(name='Testing Unicode: 台灣')
        tag.save()

        self.assertEqual(tag.slug, 'testing-unicode-台灣')
