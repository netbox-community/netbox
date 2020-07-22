from django.contrib.auth.models import Group, User
from django.test import TestCase

from users.filters import GroupFilterSet, UserFilterSet


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
