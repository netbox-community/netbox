"""Tests for the ltree-based hierarchical model infrastructure."""
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test import TestCase

from core.models import ObjectChange
from dcim.models import Region, Site
from tenancy.models import Contact, ContactGroup


def _path(*pks):
    """Construct the expected ltree path value from a sequence of PKs.

    Mirrors the trigger's zero-padded label scheme (19 chars per label).
    """
    return '.'.join(str(pk).zfill(19) for pk in pks)


class LtreeTriggerTests(TestCase):
    """Verify per-row PostgreSQL triggers maintain `path` correctly."""

    def test_insert_root_path(self):
        r = Region.objects.create(name='Root', slug='root')
        self.assertEqual(r.path, _path(r.pk))

    def test_insert_child_path(self):
        r = Region.objects.create(name='Root', slug='root')
        c = Region.objects.create(parent=r, name='Child', slug='child')
        self.assertEqual(c.path, _path(r.pk, c.pk))

    def test_grandchild_path(self):
        r = Region.objects.create(name='R', slug='r')
        c = Region.objects.create(parent=r, name='C', slug='c')
        g = Region.objects.create(parent=c, name='G', slug='g')
        self.assertEqual(g.path, _path(r.pk, c.pk, g.pk))

    def test_move_cascades_to_descendants(self):
        r = Region.objects.create(name='R', slug='r')
        c = Region.objects.create(parent=r, name='C', slug='c')
        g = Region.objects.create(parent=c, name='G', slug='g')
        c.parent = None
        c.save()
        c.refresh_from_db()
        g.refresh_from_db()
        self.assertEqual(c.path, _path(c.pk))
        self.assertEqual(g.path, _path(c.pk, g.pk))

    def test_bulk_create_populates_paths(self):
        """BEFORE INSERT trigger fires on bulk_create, populating path."""
        root = Region.objects.create(name='R', slug='r-bulk')
        children = Region.objects.bulk_create([
            Region(parent=root, name=f'C{i}', slug=f'c{i}-bulk') for i in range(3)
        ])
        for child in children:
            child.refresh_from_db()
            self.assertEqual(child.path, _path(root.pk, child.pk))

    def test_queryset_update_with_parent_id_cascades(self):
        """Raw .update() that changes parent_id still fires triggers."""
        r1 = Region.objects.create(name='R1', slug='r1-up')
        r2 = Region.objects.create(name='R2', slug='r2-up')
        c = Region.objects.create(parent=r1, name='C', slug='c-up')
        g = Region.objects.create(parent=c, name='G', slug='g-up')

        Region.objects.filter(pk=c.pk).update(parent=r2)
        c.refresh_from_db()
        g.refresh_from_db()
        self.assertEqual(c.path, _path(r2.pk, c.pk))
        self.assertEqual(g.path, _path(r2.pk, c.pk, g.pk))

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
        self.assertEqual(self.leaf.path, _path(new_root.pk, self.leaf.pk))


class CycleValidationTests(TestCase):
    """clean() and save() must refuse to assign self or a descendant as parent."""

    def test_cycle_raises(self):
        from django.core.exceptions import ValidationError
        a = Region.objects.create(name='A', slug='a-cyc')
        b = Region.objects.create(parent=a, name='B', slug='b-cyc')
        Region.objects.create(parent=b, name='C', slug='c-cyc')
        a.parent = b
        with self.assertRaises(ValidationError):
            a.full_clean()

    def test_cycle_raises_on_save_without_clean(self):
        # The save()-level guard mirrors django-mptt's InvalidMove: a cyclic move
        # is rejected even when full_clean() is bypassed (scripts, bulk callers).
        from django.core.exceptions import ValidationError
        a = Region.objects.create(name='A', slug='a-cyc2')
        b = Region.objects.create(parent=a, name='B', slug='b-cyc2')
        Region.objects.create(parent=b, name='C', slug='c-cyc2')
        a.parent = b
        with self.assertRaises(ValidationError):
            a.save()
        # The rejected move must leave the tree unchanged.
        a.refresh_from_db()
        self.assertIsNone(a.parent_id)

    def test_self_parent_raises_on_save(self):
        from django.core.exceptions import ValidationError
        a = Region.objects.create(name='A', slug='a-self')
        a.parent = a
        with self.assertRaises(ValidationError):
            a.save()

    def test_move_to_unrelated_parent_is_allowed(self):
        # A legitimate move (target is neither self nor a descendant) must succeed.
        a = Region.objects.create(name='A', slug='a-ok')
        b = Region.objects.create(name='B', slug='b-ok')
        child = Region.objects.create(parent=a, name='Child', slug='child-ok')
        child.parent = b
        child.save()
        child.refresh_from_db()
        self.assertEqual(child.parent_id, b.pk)
        self.assertEqual(child.path, _path(b.pk, child.pk))


