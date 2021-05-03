from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from users.filtersets import GroupFilterSet, ObjectPermissionFilterSet, UserFilterSet
from users.models import ObjectPermission


class UserTestCase(TestCase):
    queryset = User.objects.all()
    filterset = UserFilterSet

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
                is_staff=True
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

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

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

    def test_is_staff(self):
        params = {'is_staff': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_is_active(self):
        params = {'is_active': True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_group(self):
        groups = Group.objects.all()[:2]
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'group': [groups[0].name, groups[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class GroupTestCase(TestCase):
    queryset = Group.objects.all()
    filterset = GroupFilterSet

    @classmethod
    def setUpTestData(cls):

        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Group 1', 'Group 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ObjectPermissionTestCase(TestCase):
    queryset = ObjectPermission.objects.all()
    filterset = ObjectPermissionFilterSet

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
            ContentType.objects.get(app_label='dcim', model='site'),
            ContentType.objects.get(app_label='dcim', model='rack'),
            ContentType.objects.get(app_label='dcim', model='device'),
        )

        permissions = (
            ObjectPermission(name='Permission 1', actions=['view', 'add', 'change', 'delete']),
            ObjectPermission(name='Permission 2', actions=['view', 'add', 'change', 'delete']),
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

    def test_id(self):
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

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
        object_types = ContentType.objects.filter(model__in=['site', 'rack'])
        params = {'object_types': [object_types[0].pk, object_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
