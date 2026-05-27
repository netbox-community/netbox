"""Tests for the ltree-based hierarchical model infrastructure."""
from django.db import connection
from django.test import TestCase

from dcim.models import Region, Site


class LtreeTriggerTests(TestCase):
    """Verify per-row PostgreSQL triggers maintain `path` correctly."""

    def test_insert_root_path(self):
        r = Region.objects.create(name='Root', slug='root')
        self.assertEqual(r.path, str(r.pk))

    def test_insert_child_path(self):
        r = Region.objects.create(name='Root', slug='root')
        c = Region.objects.create(parent=r, name='Child', slug='child')
        self.assertEqual(c.path, f'{r.pk}.{c.pk}')

    def test_grandchild_path(self):
        r = Region.objects.create(name='R', slug='r')
        c = Region.objects.create(parent=r, name='C', slug='c')
        g = Region.objects.create(parent=c, name='G', slug='g')
        self.assertEqual(g.path, f'{r.pk}.{c.pk}.{g.pk}')

    def test_move_cascades_to_descendants(self):
        r = Region.objects.create(name='R', slug='r')
        c = Region.objects.create(parent=r, name='C', slug='c')
        g = Region.objects.create(parent=c, name='G', slug='g')
        c.parent = None
        c.save()
        c.refresh_from_db()
        g.refresh_from_db()
        self.assertEqual(c.path, str(c.pk))
        self.assertEqual(g.path, f'{c.pk}.{g.pk}')

    def test_bulk_create_populates_paths(self):
        """BEFORE INSERT trigger fires on bulk_create, populating path."""
        root = Region.objects.create(name='R', slug='r-bulk')
        children = Region.objects.bulk_create([
            Region(parent=root, name=f'C{i}', slug=f'c{i}-bulk') for i in range(3)
        ])
        for child in children:
            child.refresh_from_db()
            self.assertEqual(child.path, f'{root.pk}.{child.pk}')

    def test_queryset_update_with_parent_id_cascades(self):
        """Raw .update() that changes parent_id still fires triggers."""
        r1 = Region.objects.create(name='R1', slug='r1-up')
        r2 = Region.objects.create(name='R2', slug='r2-up')
        c = Region.objects.create(parent=r1, name='C', slug='c-up')
        g = Region.objects.create(parent=c, name='G', slug='g-up')

        Region.objects.filter(pk=c.pk).update(parent=r2)
        c.refresh_from_db()
        g.refresh_from_db()
        self.assertEqual(c.path, f'{r2.pk}.{c.pk}')
        self.assertEqual(g.path, f'{r2.pk}.{c.pk}.{g.pk}')

    def test_gist_index_exists(self):
        """Every ltree-backed table has a GiST index on path."""
        expected = {
            'dcim_region_path_gist',
            'dcim_sitegroup_path_gist',
            'dcim_location_path_gist',
            'dcim_devicerole_path_gist',
            'dcim_platform_path_gist',
            'dcim_inventoryitem_path_gist',
            'dcim_inv_item_tmpl_path_gist',
            'dcim_modulebay_path_gist',
            'tenancy_tenantgroup_path_gist',
            'tenancy_contactgroup_path_gist',
            'wireless_lan_grp_path_gist',
        }
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT indexname FROM pg_indexes
                WHERE indexname = ANY(%s) AND indexdef LIKE '%%USING gist%%'
            """, [list(expected)])
            found = {row[0] for row in cursor.fetchall()}
        self.assertSetEqual(found, expected)


class LtreeAPIParityTests(TestCase):
    """Verify the MPTTModel-compatible API surface."""

    @classmethod
    def setUpTestData(cls):
        # Build:  root -> mid -> leaf
        #              -> leaf2 (sibling of mid's child)
        cls.root = Region.objects.create(name='Root', slug='root-api')
        cls.mid = Region.objects.create(parent=cls.root, name='Mid', slug='mid-api')
        cls.leaf = Region.objects.create(parent=cls.mid, name='Leaf', slug='leaf-api')
        cls.leaf2 = Region.objects.create(parent=cls.mid, name='Leaf2', slug='leaf2-api')

    def test_level(self):
        self.assertEqual(self.root.level, 0)
        self.assertEqual(self.mid.level, 1)
        self.assertEqual(self.leaf.level, 2)
        self.assertEqual(self.leaf.get_level(), 2)

    def test_is_root_leaf_child(self):
        self.assertTrue(self.root.is_root_node())
        self.assertFalse(self.root.is_leaf_node())
        self.assertFalse(self.root.is_child_node())
        self.assertFalse(self.leaf.is_root_node())
        self.assertTrue(self.leaf.is_leaf_node())
        self.assertTrue(self.leaf.is_child_node())

    def test_get_root(self):
        self.assertEqual(self.leaf.get_root(), self.root)
        self.assertEqual(self.root.get_root(), self.root)

    def test_get_ancestors(self):
        ancestors = list(self.leaf.get_ancestors().values_list('name', flat=True))
        self.assertEqual(ancestors, ['Root', 'Mid'])
        with_self = list(self.leaf.get_ancestors(include_self=True).values_list('name', flat=True))
        self.assertEqual(with_self, ['Root', 'Mid', 'Leaf'])

    def test_get_descendants(self):
        descendants = sorted(self.root.get_descendants().values_list('name', flat=True))
        self.assertEqual(descendants, ['Leaf', 'Leaf2', 'Mid'])
        self.assertEqual(self.root.get_descendant_count(), 3)

    def test_get_children(self):
        children = sorted(self.root.get_children().values_list('name', flat=True))
        self.assertEqual(children, ['Mid'])

    def test_get_siblings(self):
        siblings = list(self.leaf.get_siblings().values_list('name', flat=True))
        self.assertEqual(siblings, ['Leaf2'])

    def test_get_family(self):
        family = sorted(self.mid.get_family().values_list('name', flat=True))
        self.assertEqual(family, ['Leaf', 'Leaf2', 'Mid', 'Root'])

    def test_move_to(self):
        new_root = Region.objects.create(name='New', slug='new-api')
        self.leaf.move_to(new_root)
        self.leaf.refresh_from_db()
        self.assertEqual(self.leaf.parent, new_root)
        self.assertEqual(self.leaf.path, f'{new_root.pk}.{self.leaf.pk}')


class CycleValidationTests(TestCase):
    """clean() must refuse to assign a descendant as parent."""

    def test_cycle_raises(self):
        from django.core.exceptions import ValidationError
        a = Region.objects.create(name='A', slug='a-cyc')
        b = Region.objects.create(parent=a, name='B', slug='b-cyc')
        Region.objects.create(parent=b, name='C', slug='c-cyc')
        a.parent = b
        with self.assertRaises(ValidationError):
            a.full_clean()


class AddRelatedCountTests(TestCase):
    """add_related_count must cumulate across subtrees via path <@."""

    def test_cumulative_fk_count(self):
        root = Region.objects.create(name='R', slug='r-arc')
        child = Region.objects.create(parent=root, name='C', slug='c-arc')
        Site.objects.create(name='S1', slug='s1-arc', region=child)
        Site.objects.create(name='S2', slug='s2-arc', region=root)

        qs = Region.objects.add_related_count(
            Region.objects.filter(slug__endswith='-arc'),
            Site, 'region', 'site_count', cumulative=True,
        )
        counts = {r.name: r.site_count for r in qs}
        # root sees both sites (direct + via child)
        self.assertEqual(counts['R'], 2)
        self.assertEqual(counts['C'], 1)
