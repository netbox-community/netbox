from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from taggit.models import TagBase, GenericTaggedItemBase

from netbox.models import ChangeLoggedModel
from netbox.models.features import CloningMixin, ExportTemplatesMixin, WebhooksMixin
from utilities.choices import ColorChoices
from utilities.fields import ColorField


#
# Tags
#

class Tag(CloningMixin, ExportTemplatesMixin, WebhooksMixin, ChangeLoggedModel, TagBase):
    id = models.BigAutoField(
        primary_key=True
    )
    color = ColorField(
        default=ColorChoices.COLOR_GREY
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )

    clone_fields = (
        'color', 'description',
    )

    class Meta:
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('extras:tag', args=[self.pk])

    @property
    def docs_url(self):
        return f'{settings.STATIC_URL}docs/models/extras/tag/'

    def slugify(self, tag, i=None):
        # Allow Unicode in Tag slugs (avoids empty slugs for Tags with all-Unicode names)
        slug = slugify(tag, allow_unicode=True)
        if i is not None:
            slug += "_%d" % i
        return slug


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
