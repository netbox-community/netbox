from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class LogItem(models.Model):

    for_device = models.ForeignKey(
        'dcim.Device',
        on_delete=models.CASCADE,
        related_name='logs',
        default='1',
    )
    body = models.TextField(default='')
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        default='1'
    )

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'
        ordering = ['-created_at']
