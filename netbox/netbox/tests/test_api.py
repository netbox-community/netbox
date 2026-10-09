import hashlib
import uuid
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import NON_FIELD_ERRORS
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.test import RequestFactory, TestCase, TransactionTestCase, override_settings, tag
from django.urls import reverse
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.settings import api_settings
from rest_framework.test import APIClient

from core.models import DataFile, DataSource, ObjectType
from dcim.api.serializers import RackSerializer
from dcim.models import Device, Site
from extras.models import ExportTemplate
from ipam.api.serializers import RouteTargetSerializer, VRFSerializer
from ipam.models import VRF, RouteTarget
from netbox.api.exceptions import QuerySetNotOrdered, SerializerNotFound
from netbox.api.fields import ContentTypeField, IntegerRangeSerializer, RelatedObjectCountField
from netbox.api.pagination import NetBoxPagination
from netbox.api.serializers import ValidatedModelSerializer
from users.constants import TOKEN_PREFIX
from users.models import Token, User
from utilities.api import get_serializer_for_model
from utilities.testing import APITestCase, create_test_device
from vpn.api.serializers import L2VPNSerializer


class AppTestCase(APITestCase):

    def test_http_headers(self):
        response = self.client.get(reverse('api-root'), **self.header)

        # Check that all custom response headers are present and valid
        self.assertEqual(response.status_code, 200)
        request_id = response.headers['X-Request-ID']
        uuid.UUID(request_id)

    def test_root(self):
        url = reverse('api-root')
        response = self.client.get(f'{url}?format=api', **self.header)

        self.assertEqual(response.status_code, 200)

    def test_status(self):
        url = reverse('api-status')
        response = self.client.get(f'{url}?format=api', **self.header)

        self.assertEqual(response.status_code, 200)

    def test_authentication_check(self):
        url = reverse('api-authentication-check')

        # Test an unauthenticated request
        response = self.client.get(f'{url}')
        self.assertEqual(response.status_code, 403)

        # Test an authenticated request
        response = self.client.get(f'{url}', **self.header)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.user.pk)


class NonFieldErrorKeyTestCase(APITestCase):
    """
    REST framework's key for errors which pertain to no particular field is configured to match
    Django's, so that the API reports such an error under `__all__` regardless of which layer
    rejected the request (see REST_FRAMEWORK['NON_FIELD_ERRORS_KEY'] in settings). Model validation
    errors are keyed by Django, having reached the response by way of full_clean(); errors raised by
    a serializer or field are keyed by REST framework.
    """
    def setUp(self):
        super().setUp()
        self.add_permissions('dcim.add_site', 'dcim.view_site', 'dcim.change_site')
        self.url = reverse('dcim-api:site-list')

    def test_setting_matches_django(self):
        self.assertEqual(api_settings.NON_FIELD_ERRORS_KEY, NON_FIELD_ERRORS)

    def test_serializer_error_uses_all_key(self):
        """An error from REST framework's own machinery (here, a non-dictionary item)."""
        response = self.client.post(self.url, ['not an object'], format='json', **self.header)

        self.assertEqual(response.status_code, 400)
        self.assertIn(NON_FIELD_ERRORS, response.data['errors'][0]['errors'])

    def test_model_validation_error_uses_all_key(self):
        """An error from Django's full_clean(), which uses this key of its own accord."""
        site = Site.objects.create(name='Site 1', slug='site-1')
        # A Location's name must be unique within its Site, enforced by a model constraint
        location_url = reverse('dcim-api:location-list')
        self.add_permissions('dcim.add_location', 'dcim.view_location')
        data = {'name': 'Location 1', 'slug': 'location-1', 'site': site.pk}
        self.assertEqual(self.client.post(location_url, data, format='json', **self.header).status_code, 201)

        response = self.client.post(location_url, data, format='json', **self.header)

        self.assertEqual(response.status_code, 400)
        self.assertIn(NON_FIELD_ERRORS, response.data)