class SortPathTests(TestCase):
    """
    Verify that sort_path produces tree-flatten output with siblings in name
    order, mirroring MPTT's `order_insertion_by=('name',)` behavior.
    """

    def test_siblings_in_name_order_regardless_of_insertion_order(self):
        # Create siblings out of name order
        Region.objects.create(name='Zebra', slug='zebra-sp')
        Region.objects.create(name='Aardvark', slug='aardvark-sp')
        buffalo = Region.objects.create(name='Buffalo', slug='buffalo-sp')

        # Children of Buffalo also out of order
        Region.objects.create(parent=buffalo, name='Zoo', slug='b-zoo-sp')
        Region.objects.create(parent=buffalo, name='Apex', slug='b-apex-sp')

        ordered = list(
            Region.objects.filter(slug__endswith='-sp')
            .order_by('sort_path')
            .values_list('name', flat=True)
        )
        # Tree-flatten with siblings in name order:
        # Aardvark, Buffalo (parent), Apex (child), Zoo (child), Zebra
        self.assertEqual(ordered, ['Aardvark', 'Buffalo', 'Apex', 'Zoo', 'Zebra'])

    def test_default_ordering_is_sort_path(self):
        """Region.objects.all() uses sort_path-based ordering by default."""
        Region.objects.create(name='B', slug='b-default')
        Region.objects.create(name='A', slug='a-default')
        names = list(
            Region.objects.filter(slug__endswith='-default').values_list('name', flat=True)
        )
        self.assertEqual(names, ['A', 'B'])

    def test_get_descendants_returns_siblings_in_name_order(self):
        """
        For models with a sort_path column, get_descendants() must return
        descendants with siblings in name order (matching MPTT's
        order_insertion_by behavior), not insertion/PK order.
        """
        root = Region.objects.create(name='Root', slug='root-gdord')
        # Insert siblings out of name order
        Region.objects.create(parent=root, name='Zebra', slug='z-gdord')
        Region.objects.create(parent=root, name='Aardvark', slug='a-gdord')
        Region.objects.create(parent=root, name='Buffalo', slug='b-gdord')
        names = list(root.get_descendants().values_list('name', flat=True))
        self.assertEqual(names, ['Aardvark', 'Buffalo', 'Zebra'])

    def test_get_children_returns_in_name_order(self):
        root = Region.objects.create(name='Root', slug='root-gcord')
        Region.objects.create(parent=root, name='Zebra', slug='z-gcord')
        Region.objects.create(parent=root, name='Aardvark', slug='a-gcord')
        names = list(root.get_children().values_list('name', flat=True))
        self.assertEqual(names, ['Aardvark', 'Zebra'])

    def test_get_siblings_returns_in_name_order(self):
        root = Region.objects.create(name='Root', slug='root-gsord')
        Region.objects.create(parent=root, name='Zebra', slug='z-gsord')
        a = Region.objects.create(parent=root, name='Aardvark', slug='a-gsord')
        Region.objects.create(parent=root, name='Buffalo', slug='b-gsord')
        names = list(a.get_siblings().values_list('name', flat=True))
        self.assertEqual(names, ['Buffalo', 'Zebra'])


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

    def test_cumulative_m2m_count(self):
        """
        Cumulative count over an M2M relation walks the subtree via
        path <@, joining the through table by the correct columns.

        Regression: previously the JOINs swapped m2m_column_name() and
        m2m_reverse_name(), producing wrong counts on M2M relations.
        """
        root = ContactGroup.objects.create(name='Root', slug='root-m2m')
        child = ContactGroup.objects.create(parent=root, name='Child', slug='child-m2m')
        leaf = ContactGroup.objects.create(parent=child, name='Leaf', slug='leaf-m2m')
        # 3 contacts spread across the subtree (one per node)
        c_root = Contact.objects.create(name='CR')
        c_child = Contact.objects.create(name='CC')
        c_leaf = Contact.objects.create(name='CL')
        c_root.groups.add(root)
        c_child.groups.add(child)
        c_leaf.groups.add(leaf)

        qs = ContactGroup.objects.add_related_count(
            ContactGroup.objects.filter(slug__endswith='-m2m'),
            Contact, 'groups', 'contact_count', cumulative=True,
        )
        counts = {g.name: g.contact_count for g in qs}
        self.assertEqual(counts['Root'], 3)
        self.assertEqual(counts['Child'], 2)
        self.assertEqual(counts['Leaf'], 1)

    def test_noncumulative_fk_count(self):
        """Non-cumulative FK count includes only rows pointing directly at the node."""
        root = Region.objects.create(name='R', slug='r-ncfk')
        child = Region.objects.create(parent=root, name='C', slug='c-ncfk')
        Site.objects.create(name='S1', slug='s1-ncfk', region=child)
        Site.objects.create(name='S2', slug='s2-ncfk', region=root)

        qs = Region.objects.add_related_count(
            Region.objects.filter(slug__endswith='-ncfk'),
            Site, 'region', 'site_count', cumulative=False,
        )
        counts = {r.name: r.site_count for r in qs}
        # Each node counts only its own directly-assigned sites (no subtree rollup).
        self.assertEqual(counts['R'], 1)
        self.assertEqual(counts['C'], 1)

    def test_noncumulative_m2m_count(self):
        """Non-cumulative M2M count includes only directly-assigned rows, not the subtree."""
        root = ContactGroup.objects.create(name='Root', slug='root-ncm2m')
        child = ContactGroup.objects.create(parent=root, name='Child', slug='child-ncm2m')
        c_root = Contact.objects.create(name='CR-nc')
        c_child = Contact.objects.create(name='CC-nc')
        c_root.groups.add(root)
        c_child.groups.add(child)

        qs = ContactGroup.objects.add_related_count(
            ContactGroup.objects.filter(slug__endswith='-ncm2m'),
            Contact, 'groups', 'contact_count', cumulative=False,
        )
        counts = {g.name: g.contact_count for g in qs}
        self.assertEqual(counts['Root'], 1)
        self.assertEqual(counts['Child'], 1)


