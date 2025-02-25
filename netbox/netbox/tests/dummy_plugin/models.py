from django.db import models


class DummyModel(models.Model):
    name = models.CharField(
        max_length=20
    )
    number = models.IntegerField(
        default=100
    )

    class Meta:
        ordering = ['name']