class RelatedObjectCountFieldTestCase(TestCase):
    """
    RelatedObjectCountFields are populated by annotations applied to a viewset's queryset, which are only
    added when serializing an object via its own endpoint (including ?brief=1). They are never annotated when
    the object is rendered as a nested related object, so they must be omitted from nested representations to
    keep the generated OpenAPI schema honest. See #22154.
    """
    def test_count_field_omitted_when_nested(self):
        """A nested serializer must drop RelatedObjectCountFields (e.g. RackSerializer.device_count)."""
        serializer = RackSerializer(nested=True)
        count_fields = [
            name for name, field in serializer.fields.items() if isinstance(field, RelatedObjectCountField)
        ]
        self.assertEqual(count_fields, [])
        self.assertNotIn('device_count', serializer.fields)

    def test_count_field_retained_in_brief_mode(self):
        """?brief=1 (fields=brief_fields, not nested) must retain RelatedObjectCountFields."""
        serializer = RackSerializer(fields=RackSerializer.Meta.brief_fields)
        self.assertIn('device_count', serializer.fields)
        self.assertIsInstance(serializer.fields['device_count'], RelatedObjectCountField)


class NetBoxPaginationTestCase(TestCase):

    def setUp(self):
        self.paginator = NetBoxPagination()
        self.factory = RequestFactory()

    def _make_drf_request(self, path='/', query_params=None):
        """Helper to create a proper DRF Request object"""
        return Request(self.factory.get(path, query_params or {}))

    def test_raises_exception_for_unordered_queryset(self):
        """Should raise QuerySetNotOrdered for unordered QuerySet"""
        queryset = Token.objects.all().order_by()
        request = self._make_drf_request()

        with self.assertRaises(QuerySetNotOrdered) as cm:
            self.paginator.paginate_queryset(queryset, request)

        error_msg = str(cm.exception)
        self.assertIn("Paginating over an unordered queryset is unreliable", error_msg)
        self.assertIn("Ensure that a minimal ordering has been applied", error_msg)

    def test_allows_ordered_queryset(self):
        """Should not raise exception for ordered QuerySet"""
        queryset = Token.objects.all().order_by('created')
        request = self._make_drf_request()

        self.paginator.paginate_queryset(queryset, request)  # Should not raise exception

    def test_allows_non_queryset_iterables(self):
        """Should not raise exception for non-QuerySet iterables"""
        iterable = [1, 2, 3, 4, 5]
        request = self._make_drf_request()

        self.paginator.paginate_queryset(iterable, request)  # Should not raise exception

    def test_get_start_returns_none_when_absent(self):
        """get_start() returns None when start param is not in the request"""
        request = self._make_drf_request()
        self.assertIsNone(self.paginator.get_start(request))

    def test_get_start_returns_integer(self):
        """get_start() returns an integer when start param is present"""
        request = self._make_drf_request(query_params={'start': '42'})
        self.assertEqual(self.paginator.get_start(request), 42)

    def test_get_start_raises_for_negative(self):
        """get_start() raises ValidationError for negative values"""
        request = self._make_drf_request(query_params={'start': '-1'})
        with self.assertRaises(ValidationError):
            self.paginator.get_start(request)

    def test_cursor_and_offset_conflict_raises_validation_error(self):
        """paginate_queryset() raises ValidationError when both start and offset are specified"""
        queryset = Token.objects.all().order_by('created')
        request = self._make_drf_request(query_params={'start': '1', 'offset': '10'})
        with self.assertRaises(ValidationError):
            self.paginator.paginate_queryset(queryset, request)

    def test_cursor_and_ordering_conflict_raises_validation_error(self):
        """paginate_queryset() raises ValidationError when both start and ordering are specified"""
        queryset = Token.objects.all().order_by('created')
        request = self._make_drf_request(query_params={'start': '1', 'ordering': 'created'})
        with self.assertRaises(ValidationError):
            self.paginator.paginate_queryset(queryset, request)


