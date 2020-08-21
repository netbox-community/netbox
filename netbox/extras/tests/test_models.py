from django.test import TestCase

from extras.models import Tag


class TagTest(TestCase):

    def test_create_tag_unicode(self):
        tag = Tag(name='Testing Unicode: 台灣')
        tag.save()

        self.assertEqual(tag.slug, 'testing-unicode-台灣')
