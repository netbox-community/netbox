from django.template import Context, Template
from django.test import TestCase

from dcim.models import Site
from netbox.tables import NetBoxTable, columns
from utilities.testing import create_tags


class TagColumnTable(NetBoxTable):
    tags = columns.TagColumn(url_name='dcim:site_list')

    class Meta(NetBoxTable.Meta):
        model = Site
        fields = ('pk', 'name', 'tags',)
        default_columns = fields


class TagColumnTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        sites = [
            Site(name=f'Site {i}', slug=f'site-{i}') for i in range(1, 6)
        ]
        Site.objects.bulk_create(sites)
        for site in sites:
            site.tags.add(*tags)

    def test_tagcolumn(self):
        template = Template('{% load render_table from django_tables2 %}{% render_table table %}')
        table = TagColumnTable(Site.objects.all(), orderable=False)
        context = Context({
            'table': table
        })
        template.render(context)
