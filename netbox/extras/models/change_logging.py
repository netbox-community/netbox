from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.models import ContentType
from extras.choices import *
from ..querysets import ObjectChangeQuerySet

__all__ = (
    'ObjectChange',
)


class ObjectChange(models.Model):
    """
    Record a change to an object and the user account associated with that change. A change record may optionally
    indicate an object related to the one being changed. For example, a change to an interface may also indicate the
    parent device. This will ensure changes made to component models appear in the parent model's changelog.
    """
    time = models.DateTimeField(
        verbose_name=_('time'),
        auto_now_add=True,
        editable=False,
        db_index=True
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='changes',
        blank=True,
        null=True
    )
    user_name = models.CharField(
        verbose_name=_('user name'),
        max_length=150,
        editable=False
    )
    request_id = models.UUIDField(
        verbose_name=_('request ID'),
        editable=False,
        db_index=True
    )
    action = models.CharField(
        verbose_name=_('action'),
        max_length=50,
        choices=ObjectChangeActionChoices
    )
    changed_object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.PROTECT,
        related_name='+'
    )
    changed_object_id = models.PositiveBigIntegerField()
    changed_object = GenericForeignKey(
        ct_field='changed_object_type',
        fk_field='changed_object_id'
    )
    related_object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    related_object_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    related_object = GenericForeignKey(
        ct_field='related_object_type',
        fk_field='related_object_id'
    )
    object_repr = models.CharField(
        max_length=200,
        editable=False
    )
    prechange_data = models.JSONField(
        verbose_name=_('pre-change data'),
        editable=False,
        blank=True,
        null=True
    )
    postchange_data = models.JSONField(
        verbose_name=_('post-change data'),
        editable=False,
        blank=True,
        null=True
    )

    objects = ObjectChangeQuerySet.as_manager()

    class Meta:
        ordering = ['-time']
        indexes = (
            models.Index(fields=('changed_object_type', 'changed_object_id')),
            models.Index(fields=('related_object_type', 'related_object_id')),
        )
        verbose_name = _('object change')
        verbose_name_plural = _('object changes')

    def __str__(self):
        return '{} {} {} by {}'.format(
            self.changed_object_type,
            self.object_repr,
            self.get_action_display().lower(),
            self.user_name
        )

    def clean(self):
        super().clean()

        # Validate the assigned object type
        if self.changed_object_type not in ContentType.objects.with_feature('change_logging'):
            raise ValidationError(
                _("Change logging is not supported for this object type ({type}).").format(
                    type=self.changed_object_type
                )
            )

    def save(self, *args, **kwargs):

        # Record the user's name and the object's representation as static strings
        if not self.user_name:
            self.user_name = self.user.username
        if not self.object_repr:
            self.object_repr = str(self.changed_object)

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('extras:objectchange', args=[self.pk])

    def get_action_color(self):
        return ObjectChangeActionChoices.colors.get(self.action)