class SaveUpdateFieldsTests(TestCase):
    """
    Regression: when save(update_fields=...) excludes parent, _loaded_parent_id
    must not advance, otherwise a subsequent full save() will mis-detect the
    parent change as already-applied and leave path stale in memory.
    """

    def test_partial_save_then_full_save_refreshes_path(self):
        r1 = Region.objects.create(name='R1', slug='r1-uf')
        r2 = Region.objects.create(name='R2', slug='r2-uf')
        obj = Region.objects.create(name='Obj', slug='obj-uf')
        original_path = obj.path

        # Reparent in memory but persist a different field only:
        obj.parent = r1
        obj.name = 'Obj-renamed'
        obj.save(update_fields=['name'])

        # DB parent_id is still NULL — confirm:
        db_parent = Region.objects.values_list('parent_id', flat=True).get(pk=obj.pk)
        self.assertIsNone(db_parent)
        self.assertEqual(
            Region.objects.values_list('path', flat=True).get(pk=obj.pk),
            original_path,
        )

        # Now a full save persists the new parent — path must refresh:
        obj.parent = r2
        obj.save()
        db_path = Region.objects.values_list('path', flat=True).get(pk=obj.pk)
        self.assertEqual(db_path, _path(r2.pk, obj.pk))
        self.assertEqual(obj.path, db_path, "in-memory path is stale after full save")


