from __future__ import unicode_literals

import base64

from django.urls import reverse
from rest_framework import status

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from secrets.models import Secret, SecretRole, SessionKey, UserKey
from utilities.testing import APITestCase

# Dummy RSA key pair for testing use only
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA97wPWxpq5cClRu8Ssq609ZLfyx6E8ln/v/PdFZ7fxxmA4k+z
1Q/Rn9/897PWy+1x2ZKlHjmaw1z7dS3PlGqdd453d1eY95xYVbFrIHs7yJy8lcDR
2criwGEI68VP1FwcOkkwhicjtQZQS5fkkBIbRjA2wmt2PVT26YbOX2qCMItV1+me
o/Ogh+uI1oNePJ8VYuGXbGNggf1qMY8fGhhhGY2b4PKuSTcsYjbg8adOGzFL9RXL
I1X4PHNCzD/Y1vdM3jJXv+luk3TU+JIbzJeN5ZEEz+sIdlMPCAACaZAY/t9Kd/Lx
Hr0o4K/6gqkZIukxFCK6sN53gibAXfaKc4xlqQIDAQABAoIBAQC4pDQVxNTTtQf6
nImlH83EEto1++M+9pFFsi6fxLApJvsGsjzomke1Dy7uN93qVGk8rq3enzSYU58f
sSs8BVKkH00vZ9ydAKxeAkREC1V9qkRsoTBHUY47sJcDkyZyssxfLNm7w0Q70h7a
mLVEJBqr75eAxLN19vOpDk6Wkz3Bi0Dj27HLeme3hH5jLVQIIswWZnUDP3r/sdM/
WA2GjoycPbug0r1FVZnxkFCrQ5yMfH3VzKBelj7356+5sc/TUXedDFN/DV2b90Ll
+au7EEXecFYZwmX3SX2hpe6IWEpUW3B0fvm+Ipm8h7x68i7J0oi9EUXW2+UQYfOx
dDLxTLvhAoGBAPtJJox4XcpzipSAzKxyV8K9ikUZCG2wJU7VHyZ5zpSXwl/husls
brAzHQcnWayhxxuWeiQ6pLnRFPFXjlOH2FZqHXSLnfpDaymEksDPvo9GqRE3Q+F+
lDRn72H1NLIj3Y3t5SwWRB34Dhy+gd5Ht9L3dCTH8cYvJGnmS4sH/z0NAoGBAPxh
2rhS1B0S9mqqvpduUPxqUIWaztXaHC6ZikloOFcgVMdh9MRrpa2sa+bqcygyqrbH
GZIIeGcWpmzeitWgSUNLMSIpdl/VoBSvZUMggdJyOHXayo/EhfFddGHdkfz0B0GW
LzH8ow4JcYdhkTl4+xQstXJNVRJyw5ezFy35FHwNAoGAGZzjKP470R7lyS03r3wY
Jelb5p8elM+XfemLO0i/HbY6QbuoZk9/GMac9tWz9jynJtC3smmn0KjXEaJzB2CZ
VHWMewygFZo5mgnBS5XhPoldQjv310wnnw/Y/osXy/CL7KOK8Gt0lflqttNUOWvl
+MLwO6+FnUXA2Gp42Lr/8SECgYANf2pEK2HewDHfmIwi6yp3pXPzAUmIlGanc1y6
+lDxD/CYzTta+erdc/g9XFKWVsdciR9r+Pn/gW2bKve/3xer+qyBCDilfXZXRN4k
jeuDhspQO0hUEg2b0AS2azQwlBiDQHX7tWg/CvBAbk5nBXpgJNf7aflfyDV/untF
4SlgTQKBgGmcyU02lyM6ogGbzWqSsHgR1ZhYyTV9DekQx9GysLG1wT2QzgjxOw4K
5PnVkOXr/ORqt+vJsYrtqBZQihmPPREKEwr2n8BRw0364z02wjvP04hDBHp4S5Ej
PQeC5qErboVGMMpM2SamqGEfr+HJ/uRF6mEmm+xjI57aOvAwPW0B
-----END RSA PRIVATE KEY-----"""

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA97wPWxpq5cClRu8Ssq60
9ZLfyx6E8ln/v/PdFZ7fxxmA4k+z1Q/Rn9/897PWy+1x2ZKlHjmaw1z7dS3PlGqd
d453d1eY95xYVbFrIHs7yJy8lcDR2criwGEI68VP1FwcOkkwhicjtQZQS5fkkBIb
RjA2wmt2PVT26YbOX2qCMItV1+meo/Ogh+uI1oNePJ8VYuGXbGNggf1qMY8fGhhh
GY2b4PKuSTcsYjbg8adOGzFL9RXLI1X4PHNCzD/Y1vdM3jJXv+luk3TU+JIbzJeN
5ZEEz+sIdlMPCAACaZAY/t9Kd/LxHr0o4K/6gqkZIukxFCK6sN53gibAXfaKc4xl
qQIDAQAB
-----END PUBLIC KEY-----"""


