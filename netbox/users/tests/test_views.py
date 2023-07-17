from decimal import Decimal

import yaml
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from dcim.choices import *
from dcim.constants import *
from users.models import *
from utilities.testing import ViewTestCases, TestCase


class UserTestCase(ViewTestCases.UserViewTestCase):
    model = NetBoxUser

    @classmethod
    def setUpTestData(cls):

        users = (
            NetBoxUser(username='username1', first_name='first1', last_name='last1', email='user1@foo.com', password='pass1xxx'),
            NetBoxUser(username='username2', first_name='first2', last_name='last2', email='user2@foo.com', password='pass2xxx'),
            NetBoxUser(username='username3', first_name='first3', last_name='last3', email='user3@foo.com', password='pass3xxx'),
        )
        NetBoxUser.objects.bulk_create(users)

        cls.form_data = {
            'username': 'usernamex',
            'first_name': 'firstx',
            'last_name': 'lastx',
            'email': 'userx@foo.com',
            'password': 'pass1xxx',
            'confirm_password': 'pass1xxx',
        }

        cls.csv_data = (
            "username,first_name,last_name,email,password",
            "username4,first4,last4,email4@foo.com,pass4xxx",
            "username5,first5,last5,email5@foo.com,pass5xxx",
            "username6,first6,last6,email6@foo.com,pass6xxx",
        )

        cls.csv_update_data = (
            "id,first_name,last_name",
            f"{users[0].pk},first7,last7",
            f"{users[1].pk},first8,last8",
            f"{users[2].pk},first9,last9",
        )

        cls.bulk_edit_data = {
            'last_name': 'newlastname',
        }


class GroupTestCase(ViewTestCases.GroupViewTestCase):
    model = NetBoxGroup

    @classmethod
    def setUpTestData(cls):

        groups = (
            Group(name='group1', ),
            Group(name='group2', ),
            Group(name='group3', ),
        )
        Group.objects.bulk_create(groups)

        cls.form_data = {
            'name': 'groupx',
        }

        cls.csv_data = (
            "name",
            "group4"
            "group5"
            "group6"
        )

        cls.csv_update_data = (
            "id,name",
            f"{groups[0].pk},group7",
            f"{groups[1].pk},group8",
            f"{groups[2].pk},group9",
        )


class ObjectPermissionTestCase(ViewTestCases.ObjectPermissionViewTestCase):
    model = ObjectPermission

    @classmethod
    def setUpTestData(cls):

        from dcim.models import Site
        ct = ContentType.objects.get_for_model(Site)

        # Create three Regions
        permissions = (
            ObjectPermission(name='Permission 1', actions=['view', 'add', 'delete']),
            ObjectPermission(name='Permission 2', actions=['view', 'add', 'delete']),
            ObjectPermission(name='Permission 3', actions=['view', 'add', 'delete']),
        )
        ObjectPermission.objects.bulk_create(permissions)

        cls.form_data = {
            'name': 'Permission X',
            'description': 'A new permission',
            'object_types': [ct.pk,],
            'actions': 'view,edit,delete',
        }

        cls.csv_data = (
            "name",
            "permission4"
            "permission5"
            "permission6"
        )

        cls.csv_update_data = (
            "id,name,actions",
            f"{permissions[0].pk},permission7",
            f"{permissions[1].pk},permission8",
            f"{permissions[2].pk},permission9",
        )

        cls.bulk_edit_data = {
            'description': 'New description',
        }