class BulkCreateOrderingTests(TestCase):
    """
    The BEFORE INSERT trigger looks up parent.path via subquery per row.
    In bulk_create the trigger fires per row in list order, so a parent
    placed in the same batch must precede its children.
    """

    def test_parent_before_child_in_same_batch(self):
        root = Region.objects.create(name='R', slug='r-bcord')
        # Parent BEFORE child in the list — both get correct paths
        parent_pending = Region(parent=root, name='Mid', slug='mid-bcord')
        child_pending = Region(parent=parent_pending, name='Leaf', slug='leaf-bcord')
        # parent_pending isn't yet saved, so child_pending.parent_id is None;
        # set the parent reference after the parent is saved.
        Region.objects.bulk_create([parent_pending])
        parent_pending.refresh_from_db()
        child_pending.parent = parent_pending
        Region.objects.bulk_create([child_pending])
        child_pending.refresh_from_db()
        self.assertEqual(child_pending.path, _path(root.pk, parent_pending.pk, child_pending.pk))

    def test_bulk_create_rejects_child_before_parent_in_same_batch(self):
        """The guard refuses misordered batches instead of writing bad paths."""
        unsaved_parent = Region(name='P', slug='p-bcrej')
        unsaved_child = Region(parent=unsaved_parent, name='C', slug='c-bcrej')
        with self.assertRaises(ValueError) as ctx:
            Region.objects.bulk_create([unsaved_child, unsaved_parent])
        self.assertIn('unsaved parent', str(ctx.exception))

    def test_bulk_create_rejects_unsaved_parent_earlier_in_batch(self):
        """
        An unsaved parent placed earlier in the batch must also be rejected:
        Django binds VALUES from the child's parent_id BEFORE the parent's
        RETURNING-assigned pk lands, so the child would be inserted with
        parent_id=NULL and silently stored as a root.
        """
        unsaved_parent = Region(name='P', slug='p-bcearly')
        unsaved_child = Region(parent=unsaved_parent, name='C', slug='c-bcearly')
        with self.assertRaises(ValueError) as ctx:
            Region.objects.bulk_create([unsaved_parent, unsaved_child])
        self.assertIn('unsaved parent', str(ctx.exception))
        # Nothing should have been written.
        self.assertFalse(Region.objects.filter(slug__in=('p-bcearly', 'c-bcearly')).exists())

    def test_bulk_create_rejects_unsaved_parent_not_in_batch(self):
        """
        An unsaved parent that isn't in the batch must be rejected with a clear
        ValueError; otherwise the child's parent_id is None at INSERT time and
        the BEFORE trigger silently stores the row as a root.
        """
        external_parent = Region(name='X', slug='x-bcok')  # not in the batch
        with self.assertRaises(ValueError) as ctx:
            Region.objects.bulk_create([Region(parent=external_parent, name='Y', slug='y-bcok')])
        self.assertIn('unsaved parent', str(ctx.exception))
        # Nothing should have been written.
        self.assertFalse(Region.objects.filter(slug='y-bcok').exists())


class TreeNodeFilterTests(TestCase):
    """
    Regression: the FK branch of TreeNodeFilter.filter() previously destructured
    q_filter.children as (str, value) tuples, which crashed for compound Q
    match types (DESCENDANTS, ANCESTORS, SIBLINGS, SELF_AND_DESCENDANTS). The
    FK branch must resolve via __in like the M2M / M2O branches.
    """

    @classmethod
    def setUpTestData(cls):
        from tenancy.models import Tenant, TenantGroup
        cls.Tenant = Tenant
        cls.TenantGroup = TenantGroup
        cls.root = TenantGroup.objects.create(name='Root', slug='root-tnf')
        cls.mid = TenantGroup.objects.create(parent=cls.root, name='Mid', slug='mid-tnf')
        cls.leaf = TenantGroup.objects.create(parent=cls.mid, name='Leaf', slug='leaf-tnf')
        cls.sibling = TenantGroup.objects.create(parent=cls.root, name='Sibling', slug='sibling-tnf')

        cls.t_root = Tenant.objects.create(name='TRoot', slug='troot-tnf', group=cls.root)
        cls.t_mid = Tenant.objects.create(name='TMid', slug='tmid-tnf', group=cls.mid)
        cls.t_leaf = Tenant.objects.create(name='TLeaf', slug='tleaf-tnf', group=cls.leaf)
        cls.t_sibling = Tenant.objects.create(name='TSib', slug='tsib-tnf', group=cls.sibling)

    def _filter(self, match_type):
        from netbox.graphql.filter_lookups import TreeNodeFilter, TreeNodeMatch
        tnf = TreeNodeFilter(id=self.mid.pk, match_type=getattr(TreeNodeMatch, match_type))
        # `filter` is decorated by @strawberry_django.filter_field; its wrapper
        # asserts info is not None. The undecorated body is on `_unbound_wrapped_func`.
        inner = TreeNodeFilter.filter._unbound_wrapped_func
        qs, q = inner(tnf, info=None, queryset=self.Tenant.objects.all(), prefix='group__')
        return list(qs.filter(q).values_list('name', flat=True))

    def test_descendants_strict(self):
        # DESCENDANTS of `mid` = leaf only (Mid itself excluded)
        names = self._filter('DESCENDANTS')
        self.assertEqual(sorted(names), ['TLeaf'])

    def test_self_and_descendants(self):
        names = self._filter('SELF_AND_DESCENDANTS')
        self.assertEqual(sorted(names), ['TLeaf', 'TMid'])

    def test_ancestors(self):
        names = self._filter('ANCESTORS')
        # Ancestors of Mid = Root only (Mid itself excluded)
        self.assertEqual(sorted(names), ['TRoot'])

    def test_siblings(self):
        # Siblings of Mid (within Root) = Sibling
        names = self._filter('SIBLINGS')
        self.assertEqual(sorted(names), ['TSib'])


