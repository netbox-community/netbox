from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

__all__ = (
    'CachedValue',
)


class CachedValue(models.Model):
    timestamp = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    object_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        related_name='+'
    )
    object_id = models.PositiveBigIntegerField()
    object = GenericForeignKey(
        ct_field='object_type',
        fk_field='object_id'
    )
    field = models.CharField(
        max_length=200
    )
    type = models.CharField(
        max_length=30
    )
    value = models.TextField()
    weight = models.PositiveSmallIntegerField(
        default=1000
    )

    class Meta:
        ordering = ('weight', 'pk')

    def __str__(self):
        return f'{self.object_type} {self.object_id}: {self.field}={self.value}'