class SecretRoleTest(APITestCase):

    def setUp(self):

        super(SecretRoleTest, self).setUp()

        self.secretrole1 = SecretRole.objects.create(name='Test Secret Role 1', slug='test-secret-role-1')
        self.secretrole2 = SecretRole.objects.create(name='Test Secret Role 2', slug='test-secret-role-2')
        self.secretrole3 = SecretRole.objects.create(name='Test Secret Role 3', slug='test-secret-role-3')

    def test_get_secretrole(self):

        url = reverse('secrets-api:secretrole-detail', kwargs={'pk': self.secretrole1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['name'], self.secretrole1.name)

    def test_list_secretroles(self):

        url = reverse('secrets-api:secretrole-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_list_secretroles_brief(self):

        url = reverse('secrets-api:secretrole-list')
        response = self.client.get('{}?brief=1'.format(url), **self.header)

        self.assertEqual(
            sorted(response.data['results'][0]),
            ['id', 'name', 'slug', 'url']
        )

    def test_create_secretrole(self):

        data = {
            'name': 'Test Secret Role 4',
            'slug': 'test-secret-role-4',
        }

        url = reverse('secrets-api:secretrole-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(SecretRole.objects.count(), 4)
        secretrole4 = SecretRole.objects.get(pk=response.data['id'])
        self.assertEqual(secretrole4.name, data['name'])
        self.assertEqual(secretrole4.slug, data['slug'])

    def test_create_secretrole_bulk(self):

        data = [
            {
                'name': 'Test Secret Role 4',
                'slug': 'test-secret-role-4',
            },
            {
                'name': 'Test Secret Role 5',
                'slug': 'test-secret-role-5',
            },
            {
                'name': 'Test Secret Role 6',
                'slug': 'test-secret-role-6',
            },
        ]

        url = reverse('secrets-api:secretrole-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(SecretRole.objects.count(), 6)
        self.assertEqual(response.data[0]['name'], data[0]['name'])
        self.assertEqual(response.data[1]['name'], data[1]['name'])
        self.assertEqual(response.data[2]['name'], data[2]['name'])

    def test_update_secretrole(self):

        data = {
            'name': 'Test SecretRole X',
            'slug': 'test-secretrole-x',
        }

        url = reverse('secrets-api:secretrole-detail', kwargs={'pk': self.secretrole1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(SecretRole.objects.count(), 3)
        secretrole1 = SecretRole.objects.get(pk=response.data['id'])
        self.assertEqual(secretrole1.name, data['name'])
        self.assertEqual(secretrole1.slug, data['slug'])

    def test_delete_secretrole(self):

        url = reverse('secrets-api:secretrole-detail', kwargs={'pk': self.secretrole1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(SecretRole.objects.count(), 2)


class SecretTest(APITestCase):

    def setUp(self):

        super(SecretTest, self).setUp()

        userkey = UserKey(user=self.user, public_key=PUBLIC_KEY)
        userkey.save()
        self.master_key = userkey.get_master_key(PRIVATE_KEY)
        session_key = SessionKey(userkey=userkey)
        session_key.save(self.master_key)

        self.header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key),
            'HTTP_X_SESSION_KEY': base64.b64encode(session_key.key),
        }

        self.plaintext = {
            'secret1': 'Secret #1 Plaintext',
            'secret2': 'Secret #2 Plaintext',
            'secret3': 'Secret #3 Plaintext',
        }

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        manufacturer = Manufacturer.objects.create(name='Test Manufacturer 1', slug='test-manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Test Device Type 1')
        devicerole = DeviceRole.objects.create(name='Test Device Role 1', slug='test-device-role-1')
        self.device = Device.objects.create(
            name='Test Device 1', site=site, device_type=devicetype, device_role=devicerole
        )
        self.secretrole1 = SecretRole.objects.create(name='Test Secret Role 1', slug='test-secret-role-1')
        self.secretrole2 = SecretRole.objects.create(name='Test Secret Role 2', slug='test-secret-role-2')
        self.secret1 = Secret(
            device=self.device, role=self.secretrole1, name='Test Secret 1', plaintext=self.plaintext['secret1']
        )
        self.secret1.encrypt(self.master_key)
        self.secret1.save()
        self.secret2 = Secret(
            device=self.device, role=self.secretrole1, name='Test Secret 2', plaintext=self.plaintext['secret2']
        )
        self.secret2.encrypt(self.master_key)
        self.secret2.save()
        self.secret3 = Secret(
            device=self.device, role=self.secretrole1, name='Test Secret 3', plaintext=self.plaintext['secret3']
        )
        self.secret3.encrypt(self.master_key)
        self.secret3.save()

    def test_get_secret(self):

        url = reverse('secrets-api:secret-detail', kwargs={'pk': self.secret1.pk})
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['plaintext'], self.plaintext['secret1'])

    def test_list_secrets(self):

        url = reverse('secrets-api:secret-list')
        response = self.client.get(url, **self.header)

        self.assertEqual(response.data['count'], 3)

    def test_create_secret(self):

        data = {
            'device': self.device.pk,
            'role': self.secretrole1.pk,
            'name': 'Test Secret 4',
            'plaintext': 'Secret #4 Plaintext',
        }

        url = reverse('secrets-api:secret-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['plaintext'], data['plaintext'])
        self.assertEqual(Secret.objects.count(), 4)
        secret4 = Secret.objects.get(pk=response.data['id'])
        secret4.decrypt(self.master_key)
        self.assertEqual(secret4.role_id, data['role'])
        self.assertEqual(secret4.plaintext, data['plaintext'])

    def test_create_secret_bulk(self):

        data = [
            {
                'device': self.device.pk,
                'role': self.secretrole1.pk,
                'name': 'Test Secret 4',
                'plaintext': 'Secret #4 Plaintext',
            },
            {
                'device': self.device.pk,
                'role': self.secretrole1.pk,
                'name': 'Test Secret 5',
                'plaintext': 'Secret #5 Plaintext',
            },
            {
                'device': self.device.pk,
                'role': self.secretrole1.pk,
                'name': 'Test Secret 6',
                'plaintext': 'Secret #6 Plaintext',
            },
        ]

        url = reverse('secrets-api:secret-list')
        response = self.client.post(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(Secret.objects.count(), 6)
        self.assertEqual(response.data[0]['plaintext'], data[0]['plaintext'])
        self.assertEqual(response.data[1]['plaintext'], data[1]['plaintext'])
        self.assertEqual(response.data[2]['plaintext'], data[2]['plaintext'])

    def test_update_secret(self):

        data = {
            'device': self.device.pk,
            'role': self.secretrole2.pk,
            'plaintext': 'NewPlaintext',
        }

        url = reverse('secrets-api:secret-detail', kwargs={'pk': self.secret1.pk})
        response = self.client.put(url, data, format='json', **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['plaintext'], data['plaintext'])
        self.assertEqual(Secret.objects.count(), 3)
        secret1 = Secret.objects.get(pk=response.data['id'])
        secret1.decrypt(self.master_key)
        self.assertEqual(secret1.role_id, data['role'])
        self.assertEqual(secret1.plaintext, data['plaintext'])

    def test_delete_secret(self):

        url = reverse('secrets-api:secret-detail', kwargs={'pk': self.secret1.pk})
        response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Secret.objects.count(), 2)


class GetSessionKeyTest(APITestCase):

    def setUp(self):

        super(GetSessionKeyTest, self).setUp()

        userkey = UserKey(user=self.user, public_key=PUBLIC_KEY)
        userkey.save()
        master_key = userkey.get_master_key(PRIVATE_KEY)
        self.session_key = SessionKey(userkey=userkey)
        self.session_key.save(master_key)

        self.header = {
            'HTTP_AUTHORIZATION': 'Token {}'.format(self.token.key),
        }

    def test_get_session_key(self):

        encoded_session_key = base64.b64encode(self.session_key.key).decode()

        url = reverse('secrets-api:get-session-key-list')
        data = {
            'private_key': PRIVATE_KEY,
        }
        response = self.client.post(url, data, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('session_key'))
        self.assertNotEqual(response.data.get('session_key'), encoded_session_key)

    def test_get_session_key_preserved(self):

        encoded_session_key = base64.b64encode(self.session_key.key).decode()

        url = reverse('secrets-api:get-session-key-list') + '?preserve_key=True'
        data = {
            'private_key': PRIVATE_KEY,
        }
        response = self.client.post(url, data, **self.header)

        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data.get('session_key'), encoded_session_key)
