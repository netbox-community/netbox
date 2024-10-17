from core.models import ObjectType
from users.models import *
from utilities.testing import ViewTestCases, create_test_user


class UserTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = User
    maxDiff = None
    validation_excluded_fields = ['password']

    def _get_queryset(self):
        # Omit the user attached to the test client
        return self.model.objects.exclude(username='testuser')

    @classmethod
    def setUpTestData(cls):

        users = (
            User(username='username1', first_name='first1', last_name='last1', email='user1@foo.com', password='pass1xxx'),
            User(username='username2', first_name='first2', last_name='last2', email='user2@foo.com', password='pass2xxx'),
            User(username='username3', first_name='first3', last_name='last3', email='user3@foo.com', password='pass3xxx'),
        )
        User.objects.bulk_create(users)

        cls.form_data = {
            'username': 'usernamex',
            'first_name': 'firstx',
            'last_name': 'lastx',
            'email': 'userx@foo.com',
            'password': 'pass1xxxABCD',
            'confirm_password': 'pass1xxxABCD',
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

    def test_password_validation_enforced(self):
        """
        Test that any configured password validation rules (AUTH_PASSWORD_VALIDATORS) are enforced.
        """
        self.add_permissions('users.add_user')
        data = {
            'username': 'new_user',
            'password': 'F1a',
            'confirm_password': 'F1a',
        }

        # Password too short
        request = {
            'path': self._get_url('add'),
            'data': data,
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)

        # Password long enough
        data['password'] = 'fooBarFoo123'
        data['confirm_password'] = 'fooBarFoo123'
        self.assertHttpStatus(self.client.post(**request), 302)

        # Password no number
        data['password'] = 'FooBarFooBar'
        data['confirm_password'] = 'FooBarFooBar'
        self.assertHttpStatus(self.client.post(**request), 200)

        # Password no letter
        data['password'] = '123456789123'
        data['confirm_password'] = '123456789123'
        self.assertHttpStatus(self.client.post(**request), 200)

        # Password no uppercase
        data['password'] = 'foobar123abc'
        data['confirm_password'] = 'foobar123abc'
        self.assertHttpStatus(self.client.post(**request), 200)

        # Password no lowercase
        data['password'] = 'FOOBAR123ABC'
        data['confirm_password'] = 'FOOBAR123ABC'
        self.assertHttpStatus(self.client.post(**request), 200)


class GroupTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = Group
    maxDiff = None

    @classmethod
    def setUpTestData(cls):

        groups = (
            Group(name='group1'),
            Group(name='group2'),
            Group(name='group3'),
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

        cls.bulk_edit_data = {
            'description': 'New description',
        }


class ObjectPermissionTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = ObjectPermission
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        object_type = ObjectType.objects.get_by_natural_key('dcim', 'site')

        permissions = (
            ObjectPermission(name='Permission 1', actions=['view', 'add', 'delete']),
            ObjectPermission(name='Permission 2', actions=['view', 'add', 'delete']),
            ObjectPermission(name='Permission 3', actions=['view', 'add', 'delete']),
        )
        ObjectPermission.objects.bulk_create(permissions)

        cls.form_data = {
            'name': 'Permission X',
            'description': 'A new permission',
            'object_types': [object_type.pk],
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


class TokenTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.CreateObjectViewTestCase,
    ViewTestCases.EditObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkImportObjectsViewTestCase,
    ViewTestCases.BulkEditObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = Token
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        users = (
            create_test_user('User 1'),
            create_test_user('User 2'),
        )
        tokens = (
            Token(key='123456789012345678901234567890123456789A', user=users[0]),
            Token(key='123456789012345678901234567890123456789B', user=users[0]),
            Token(key='123456789012345678901234567890123456789C', user=users[1]),
        )
        Token.objects.bulk_create(tokens)

        cls.form_data = {
            'user': users[0].pk,
            'key': '1234567890123456789012345678901234567890',
            'description': 'testdescription',
        }

        cls.csv_data = (
            "key,user,description",
            f"123456789012345678901234567890123456789D,{users[0].pk},testdescriptionD",
            f"123456789012345678901234567890123456789E,{users[1].pk},testdescriptionE",
            f"123456789012345678901234567890123456789F,{users[1].pk},testdescriptionF",
        )

        cls.csv_update_data = (
            "id,description",
            f"{tokens[0].pk},testdescriptionH",
            f"{tokens[1].pk},testdescriptionI",
            f"{tokens[2].pk},testdescriptionJ",
        )

        cls.bulk_edit_data = {
            'description': 'newdescription',
        }
