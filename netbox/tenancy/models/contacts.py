from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from netbox.models import ChangeLoggedModel, NestedGroupModel, OrganizationalModel, PrimaryModel
from netbox.models.features import CustomFieldsMixin, ExportTemplatesMixin, TagsMixin
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
        verbose_name = _('contact group')
        verbose_name_plural = _('contact groups')


class ContactRole(OrganizationalModel):
    """
    Functional role for a Contact assigned to an object.
    """
    class Meta:
        ordering = ('name',)
        verbose_name = _('contact role')
        verbose_name_plural = _('contact roles')


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
        max_length=100,
        db_collation="natural_sort"
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
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')

    def __str__(self):
        return self.name


class ContactAssignment(CustomFieldsMixin, ExportTemplatesMixin, TagsMixin, ChangeLoggedModel):
    object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.CASCADE
    )
    object_id = models.PositiveBigIntegerField()
    object = GenericForeignKey(
        ct_field='object_type',
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
        blank=True,
        null=True
    )

    clone_fields = ('object_type', 'object_id', 'role', 'priority')

    class Meta:
        ordering = ('contact', 'priority', 'role', 'pk')
        indexes = (
            models.Index(fields=('object_type', 'object_id')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('object_type', 'object_id', 'contact', 'role'),
                name='%(app_label)s_%(class)s_unique_object_contact_role'
            ),
        )
        verbose_name = _('contact assignment')
        verbose_name_plural = _('contact assignments')

    def __str__(self):
        if self.priority:
            return f"{self.contact} ({self.get_priority_display()}) -> {self.object}"
        return str(f"{self.contact} -> {self.object}")

    def get_absolute_url(self):
        return reverse('tenancy:contact', args=[self.contact.pk])

    def clean(self):
        super().clean()

        # Validate the assigned object type
        if self.object_type not in ObjectType.objects.with_feature('contacts'):
            raise ValidationError(
                _("Contacts cannot be assigned to this object type ({type}).").format(type=self.object_type)
            )

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.object
        return objectchange
