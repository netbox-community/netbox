from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import ChangeLoggedModel, NestedGroupModel, OrganizationalModel, PrimaryModel
from tenancy.choices import *

__all__ = (
    'ContactAssignment',
    'Contact',
    'ContactGroup',
    'ContactRole',
)


class ContactGroup(NestedGroupModel):
    """
    An arbitrary collection of Contacts.
    """
    class Meta:
        ordering = ['name']
        constraints = (
            models.UniqueConstraint(
                fields=('parent', 'name'),
                name='%(app_label)s_%(class)s_unique_parent_name'
            ),
        )

    def get_absolute_url(self):
        return reverse('tenancy:contactgroup', args=[self.pk])


class ContactRole(OrganizationalModel):
    """
    Functional role for a Contact assigned to an object.
    """
    def get_absolute_url(self):
        return reverse('tenancy:contactrole', args=[self.pk])


class Contact(PrimaryModel):
    """
    Contact information for a particular object(s) in NetBox.
    """
    group = models.ForeignKey(
        to='tenancy.ContactGroup',
        on_delete=models.SET_NULL,
        related_name='contacts',
        blank=True,
        null=True
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100
    )
    title = models.CharField(
        verbose_name=_('title'),
        max_length=100,
        blank=True
    )
    phone = models.CharField(
        verbose_name=_('phone'),
        max_length=50,
        blank=True
    )
    email = models.EmailField(
        verbose_name=_('email'),
        blank=True
    )
    address = models.CharField(
        verbose_name=_('address'),
        max_length=200,
        blank=True
    )
    link = models.URLField(
        verbose_name=_('link'),
        blank=True
    )

    clone_fields = (
        'group', 'name', 'title', 'phone', 'email', 'address', 'link',
    )

    class Meta:
        ordering = ['name']
        constraints = (
            models.UniqueConstraint(
                fields=('group', 'name'),
                name='%(app_label)s_%(class)s_unique_group_name'
            ),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tenancy:contact', args=[self.pk])


class ContactAssignment(ChangeLoggedModel):
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveBigIntegerField()
    object = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id'
    )
    contact = models.ForeignKey(
        to='tenancy.Contact',
        on_delete=models.PROTECT,
        related_name='assignments'
    )
    role = models.ForeignKey(
        to='tenancy.ContactRole',
        on_delete=models.PROTECT,
        related_name='assignments'
    )
    priority = models.CharField(
        verbose_name=_('priority'),
        max_length=50,
        choices=ContactPriorityChoices,
        blank=True
    )

    clone_fields = ('content_type', 'object_id', 'role', 'priority')

    class Meta:
        ordering = ('priority', 'contact')
        constraints = (
            models.UniqueConstraint(
                fields=('content_type', 'object_id', 'contact', 'role'),
                name='%(app_label)s_%(class)s_unique_object_contact_role'
            ),
        )

    def __str__(self):
        if self.priority:
            return f"{self.contact} ({self.get_priority_display()}) -> {self.object}"
        return str(f"{self.contact} -> {self.object}")

    def get_absolute_url(self):
        return reverse('tenancy:contact', args=[self.contact.pk])

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.object
        return objectchange