class DescendantLookupSemanticsTests(TestCase):
    """
    path__descendant is strict (path <@ rhs AND path != rhs); the inclusive
    form is path__descendant_or_equal. Previously both were inclusive.
    """

    def test_strict_descendant_excludes_self(self):
        root = Region.objects.create(name='Root', slug='root-dls')
        Region.objects.create(parent=root, name='Kid', slug='kid-dls')
        strict = list(
            Region.objects.filter(path__descendant=root.path)
            .values_list('name', flat=True)
        )
        self.assertEqual(sorted(strict), ['Kid'])
        inclusive = list(
            Region.objects.filter(path__descendant_or_equal=root.path)
            .values_list('name', flat=True)
        )
        self.assertEqual(sorted(inclusive), ['Kid', 'Root'])


class RenameCascadesSortPathTests(TestCase):
    """
    Renaming a node updates its own sort_path AND cascades into descendants'
    sort_paths via the AFTER trigger. (Diverges from MPTT order_insertion_by,
    which leaves descendants stale until manual rebuild.)
    """

    def test_rename_cascades_into_descendants(self):
        parent = Region.objects.create(name='Bravo', slug='bravo-rcsp')
        mid = Region.objects.create(parent=parent, name='Mid', slug='mid-rcsp')
        leaf = Region.objects.create(parent=mid, name='Leaf', slug='leaf-rcsp')

        parent.name = 'Zulu'
        parent.save()

        parent.refresh_from_db()
        mid.refresh_from_db()
        leaf.refresh_from_db()
        self.assertEqual(parent.sort_path, 'Zulu')
        self.assertEqual(mid.sort_path, f'Zulu{chr(9)}Mid')
        self.assertEqual(leaf.sort_path, f'Zulu{chr(9)}Mid{chr(9)}Leaf')
        # Paths unchanged — only sort_path moved.
        self.assertEqual(mid.path, _path(parent.pk, mid.pk))
        self.assertEqual(leaf.path, _path(parent.pk, mid.pk, leaf.pk))

    def test_rename_does_not_affect_unrelated_subtree(self):
        # Two roots; renaming one must not touch the other's sort_path.
        a = Region.objects.create(name='AA', slug='aa-iso')
        Region.objects.create(parent=a, name='AKid', slug='akid-iso')
        b = Region.objects.create(name='BB', slug='bb-iso')
        b_kid = Region.objects.create(parent=b, name='BKid', slug='bkid-iso')

        a.name = 'AAren'
        a.save()

        b_kid.refresh_from_db()
        self.assertEqual(b_kid.sort_path, f'BB{chr(9)}BKid')


class RebuildSortPathsTests(TestCase):
    """rebuild_sort_paths() is still available for repair after raw SQL writes."""

    def test_rebuild_after_raw_update(self):
        parent = Region.objects.create(name='Bravo', slug='bravo-rsp')
        mid = Region.objects.create(parent=parent, name='Mid', slug='mid-rsp')
        # Raw .update() with only the name column bypasses the BEFORE trigger
        # (its column list is parent_id + name, but the trigger is keyed on
        # name in the SET clause). Actually update() on `name` DOES fire the
        # trigger now — so to simulate a bypass we corrupt sort_path directly.
        Region.objects.filter(pk=parent.pk).update(sort_path='garbage')
        Region.objects.filter(pk=mid.pk).update(sort_path='also-garbage')

        Region.rebuild_sort_paths()
        parent.refresh_from_db()
        mid.refresh_from_db()
        self.assertEqual(parent.sort_path, 'Bravo')
        self.assertEqual(mid.sort_path, f'Bravo{chr(9)}Mid')

    def test_raises_without_sort_path(self):
        # InventoryItem uses LtreeModel but doesn't have a sort_path column.
        from dcim.models import InventoryItem
        with self.assertRaises(NotImplementedError):
            InventoryItem.rebuild_sort_paths()