class IntegerRangeSerializerTestCase(TestCase):

    def test_to_representation_emits_inclusive_bounds_for_non_canonical_range(self):
        """A NumericRange with bounds='[]' must serialize to its inclusive (lower, upper) pair."""
        serializer = IntegerRangeSerializer()
        self.assertEqual(
            serializer.to_representation(NumericRange(100, 199, bounds='[]')),
            (100, 199)
        )
        self.assertEqual(
            serializer.to_representation(NumericRange(100, 200, bounds='[)')),
            (100, 199)
        )

    def test_to_internal_value_produces_canonical_half_open_range(self):
        """An inclusive [lo, hi] pair is normalized to NumericRange(lo, hi+1, '[)')."""
        serializer = IntegerRangeSerializer()
        self.assertEqual(
            serializer.to_internal_value([100, 199]),
            NumericRange(100, 200, bounds='[)')
        )

    def test_to_internal_value_rejects_malformed_input(self):
        """Input must be a two-element list or tuple of ints."""
        serializer = IntegerRangeSerializer()
        with self.assertRaises(ValidationError):
            serializer.to_internal_value('100-200')
        with self.assertRaises(ValidationError):
            serializer.to_internal_value([100])
        with self.assertRaises(ValidationError):
            serializer.to_internal_value([100, 200, 300])

    def test_to_internal_value_rejects_non_integer_bounds(self):
        """Range boundaries must be integers, not strings or floats."""
        serializer = IntegerRangeSerializer()
        with self.assertRaises(ValidationError):
            serializer.to_internal_value(['100', '200'])
        with self.assertRaises(ValidationError):
            serializer.to_internal_value([100.5, 200.5])


class ContentTypeFieldTestCase(TestCase):

    def test_to_internal_value_resolves_content_type_within_queryset(self):
        """A content type present in the field's declared queryset resolves successfully."""
        site_ct = ContentType.objects.get_for_model(Site)
        field = ContentTypeField(queryset=ContentType.objects.filter(pk=site_ct.pk))
        self.assertEqual(field.to_internal_value('dcim.site'), site_ct)

    def test_to_internal_value_rejects_content_type_outside_queryset(self):
        """
        Regression test for #22748: ContentTypeField.to_internal_value() previously resolved
        against the raw, unfiltered ContentType table via get_by_natural_key(), ignoring the
        field's own declared queryset entirely. A content type that is real and resolvable in
        general, but falls outside the specific queryset a given field declares, must be
        rejected rather than silently accepted.
        """
        site_ct = ContentType.objects.get_for_model(Site)
        device_ct = ContentType.objects.get_for_model(Device)

        # Scope the field to a single, unrelated content type so `dcim.site` is guaranteed to
        # fall outside it.
        field = ContentTypeField(queryset=ContentType.objects.filter(pk=device_ct.pk))
        with self.assertRaises(ValidationError):
            field.to_internal_value('dcim.site')

        # Sanity check: the rejected content type is a genuine, generally-resolvable content
        # type, so the rejection above is attributable to queryset scoping and not a bogus value.
        self.assertTrue(ContentType.objects.filter(pk=site_ct.pk).exists())

    def test_to_internal_value_rejects_malformed_input(self):
        """Input must be exactly '<app_label>.<model>'."""
        field = ContentTypeField(queryset=ContentType.objects.all())
        with self.assertRaises(ValidationError):
            field.to_internal_value('not-a-valid-format')
        with self.assertRaises(ValidationError):
            field.to_internal_value('too.many.dots')

    def test_to_internal_value_rejects_nonexistent_content_type(self):
        """A syntactically valid but nonexistent content type must be rejected."""
        field = ContentTypeField(queryset=ContentType.objects.all())
        with self.assertRaises(ValidationError):
            field.to_internal_value('nonexistent_app.nonexistent_model')

    def test_to_internal_value_many_rejects_content_type_outside_queryset(self):
        """
        many=True wraps the field in a ManyRelatedField, which delegates per-item validation to
        the child field's to_internal_value() unconditionally; the same queryset scoping must
        hold there too.
        """
        device_ct = ContentType.objects.get_for_model(Device)
        field = ContentTypeField(queryset=ContentType.objects.filter(pk=device_ct.pk), many=True)

        self.assertEqual(field.to_internal_value(['dcim.device']), [device_ct])
        with self.assertRaises(ValidationError):
            field.to_internal_value(['dcim.device', 'dcim.site'])


class SerializedPKRelatedFieldTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        route_targets = (
            RouteTarget(name='65000:1'),
            RouteTarget(name='65000:2'),
            RouteTarget(name='65000:3'),
        )
        RouteTarget.objects.bulk_create(route_targets)

        vrfs = (
            VRF(name='VRF 1'),
            VRF(name='VRF 2'),
        )
        VRF.objects.bulk_create(vrfs)
        vrfs[0].import_targets.set(route_targets[:2])
        vrfs[1].import_targets.set(route_targets[1:])

    def test_to_representation_reuses_nested_serializer(self):
        """A field builds one nested serializer for all its objects, lazily, in nested and full mode."""
        context = {'request': RequestFactory().get('/')}
        route_targets = RouteTarget.objects.order_by('name')
        for serializer_class, nested in ((L2VPNSerializer, True), (VRFSerializer, False)):
            with self.subTest(serializer=serializer_class.__name__):
                expected = [
                    RouteTargetSerializer(route_target, nested=nested, context=context).data
                    for route_target in route_targets
                ]
                with patch.object(
                    RouteTargetSerializer, '__init__', autospec=True, side_effect=RouteTargetSerializer.__init__
                ) as init:
                    field = serializer_class(context=context).fields['import_targets']
                    self.assertEqual(field.to_representation([]), [])
                    self.assertEqual(init.call_count, 0)
                    self.assertEqual(field.to_representation(route_targets), expected)
                self.assertEqual(init.call_count, 1)

    def test_list_reuses_nested_serializer_per_request(self):
        """Each list request builds its own nested serializer, also through the browsable API."""
        self.add_permissions('ipam.view_vrf')
        url = reverse('ipam-api:vrf-list')

        def get(params, host):
            with patch.object(
                RouteTargetSerializer, '__init__', autospec=True, side_effect=RouteTargetSerializer.__init__
            ) as init:
                response = self.client.get(
                    url, {'fields': 'name,import_targets', **params}, HTTP_HOST=host, **self.header
                )
            self.assertEqual(response.status_code, 200)
            return init.call_count, response.data['results']

        one, _ = get({'name': 'VRF 1'}, 'a.example.com')
        two, vrfs = get({}, 'b.example.com')
        self.assertEqual(one, two)
        self.assertEqual(
            {vrf['name']: [target['name'] for target in vrf['import_targets']] for vrf in vrfs},
            {'VRF 1': ['65000:1', '65000:2'], 'VRF 2': ['65000:2', '65000:3']},
        )
        for vrf in vrfs:
            for target in vrf['import_targets']:
                self.assertTrue(target['url'].startswith('http://b.example.com/'))

        response = self.client.get(url, {'format': 'api'}, **self.header)
        self.assertContains(response, '65000:3')


class ValidatedModelSerializerTestCase(TestCase):

    def test_serializers_declare_model_clean_fields(self):
        """Serializers accepting a data file must declare the fields SyncedDataMixin.clean() normalizes."""
        normalized_fields = {'data_source', 'data_path', 'auto_sync_enabled', 'data_synced'}

        for object_type in ObjectType.objects.with_feature('synced_data'):
            model = object_type.model_class()
            if model is None:
                continue
            try:
                serializer = get_serializer_for_model(model)
            except SerializerNotFound:
                continue
            # Only serializers that let a client bind a data file have normalization to preserve
            data_file = serializer().fields.get('data_file')
            if data_file is None or data_file.read_only:
                continue
            with self.subTest(model=model._meta.label):
                declared = set(getattr(serializer.Meta, 'model_clean_fields', ()))
                self.assertTrue(
                    normalized_fields.issubset(declared),
                    f'{serializer.__name__}.Meta.model_clean_fields is missing '
                    f'{sorted(normalized_fields - declared)}'
                )

    def test_model_clean_fields_is_opt_in(self):
        """A declared field takes its value from the cleaned instance, while an undeclared one keeps the input."""
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='local',
            source_url='file:///tmp/netbox-datasource/',
        )
        file_data = b'{{ synced }}'
        datafile = DataFile.objects.create(
            source=datasource,
            path='exports/devices.j2',
            last_updated=now(),
            size=len(file_data),
            hash=hashlib.sha256(file_data).hexdigest(),
            data=file_data,
        )

        class PlainSerializer(ValidatedModelSerializer):
            class Meta:
                model = ExportTemplate
                fields = ['name', 'template_code', 'data_file']

        class OptedInSerializer(PlainSerializer):
            class Meta(PlainSerializer.Meta):
                model_clean_fields = ('template_code',)

        payload = {
            'name': 'Export Template X',
            'template_code': '{# placeholder #}',
            'data_file': datafile.pk,
        }

        plain = PlainSerializer(data=payload)
        self.assertTrue(plain.is_valid(), plain.errors)
        self.assertEqual(plain.validated_data['template_code'], '{# placeholder #}')

        opted_in = OptedInSerializer(data=payload)
        self.assertTrue(opted_in.is_valid(), opted_in.errors)
        self.assertEqual(opted_in.validated_data['template_code'], '{{ synced }}')

    def test_nested_serializer_skips_model_validation(self):
        """A serializer representing a nested object returns its input untouched."""

        class OptedInSerializer(ValidatedModelSerializer):
            class Meta:
                model = ExportTemplate
                fields = ['name', 'template_code']
                brief_fields = ('name',)
                model_clean_fields = ('template_code',)

        serializer = OptedInSerializer(nested=True)
        data = {'template_code': '{# untouched #}'}

        self.assertEqual(serializer.validate(data), data)


