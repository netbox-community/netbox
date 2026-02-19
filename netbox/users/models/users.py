from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import (
    GroupManager as DjangoGroupManager,
)
from django.contrib.auth.models import (
    Permission,
    PermissionsMixin,
)
from django.contrib.auth.models import (
    UserManager as DjangoUserManager,
)
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utilities.querysets import RestrictedQuerySet

__all__ = (
    'Group',
    'GroupManager',
    'User',
    'UserManager',
)


class GroupManager(DjangoGroupManager.from_queryset(RestrictedQuerySet)):
    pass


class Group(models.Model):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=150,
        unique=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    object_permissions = models.ManyToManyField(
        to='users.ObjectPermission',
        blank=True,
        related_name='groups'
    )

    # Replicate legacy Django permissions support from stock Group model
    # to ensure authentication backend compatibility
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("permissions"),
        blank=True,
        related_name='groups',
        related_query_name='group'
    )

    objects = GroupManager()

    class Meta:
        ordering = ('name',)
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('users:group', args=[self.pk])

    def natural_key(self):
        return (self.name,)


class UserManager(DjangoUserManager.from_queryset(RestrictedQuerySet)):

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    create_user.alters_data = True

    async def acreate_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return await self._acreate_user(username, email, password, **extra_fields)

    acreate_user.alters_data = True

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

    create_superuser.alters_data = True

    async def acreate_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return await self._acreate_user(username, email, password, **extra_fields)

    acreate_superuser.alters_data = True


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(
        _("first name"),
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        _("last name"),
        max_length=150,
        blank=True,
    )
    email = models.EmailField(
        _("email address"),
        blank=True,
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(
        _("date joined"),
        default=timezone.now,
    )
    groups = models.ManyToManyField(
        to='users.Group',
        verbose_name=_('groups'),
        blank=True,
        related_name='users',
        related_query_name='user'
    )
    object_permissions = models.ManyToManyField(
        to='users.ObjectPermission',
        blank=True,
        related_name='users'
    )

    objects = UserManager()

    # Ensure compatibility with Django's stock User model
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        ordering = ('username',)
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return reverse('users:user', args=[self.pk])

    def clean(self):
        super().clean()

        # Normalize email address
        self.email = self.__class__.objects.normalize_email(self.email)

        # Check for any existing Users with names that differ only in case
        model = self._meta.model
        if model.objects.exclude(pk=self.pk).filter(username__iexact=self.username).exists():
            raise ValidationError(_("A user with this username already exists."))

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