class SortPathRefreshTests(TestCase):
    """
    save() must refresh the in-memory `sort_path` (not just `path`) after insert
    and reparent, so callers (notably change logging) never snapshot a stale value.
    """

    def test_create_refreshes_sort_path(self):
        root = Region.objects.create(name='Root', slug='root-spr')
        child = Region.objects.create(name='Kid', slug='kid-spr', parent=root)
        db_sort_path = Region.objects.values_list('sort_path', flat=True).get(pk=child.pk)
        self.assertEqual(child.sort_path, db_sort_path)
        self.assertEqual(child.sort_path, f'Root{chr(9)}Kid')

    def test_reparent_refreshes_sort_path(self):
        a = Region.objects.create(name='Alpha', slug='alpha-spr')
        b = Region.objects.create(name='Bravo', slug='bravo-spr')
        child = Region.objects.create(name='Kid', slug='kid2-spr', parent=a)
        child.parent = b
        child.save()
        db_sort_path = Region.objects.values_list('sort_path', flat=True).get(pk=child.pk)
        self.assertEqual(child.sort_path, db_sort_path)
        self.assertEqual(child.sort_path, f'Bravo{chr(9)}Kid')

    def test_rename_refreshes_sort_path(self):
        # The trigger rewrites sort_path on a name change; the in-memory instance
        # must reflect it without a manual refresh_from_db().
        root = Region.objects.create(name='Root', slug='root-rn')
        root.name = 'Renamed'
        root.save()
        db_sort_path = Region.objects.values_list('sort_path', flat=True).get(pk=root.pk)
        self.assertEqual(root.sort_path, db_sort_path)
        self.assertEqual(root.sort_path, 'Renamed')


class ReapplyModelOrderingTests(TestCase):
    """Ltree-backed models must be exempt from reapply_model_ordering()."""

    def test_ltree_model_is_exempt(self):
        from utilities.query import reapply_model_ordering
        # Clear ordering so a non-exempt model would be re-ordered by Meta.ordering.
        qs = Region.objects.all().order_by()
        result = reapply_model_ordering(qs)
        # The LtreeManager is inherited from the abstract base (not in
        # local_managers), so the exemption must still apply and return qs as-is.
        self.assertIs(result, qs)


class AddRelatedCountErrorTests(TestCase):
    """
    add_related_count() must not raise at queryset-build time for unresolvable
    rel_field — many call sites bind the annotation as a class attribute at
    module import. The annotation is still attached using the Django default
    column naming, and any error surfaces at evaluation time.
    """

    def test_unknown_field_does_not_raise_at_build(self):
        qs = Region.objects.add_related_count(
            Region.objects.all(), Region, 'not_a_field', 'bogus_count', cumulative=True
        )
        self.assertIn('bogus_count', qs.query.annotations)


class ChangeLogExclusionTests(TestCase):
    """
    Trigger-maintained columns (`path`, `sort_path`) must be excluded from change
    log diffs, and the postchange snapshot must capture the refreshed values.
    """

    def test_sort_path_excluded_from_diff(self):
        oc = ObjectChange()
        oc.changed_object_type = ContentType.objects.get_for_model(Region)
        self.assertIn('path', oc.diff_exclude_fields)
        self.assertIn('sort_path', oc.diff_exclude_fields)

    def test_reparent_postchange_snapshot_matches_db(self):
        a = Region.objects.create(name='Alpha', slug='alpha-cl')
        b = Region.objects.create(name='Bravo', slug='bravo-cl')
        child = Region.objects.create(name='Kid', slug='kid-cl', parent=a)
        # Reload so the prechange snapshot reflects the persisted state.
        child = Region.objects.get(pk=child.pk)
        child.snapshot()
        child.parent = b
        child.save()
        oc = child.to_objectchange('update')
        db = Region.objects.values('path', 'sort_path').get(pk=child.pk)
        self.assertEqual(oc.postchange_data['path'], db['path'])
        self.assertEqual(oc.postchange_data['sort_path'], db['sort_path'])
        # path/sort_path are excluded, so they must not surface in the cleaned diff data.
        self.assertNotIn('sort_path', oc.postchange_data_clean)
        self.assertNotIn('path', oc.postchange_data_clean)


