from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from taggit.models import TagBase, GenericTaggedItemBase

from extras.utils import extras_features
from netbox.models import BigIDModel, ChangeLoggedModel
from utilities.choices import ColorChoices
from utilities.fields import ColorField
from utilities.querysets import RestrictedQuerySet


#
# Tags
#

@extras_features('webhooks')
class Tag(ChangeLoggedModel, TagBase):
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

    def get_absolute_url(self):
        return reverse('extras:tag', args=[self.pk])

    def slugify(self, tag, i=None):
        # Allow Unicode in Tag slugs (avoids empty slugs for Tags with all-Unicode names)
        slug = slugify(tag, allow_unicode=True)
        if i is not None:
            slug += "_%d" % i
        return slug


class TaggedItem(BigIDModel, GenericTaggedItemBase):
    tag = models.ForeignKey(
        to=Tag,
        related_name="%(app_label)s_%(class)s_items",
        on_delete=models.CASCADE
    )

    class Meta:
        index_together = (
            ("content_type", "object_id")
        )
