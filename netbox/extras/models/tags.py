from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from taggit.models import TagBase, GenericTaggedItemBase

from netbox.choices import ColorChoices
from netbox.models import ChangeLoggedModel
from netbox.models.features import CloningMixin, ExportTemplatesMixin
from utilities.fields import ColorField
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'Tag',
    'TaggedItem',
)


#
# Tags
#

class Tag(CloningMixin, ExportTemplatesMixin, ChangeLoggedModel, TagBase):
    id = models.BigAutoField(
        primary_key=True
    )
    color = ColorField(
        verbose_name=_('color'),
        default=ColorChoices.COLOR_GREY
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True,
    )
    object_types = models.ManyToManyField(
        to='contenttypes.ContentType',
        related_name='+',
        blank=True,
        help_text=_("The object type(s) to which this tag can be applied.")
    )
    weight = models.PositiveSmallIntegerField(
        verbose_name=_('weight'),
        default=1000,
    )

    clone_fields = (
        'color', 'description', 'object_types',
    )

    class Meta:
        ordering = ('weight', 'name')
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

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

    _netbox_private = True
    objects = RestrictedQuerySet.as_manager()

    class Meta:
        indexes = [models.Index(fields=["content_type", "object_id"])]
        verbose_name = _('tagged item')
        verbose_name_plural = _('tagged items')
        # Note: while there is no ordering applied here (because it would basically be done on fields
        # of the related `tag`), there is an ordering applied to extras.api.views.TaggedItemViewSet
        # to allow for proper pagination.
