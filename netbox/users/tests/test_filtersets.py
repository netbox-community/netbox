import datetime

from django.test import TestCase
from django.utils.timezone import make_aware

from core.models import ObjectType
from users import filtersets
from users.models import Group, ObjectPermission, Owner, OwnerGroup, Token, User
from utilities.testing import BaseFilterSetTests


class UserTestCase(TestCase, BaseFilterSetTests):
    queryset = User.objects.all()
    filterset = filtersets.UserFilterSet
    ignore_fields = ('config', 'dashboard', 'password', 'user_permissions')

    @classmethod
    def setUpTestData(cls):

        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

        users = (
            User(
                username='User1',
                first_name='Hank',
                last_name='Hill',
                email='hank@stricklandpropane.com',
                is_superuser=True
            ),
            User(
                username='User2',
                first_name='Dale',
                last_name='Gribble',
                email='dale@dalesdeadbug.com'
            ),
            User(
                username='User3',
                first_name='Bill',
                last_name='Dauterive',
                email='bill.dauterive@army.mil'
            ),
            User(
                username='User4',
                first_name='Jeff',
                last_name='Boomhauer',
                email='boomhauer@dangolemail.com'
            ),
            User(
                username='User5',
                first_name='Debbie',
                last_name='Grund',
                is_active=False
            )
        )
        User.objects.bulk_create(users)

        users[0].groups.set([groups[0]])
        users[1].groups.set([groups[1]])
        users[2].groups.set([groups[2]])

        object_permissions = (
            ObjectPermission(name='Permission 1', actions=['add']),
            ObjectPermission(name='Permission 2', actions=['change']),
            ObjectPermission(name='Permission 3', actions=['delete']),
        )
        ObjectPermission.objects.bulk_create(object_permissions)
        object_permissions[0].users.add(users[0])
        object_permissions[1].users.add(users[1])
        object_permissions[2].users.add(users[2])

    def test_q(self):
        params = {'q': 'user1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_username(self):
        params = {'username': ['User1', 'User2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_first_name(self):
        params = {'first_name': ['Hank', 'Dale']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_last_name(self):
        params = {'last_name': ['Hill', 'Gribble']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_email(self):
        params = {'email': ['hank@stricklandpropane.com', 'dale@dalesdeadbug.com']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_is_active(self):
        params = {'is_active': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_is_superuser(self):
        params = {'is_superuser': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_group(self):
        groups = Group.objects.all()[:2]
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [groups[0].name, groups[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_permission(self):
        object_permissions = ObjectPermission.objects.all()[:2]
        params = {'permission_id': [object_permissions[0].pk, object_permissions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class GroupTestCase(TestCase, BaseFilterSetTests):
    queryset = Group.objects.all()
    filterset = filtersets.GroupFilterSet
    ignore_fields = ('permissions',)

    @classmethod
    def setUpTestData(cls):

        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

        users = (
            User(username='User 1'),
            User(username='User 2'),
            User(username='User 3'),
        )
        User.objects.bulk_create(users)
        users[0].groups.set([groups[0]])
        users[1].groups.set([groups[1]])
        users[2].groups.set([groups[2]])

        object_permissions = (
            ObjectPermission(name='Permission 1', actions=['add']),
            ObjectPermission(name='Permission 2', actions=['change']),
            ObjectPermission(name='Permission 3', actions=['delete']),
        )
        ObjectPermission.objects.bulk_create(object_permissions)
        object_permissions[0].groups.add(groups[0])
        object_permissions[1].groups.add(groups[1])
        object_permissions[2].groups.add(groups[2])

    def test_q(self):
        params = {'q': 'group 1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Group 1', 'Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_user(self):
        users = User.objects.all()[:2]
        params = {'user_id': [users[0].pk, users[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_permission(self):
        object_permissions = ObjectPermission.objects.all()[:2]
        params = {'permission_id': [object_permissions[0].pk, object_permissions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ObjectPermissionTestCase(TestCase, BaseFilterSetTests):
    queryset = ObjectPermission.objects.all()
    filterset = filtersets.ObjectPermissionFilterSet
    ignore_fields = ('actions', 'constraints')

    @classmethod
    def setUpTestData(cls):

        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

        users = (
            User(username='User1'),
            User(username='User2'),
            User(username='User3'),
        )
        User.objects.bulk_create(users)

        object_types = (
            ObjectType.objects.get(app_label='dcim', model='site'),
            ObjectType.objects.get(app_label='dcim', model='rack'),
            ObjectType.objects.get(app_label='dcim', model='device'),
        )

        permissions = (
            ObjectPermission(name='Permission 1', actions=['view', 'add', 'change', 'delete'], description='foobar1'),
            ObjectPermission(name='Permission 2', actions=['view', 'add', 'change', 'delete'], description='foobar2'),
            ObjectPermission(name='Permission 3', actions=['view', 'add', 'change', 'delete']),
            ObjectPermission(name='Permission 4', actions=['view'], enabled=False),
            ObjectPermission(name='Permission 5', actions=['add'], enabled=False),
            ObjectPermission(name='Permission 6', actions=['change'], enabled=False),
            ObjectPermission(name='Permission 7', actions=['delete'], enabled=False),
        )
        ObjectPermission.objects.bulk_create(permissions)
        for i in range(0, 3):
            permissions[i].groups.set([groups[i]])
            permissions[i].users.set([users[i]])
            permissions[i].object_types.set([object_types[i]])

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Permission 1', 'Permission 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_enabled(self):
        params = {'enabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_group(self):
        groups = Group.objects.filter(name__in=['Group 1', 'Group 2'])
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [groups[0].name, groups[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_user(self):
        users = User.objects.filter(username__in=['User1', 'User2'])
        params = {'user_id': [users[0].pk, users[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'user': [users[0].username, users[1].username]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_object_types(self):
        object_types = ObjectType.objects.filter(model__in=['site', 'rack'])
        params = {'object_types': [object_types[0].pk, object_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_can_view(self):
        params = {'can_view': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_can_add(self):
        params = {'can_add': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_can_change(self):
        params = {'can_change': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_can_delete(self):
        params = {'can_delete': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class TokenTestCase(TestCase, BaseFilterSetTests):
    queryset = Token.objects.all()
    filterset = filtersets.TokenFilterSet
    ignore_fields = ('plaintext', 'hmac_digest', 'allowed_ips')

    @classmethod
    def setUpTestData(cls):

        users = (
            User(username='User1'),
            User(username='User2'),
            User(username='User3'),
        )
        User.objects.bulk_create(users)

        future_date = make_aware(datetime.datetime(3000, 1, 1))
        past_date = make_aware(datetime.datetime(2000, 1, 1))
        tokens = (
            Token(
                version=1,
                user=users[0],
                expires=future_date,
                enabled=True,
                write_enabled=True,
                description='foobar1',
            ),
            Token(
                version=2,
                user=users[1],
                expires=future_date,
                enabled=False,
                write_enabled=True,
                description='foobar2',
            ),
            Token(
                version=2,
                user=users[2],
                enabled=True,
                expires=past_date,
                write_enabled=False,
            ),
        )
        for token in tokens:
            token.save()

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_version(self):
        params = {'version': 1}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {'version': 2}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_key(self):
        tokens = Token.objects.filter(version=2)
        params = {'key': [tokens[0].key, tokens[1].key]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_pepper_id(self):
        params = {'pepper_id': [1]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_user(self):
        users = User.objects.order_by('id')[:2]
        params = {'user_id': [users[0].pk, users[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'user': [users[0].username, users[1].username]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_expires(self):
        params = {'expires': '3000-01-01T00:00:00'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'expires__gte': '2021-01-01T00:00:00'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'expires__lte': '2021-01-01T00:00:00'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_enabled(self):
        params = {'enabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'enabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_write_enabled(self):
        params = {'write_enabled': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'write_enabled': False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class OwnerGroupTestCase(TestCase, BaseFilterSetTests):
    queryset = OwnerGroup.objects.all()
    filterset = filtersets.OwnerGroupFilterSet

    @classmethod
    def setUpTestData(cls):

        owner_groups = (
            OwnerGroup(name='Owner Group 1', description='Foo'),
            OwnerGroup(name='Owner Group 2', description='Bar'),
            OwnerGroup(name='Owner Group 3', description='Baz'),
        )
        OwnerGroup.objects.bulk_create(owner_groups)

    def test_q(self):
        params = {'q': 'foo'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Owner Group 1', 'Owner Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['Foo', 'Bar']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class OwnerTestCase(TestCase, BaseFilterSetTests):
    queryset = Owner.objects.all()
    filterset = filtersets.OwnerFilterSet

    @classmethod
    def setUpTestData(cls):
        owner_groups = (
            OwnerGroup(name='Owner Group 1'),
            OwnerGroup(name='Owner Group 2'),
            OwnerGroup(name='Owner Group 3'),
        )
        OwnerGroup.objects.bulk_create(owner_groups)

        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

        users = (
            User(username='User 1'),
            User(username='User 2'),
            User(username='User 3'),
        )
        User.objects.bulk_create(users)

        owners = (
            Owner(name='Owner 1', group=owner_groups[0], description='Foo'),
            Owner(name='Owner 2', group=owner_groups[1], description='Bar'),
            Owner(name='Owner 3', group=owner_groups[2], description='Baz'),
        )
        Owner.objects.bulk_create(owners)

        # Assign users and groups to owners
        owners[0].user_groups.add(groups[0])
        owners[1].user_groups.add(groups[1])
        owners[2].user_groups.add(groups[2])
        owners[0].users.add(users[0])
        owners[1].users.add(users[1])
        owners[2].users.add(users[2])

    def test_q(self):
        params = {'q': 'foo'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Owner 1', 'Owner 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['Foo', 'Bar']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_group(self):
        owner_groups = OwnerGroup.objects.order_by('id')[:2]
        params = {'group_id': [owner_groups[0].pk, owner_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [owner_groups[0].name, owner_groups[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_user_group(self):
        group = Group.objects.order_by('id')[:2]
        params = {'user_group_id': [group[0].pk, group[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'user_group': [group[0].name, group[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_user(self):
        users = User.objects.order_by('id')[:2]
        params = {'user_id': [users[0].pk, users[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'user': [users[0].username, users[1].username]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