class MPTTChangeLogExclusionTests(TestCase):
    """
    ObjectChange.diff_exclude_fields must hide MPTT bookkeeping columns
    (lft/rght/tree_id/level) for plugin models still using the deprecated
    MPTT-backed NestedGroupModel, in addition to ltree's path/sort_path.
    """

    def test_diff_exclude_fields_for_mptt_subclass(self):
        from unittest.mock import MagicMock

        from mptt.models import MPTTModel

        class _FakeMPTT(MPTTModel):
            class Meta:
                abstract = True
                app_label = 'tests'

        oc = ObjectChange()
        fake_ct = MagicMock()
        fake_ct.model_class.return_value = _FakeMPTT
        # Prime the FK descriptor's cache so accessing changed_object_type
        # returns our mock without hitting the DB or invoking type checks.
        ObjectChange._meta.get_field('changed_object_type').set_cached_value(oc, fake_ct)

        excluded = oc.diff_exclude_fields
        self.assertIn('lft', excluded)
        self.assertIn('rght', excluded)
        self.assertIn('tree_id', excluded)
        self.assertIn('level', excluded)


class AddRelatedCountResilienceTests(TestCase):
    """
    add_related_count() must not raise FieldDoesNotExist at queryset-build
    time so that view modules (which bind it as a class attribute) can be
    imported even if a referenced field has been renamed.
    """

    def test_unknown_field_does_not_raise(self):
        # Bare manager call equivalent to a view class body using a stale name.
        qs = Region.objects.add_related_count(
            Region.objects.all(),
            Region,  # any model; the field name is what matters
            'this_field_does_not_exist',
            'noop_count',
            cumulative=True,
        )
        # The annotation was attached; evaluating it would fail at the DB
        # (column doesn't exist) but importing the view module must succeed.
        self.assertIn('noop_count', qs.query.annotations)


class CascadeTriggerScopeTests(TestCase):
    """
    The AFTER cascade trigger fires on parent_id or name changes. A rename
    leaves `path` untouched but pushes the new sort_path into descendants.
    """

    def test_rename_preserves_descendant_path_but_updates_sort_path(self):
        parent = Region.objects.create(name='Bravo', slug='bravo-ct')
        child = Region.objects.create(parent=parent, name='Mid', slug='mid-ct')
        original_child_path = child.path
        parent.name = 'Zulu'
        parent.save()
        child.refresh_from_db()
        # Path is unaffected by a rename; sort_path follows the new name.
        self.assertEqual(child.path, original_child_path)
        self.assertNotIn('Bravo', child.sort_path)
        self.assertIn('Zulu', child.sort_path)


class CycleGuardWithEmptyPathTests(TestCase):
    """
    _parent_creates_cycle must catch self-as-parent even when self.path is
    empty or deferred — otherwise an instance constructed without a loaded
    path can pass the Python guard and corrupt the tree.
    """

    def test_self_parent_rejected_when_path_is_empty(self):
        from django.core.exceptions import ValidationError
        a = Region.objects.create(name='A', slug='a-empty-cyc')
        # Simulate a caller (script, plugin) that holds an instance whose `path`
        # attribute was never loaded — e.g. via .only('id', 'parent_id').
        # Empty-string path is the LtreeField default, so this mirrors what a
        # deferred-or-unset path looks like at the Python layer.
        a.path = ''
        a.parent_id = a.pk
        with self.assertRaises(ValidationError):
            a.save()