ROUTED_ALIAS = 'routed'


class SiteRouter:
    """
    Route Site queries to a second connection, as a plugin's router may.
    """
    def db_for_read(self, model, **hints):
        return ROUTED_ALIAS if model is Site else None

    db_for_write = db_for_read

    def allow_relation(self, obj1, obj2, **hints):
        return True


@override_settings(DATABASE_ROUTERS=[SiteRouter()])
class BulkOperationRoutingTestCase(TransactionTestCase):
    """
    Exercise the bulk operations on a connection which DATABASE_ROUTERS selects in place of the default one, as
    netbox-branching does for an active branch. Uses TransactionTestCase so that the default connection is not in
    a transaction while the request is served, as is the case outside of tests.

    Note: TransactionTestCase teardown flushes all tables, which removes rows seeded by data migrations from a
    --keepdb database (e.g. the dcim.0206 ModuleTypeProfiles). A fresh test database restores them.
    """
    client_class = APIClient

    def setUp(self):
        # A second connection to the test database, standing in for e.g. a branch schema
        routed = connections[DEFAULT_DB_ALIAS].copy(ROUTED_ALIAS)
        connections[ROUTED_ALIAS] = routed
        self.addCleanup(connections.__delitem__, ROUTED_ALIAS)
        self.addCleanup(routed.close)

        # A superuser, as this case covers transaction handling rather than permission enforcement
        user = User.objects.create_user(username='testuser', is_superuser=True)
        token = Token.objects.create(user=user)
        self.header = {'HTTP_AUTHORIZATION': f'Bearer {TOKEN_PREFIX}{token.key}.{token.token}'}
        self.url = reverse('dcim-api:site-list')

    @tag('regression')  # Ref: #23367
    def test_bulk_create_rollback(self):
        """Roll back a bulk create on the routed connection when one object is invalid."""
        data = [
            {'name': 'Site 1', 'slug': 'site-1'},
            {'name': 'Site 2'},
        ]
        with patch('netbox.context_managers.flush_events') as flush_events:
            response = self.client.post(self.url, data, format='json', **self.header)

        self.assertEqual(response.status_code, 400)
        self.assertEqual([e['index'] for e in response.data['errors']], [1])
        self.assertIn('slug', response.data['errors'][0]['errors'])
        self.assertFalse(Site.objects.exists())
        flush_events.assert_not_called()

    @tag('regression')  # Ref: #23367
    def test_bulk_update_rollback(self):
        """Roll back a bulk update on the routed connection when one object is invalid."""
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)
        data = [
            {'id': sites[0].pk, 'description': 'Updated'},
            {'id': sites[1].pk, 'status': 'invalid'},
        ]
        with patch('netbox.context_managers.flush_events') as flush_events:
            response = self.client.patch(self.url, data, format='json', **self.header)

        self.assertEqual(response.status_code, 400)
        self.assertEqual([e['id'] for e in response.data['errors']], [sites[1].pk])
        self.assertIn('status', response.data['errors'][0]['errors'])
        self.assertEqual(Site.objects.get(pk=sites[0].pk).description, '')
        flush_events.assert_not_called()

    @tag('regression')  # Ref: #23367
    def test_bulk_delete_rollback(self):
        """Roll back a bulk delete on the routed connection when one object is protected."""
        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
        )
        Site.objects.bulk_create(sites)
        # Protect the first Site, as its failed delete clears the event queue before the second is deleted
        create_test_device('Device 1', site=sites[0])
        data = [{'id': site.pk} for site in sites]
        with patch('netbox.context_managers.flush_events') as flush_events:
            response = self.client.delete(self.url, data, format='json', **self.header)

        self.assertEqual(response.status_code, 409)
        self.assertEqual([e['id'] for e in response.data['errors']], [sites[0].pk])
        self.assertEqual(Site.objects.count(), 2)
        flush_events.assert_not_called()
