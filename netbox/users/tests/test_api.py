from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from users.models import ObjectPermission
from utilities.testing import APITestCase


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('users-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class ObjectPermissionTest(APITestCase):

    @classmethod
    def setUpTestData(cls):

        groups = (
            Group(name='Group 1'),
            Group(name='Group 2'),
            Group(name='Group 3'),
        )
        Group.objects.bulk_create(groups)

        users = (
            User(username='User 1', is_active=True),
            User(username='User 2', is_active=True),
            User(username='User 3', is_active=True),
        )
        User.objects.bulk_create(users)

        object_type = ContentType.objects.get(app_label='dcim', model='device')

        for i in range(0, 3):
            objectpermission = ObjectPermission(
                actions=['view', 'add', 'change', 'delete'],
                constraints={'name': f'TEST{i+1}'}
            )
            objectpermission.save()
            objectpermission.object_types.add(object_type)
            objectpermission.groups.add(groups[i])
            objectpermission.users.add(users[i])

    def test_get_objectpermission(self):
        objectpermission = ObjectPermission.objects.first()
        url = reverse('users-api:objectpermission-detail', kwargs={'pk': objectpermission.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['id'], objectpermission.pk)

    def test_list_objectpermissions(self):
        url = reverse('users-api:objectpermission-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], ObjectPermission.objects.count())

    def test_create_objectpermission(self):
        data = {
            'object_types': ['dcim.site'],
            'groups': [Group.objects.first().pk],
            'users': [User.objects.first().pk],
            'actions': ['view', 'add', 'change', 'delete'],
            'constraints': {'name': 'TEST4'},
        }

        url = reverse('users-api:objectpermission-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ObjectPermission.objects.count(), 4)
        objectpermission = ObjectPermission.objects.get(pk=response.data['id'])
        self.assertEqual(objectpermission.groups.first().pk, data['groups'][0])
        self.assertEqual(objectpermission.users.first().pk, data['users'][0])
        self.assertEqual(objectpermission.actions, data['actions'])
        self.assertEqual(objectpermission.constraints, data['constraints'])

    def test_create_objectpermission_bulk(self):
        groups = Group.objects.all()[:3]
        users = User.objects.all()[:3]
        data = [
            {
                'object_types': ['dcim.site'],
                'groups': [groups[0].pk],
                'users': [users[0].pk],
                'actions': ['view', 'add', 'change', 'delete'],
                'constraints': {'name': 'TEST4'},
            },
            {
                'object_types': ['dcim.site'],
                'groups': [groups[1].pk],
                'users': [users[1].pk],
                'actions': ['view', 'add', 'change', 'delete'],
                'constraints': {'name': 'TEST5'},
            },
            {
                'object_types': ['dcim.site'],
                'groups': [groups[2].pk],
                'users': [users[2].pk],
                'actions': ['view', 'add', 'change', 'delete'],
                'constraints': {'name': 'TEST6'},
            },
        ]

        url = reverse('users-api:objectpermission-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(ObjectPermission.objects.count(), 6)

    def test_update_objectpermission(self):
        objectpermission = ObjectPermission.objects.first()
        data = {
            'object_types': ['dcim.site', 'dcim.device'],
            'groups': [g.pk for g in Group.objects.all()[:2]],
            'users': [u.pk for u in User.objects.all()[:2]],
            'actions': ['view'],
            'constraints': {'name': 'TEST'},
        }

        url = reverse('users-api:objectpermission-detail', kwargs={'pk': objectpermission.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(ObjectPermission.objects.count(), 3)
        objectpermission = ObjectPermission.objects.get(pk=response.data['id'])
        self.assertEqual(objectpermission.groups.first().pk, data['groups'][0])
        self.assertEqual(objectpermission.users.first().pk, data['users'][0])
        self.assertEqual(objectpermission.actions, data['actions'])
        self.assertEqual(objectpermission.constraints, data['constraints'])

    def test_delete_objectpermission(self):
        objectpermission = ObjectPermission.objects.first()
        url = reverse('users-api:objectpermission-detail', kwargs={'pk': objectpermission.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ObjectPermission.objects.count(), 2)
