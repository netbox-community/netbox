from django.db import models
from django.utils.text import slugify
from taggit.models import TagBase, GenericTaggedItemBase

from extras.models import ChangeLoggedModel
from utilities.choices import ColorChoices
from utilities.fields import ColorField
from utilities.querysets import RestrictedQuerySet


#
# Tags
#

class Tag(TagBase, ChangeLoggedModel):
    color = ColorField(
        default=ColorChoices.COLOR_GREY
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )

    objects = RestrictedQuerySet.as_manager()

    csv_headers = ['name', 'slug', 'color', 'description']

    class Meta:
        ordering = ['name']

    def slugify(self, tag, i=None):
        # Allow Unicode in Tag slugs (avoids empty slugs for Tags with all-Unicode names)
        slug = slugify(tag, allow_unicode=True)
        if i is not None:
            slug += "_%d" % i
        return slug

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.color,
            self.description
        )


class TaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(
        to=Tag,
        related_name="%(app_label)s_%(class)s_items",
        on_delete=models.CASCADE
    )

    class Meta:
        index_together = (
            ("content_type", "object_id")
        )