class TriggerCycleGuardTests(TestCase):
    """
    The BEFORE INSERT/UPDATE trigger must reject a parent_id assignment that
    would form a cycle. The Python save()-time guard already catches this for
    ordinary save(); the trigger backstops QuerySet.update / bulk_update /
    raw UPDATEs that bypass save().
    """

    def test_queryset_update_to_self_parent_blocked_by_trigger(self):
        from django.db import IntegrityError, transaction
        a = Region.objects.create(name='A', slug='a-tgcyc')
        # IntegrityError leaves Django's transaction marked-for-rollback; wrap
        # the failing UPDATE in a savepoint so the outer test transaction can
        # continue to issue queries (refresh_from_db).
        with self.assertRaises(IntegrityError) as ctx:
            with transaction.atomic():
                Region.objects.filter(pk=a.pk).update(parent_id=a.pk)
        self.assertIn('cycle detected', str(ctx.exception))
        a.refresh_from_db()
        self.assertIsNone(a.parent_id)

    def test_queryset_update_to_descendant_blocked_by_trigger(self):
        from django.db import IntegrityError, transaction
        a = Region.objects.create(name='A', slug='a-tgcyc2')
        b = Region.objects.create(parent=a, name='B', slug='b-tgcyc2')
        # Try to reparent A under B (B is A's descendant) via raw UPDATE.
        with self.assertRaises(IntegrityError) as ctx:
            with transaction.atomic():
                Region.objects.filter(pk=a.pk).update(parent_id=b.pk)
        self.assertIn('cycle detected', str(ctx.exception))
        a.refresh_from_db()
        self.assertIsNone(a.parent_id)

    def test_legitimate_reparent_via_update_still_works(self):
        a = Region.objects.create(name='A', slug='a-tgok')
        b = Region.objects.create(name='B', slug='b-tgok')
        child = Region.objects.create(parent=a, name='C', slug='c-tgok')
        Region.objects.filter(pk=child.pk).update(parent_id=b.pk)
        child.refresh_from_db()
        self.assertEqual(child.parent_id, b.pk)
        self.assertEqual(child.path, _path(b.pk, child.pk))

    def test_queryset_update_mid_tree_to_own_descendant_blocked(self):
        """
        Reparenting a non-root node under one of its own (non-immediate)
        descendants must raise. The earlier `lpad(NEW.id) @> parent_path`
        check only fired when NEW was the root of parent_path, missing
        mid-tree cycles entirely.
        """
        from django.db import IntegrityError, transaction
        a = Region.objects.create(name='A', slug='a-midcyc')
        b = Region.objects.create(parent=a, name='B', slug='b-midcyc')
        c = Region.objects.create(parent=b, name='C', slug='c-midcyc')
        # Try to make B a child of C — B is mid-tree (path A.B), parent_path is A.B.C.
        with self.assertRaises(IntegrityError) as ctx:
            with transaction.atomic():
                Region.objects.filter(pk=b.pk).update(parent_id=c.pk)
        self.assertIn('cycle detected', str(ctx.exception))
        b.refresh_from_db()
        self.assertEqual(b.parent_id, a.pk)

    def test_queryset_update_mid_tree_self_loop_blocked(self):
        """A non-root node assigning itself as parent must also raise."""
        from django.db import IntegrityError, transaction
        a = Region.objects.create(name='A', slug='a-midself')
        b = Region.objects.create(parent=a, name='B', slug='b-midself')
        with self.assertRaises(IntegrityError) as ctx:
            with transaction.atomic():
                Region.objects.filter(pk=b.pk).update(parent_id=b.pk)
        self.assertIn('cycle detected', str(ctx.exception))
        b.refresh_from_db()
        self.assertEqual(b.parent_id, a.pk)


class NaturalSortSortPathTests(TestCase):
    """
    Sort-path separator must produce correct tree-flatten ordering under the
    `natural_sort` (ICU `und-u-kn-true`) collation used by ModuleBay,
    TenantGroup, and WirelessLANGroup. chr(1) was variable-ignorable under
    that collation and would interleave children with unrelated roots;
    chr(9) (TAB) is treated non-variably and orders deterministically.
    """

    def test_chr9_separator_collates_below_letters_under_natural_sort(self):
        # Direct collation probe — independent of any model schema.
        with connection.cursor() as cur:
            cur.execute("""
                SELECT
                  ('A' || chr(9) || 'Z') COLLATE "natural_sort"
                    < 'AA' COLLATE "natural_sort"
            """)
            self.assertTrue(cur.fetchone()[0])

    def test_tree_flatten_ordering_under_natural_sort(self):
        # TenantGroup.sort_path uses natural_sort collation; build a small tree
        # where chr(1) would have produced wrong sibling ordering. TenantGroup
        # names are globally unique, so each row gets a distinct name. Under
        # the old chr(1) separator the child's sort_path was variable-ignorable
        # and collated AFTER the unrelated root 'nsP1'; chr(9) sorts strictly
        # below digits/letters and keeps children clustered under their parent.
        from tenancy.models import TenantGroup
        parent = TenantGroup.objects.create(name='nsP', slug='nsp-ns')
        TenantGroup.objects.create(parent=parent, name='nsPchild', slug='nspc-ns')
        TenantGroup.objects.create(name='nsP1', slug='nsp1-ns')  # unrelated root

        names = list(
            TenantGroup.objects.filter(slug__endswith='-ns')
            .order_by('sort_path')
            .values_list('name', flat=True)
        )
        # Expected tree-flatten: parent, its child, then the unrelated root.
        self.assertEqual(names, ['nsP', 'nsPchild', 'nsP1'])
