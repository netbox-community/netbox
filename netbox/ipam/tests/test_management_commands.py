from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from netaddr import IPNetwork

from ipam.models import Prefix


class RebuildPrefixesTestCase(TestCase):
    def test_rebuilds_global_prefix_tree(self):
        out = StringIO()

        with (
            patch('ipam.management.commands.rebuild_prefixes.Prefix') as prefix_model,
            patch('ipam.management.commands.rebuild_prefixes.VRF') as vrf_model,
            patch('ipam.management.commands.rebuild_prefixes.rebuild_prefixes') as rebuild_prefixes,
            patch('ipam.management.commands.rebuild_prefixes.chunked_update') as chunked_update,
        ):
            prefix_model.objects.count.return_value = 0
            prefix_model.objects.filter.return_value.count.return_value = 0
            vrf_model.objects.all.return_value = []
            call_command('rebuild_prefixes', stdout=out)

        rebuild_prefixes.assert_called_once_with(None)
        chunked_update.assert_called_once_with(prefix_model.objects.all.return_value, _depth=0, _children=0)
        self.assertIn('Rebuilding 0 prefixes', out.getvalue())
        self.assertIn('Finished.', out.getvalue())

    def test_hierarchy_is_correct_after_rebuild(self):
        Prefix.objects.bulk_create(
            [
                Prefix(prefix=IPNetwork('10.0.0.0/8')),
                Prefix(prefix=IPNetwork('10.0.0.0/16')),
                Prefix(prefix=IPNetwork('10.0.0.0/24')),
            ]
        )

        out = StringIO()
        call_command('rebuild_prefixes', stdout=out)

        self.assertIn('Finished.', out.getvalue())
        self.assertEqual(Prefix.objects.get(prefix=IPNetwork('10.0.0.0/8'))._depth, 0)
        self.assertEqual(Prefix.objects.get(prefix=IPNetwork('10.0.0.0/8'))._children, 2)
        self.assertEqual(Prefix.objects.get(prefix=IPNetwork('10.0.0.0/16'))._depth, 1)
        self.assertEqual(Prefix.objects.get(prefix=IPNetwork('10.0.0.0/16'))._children, 1)
        self.assertEqual(Prefix.objects.get(prefix=IPNetwork('10.0.0.0/24'))._depth, 2)
        self.assertEqual(Prefix.objects.get(prefix=IPNetwork('10.0.0.0/24'))._children, 0)

    def test_rebuilds_prefix_tree_for_each_vrf(self):
        class FakeVRF:
            pk = 123

            def __str__(self):
                return 'Tenant VRF'

        class FakeQuerySet:
            def __init__(self, count):
                self._count = count

            def count(self):
                return self._count

        out = StringIO()
        vrf = FakeVRF()

        with (
            patch('ipam.management.commands.rebuild_prefixes.Prefix') as prefix_model,
            patch('ipam.management.commands.rebuild_prefixes.VRF') as vrf_model,
            patch('ipam.management.commands.rebuild_prefixes.rebuild_prefixes') as rebuild_prefixes,
            patch('ipam.management.commands.rebuild_prefixes.chunked_update'),
        ):
            prefix_model.objects.count.return_value = 3
            prefix_model.objects.filter.side_effect = [
                FakeQuerySet(1),
                FakeQuerySet(2),
            ]
            vrf_model.objects.all.return_value = [vrf]

            call_command('rebuild_prefixes', stdout=out)

        rebuild_prefixes.assert_any_call(None)
        rebuild_prefixes.assert_any_call(vrf.pk)
        self.assertIn('Global: 1 prefixes', out.getvalue())
        self.assertIn('VRF Tenant VRF: 2 prefixes', out.getvalue())
