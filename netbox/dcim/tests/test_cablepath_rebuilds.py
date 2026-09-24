from io import StringIO
from itertools import permutations
from types import SimpleNamespace
from unittest.mock import call, patch

from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import transaction
from django.db.models import Case, IntegerField, Value, When

from dcim import utils
from dcim.choices import CableEndChoices, CableProfileChoices
from dcim.exceptions import UnsupportedCablePath
from dcim.management.commands import trace_paths
from dcim.models import (
    Cable,
    CablePath,
    CableTermination,
    ConsolePort,
    ConsoleServerPort,
    FrontPort,
    Interface,
    PortMapping,
    RearPort,
)
from dcim.tests.utils import BaseCablePathTestCase


class CablePathRebuildTestCase(BaseCablePathTestCase):
    """
    Explicit rebuilds must use current membership, not the order or grouping of historical paths.
    """

    def _create_interfaces(self, *names):
        return [Interface.objects.create(device=self.device, name=name) for name in names]

    def _assert_joint_paths(self, cable, far, origins):
        self.assertCurrentPathExists((far, cable, origins), is_complete=True, is_active=True)
        path = self.assertPathExists((origins, cable, far), is_complete=True, is_active=True)
        for origin in origins:
            origin.refresh_from_db()
            self.assertPathIsSet(origin, path)
        self.assertEqual(CablePath.objects.filter(_nodes__contains=cable).count(), 2)

    def test_rebuild_uses_current_membership_in_every_candidate_order(self):
        for order in permutations(('far', 'joint', 'stale')):
            with self.subTest(order=order), transaction.atomic():
                far, first, second = self._create_interfaces('IF1', 'IF2', 'IF3')
                cable = Cable(a_terminations=[far], b_terminations=[first, second])
                cable.save()
                for origin in (far, first, second):
                    origin.refresh_from_db()
                joint = first._path
                stale = CablePath.from_origin([second])
                stale.save()
                joint.save()
                pks = {'far': far._path_id, 'joint': joint.pk, 'stale': stale.pk}
                node = utils.object_to_path_node(cable)
                filter_paths = CablePath.objects.filter
                candidate_orders = []

                def ordered_candidates(*args, **kwargs):
                    queryset = filter_paths(*args, **kwargs)
                    # Order only candidate discovery, never the replacement helper's overlap lookups.
                    if not args and kwargs in ({'_nodes__overlap': [node]}, {'_nodes__contains': cable}):
                        queryset = queryset.order_by(Case(
                            *[When(pk=pks[name], then=Value(index)) for index, name in enumerate(order)],
                            output_field=IntegerField(),
                        ))
                        candidate_orders.append(list(queryset.values_list('pk', flat=True)))
                    return queryset

                with patch.object(CablePath.objects, 'filter', side_effect=ordered_candidates):
                    utils.rebuild_paths([cable])

                self.assertEqual(candidate_orders, [[pks[name] for name in order]])
                self.assertFalse(CablePath.objects.filter(pk__in=pks.values()).exists())
                self._assert_joint_paths(cable, far, [first, second])
                self.assertEqual(CablePath.objects.count(), 2)

                # Repeating the rebuild must preserve the same shape, without pinning any query order.
                utils.rebuild_paths([cable])
                self._assert_joint_paths(cable, far, [first, second])
                self.assertEqual(CablePath.objects.count(), 2)
                transaction.set_rollback(True)

    def test_rebuild_resolves_a_stale_hop_spanning_current_cable_ends(self):
        far1, origin1, far2, origin2 = self._create_interfaces('IF1', 'IF2', 'IF3', 'IF4')
        cable1 = Cable(a_terminations=[far1], b_terminations=[origin1])
        cable1.save()
        cable2 = Cable(a_terminations=[far2], b_terminations=[origin2])
        cable2.save()
        far2.refresh_from_db()
        untouched = far2._path_id
        stale = CablePath(
            path=[
                [utils.object_to_path_node(origin1), utils.object_to_path_node(origin2)],
                [utils.object_to_path_node(cable1)],
                [utils.object_to_path_node(far1)],
            ],
            is_complete=True,
            is_active=True,
        )
        stale.save()

        utils.rebuild_paths([cable1])

        self.assertFalse(CablePath.objects.filter(pk=stale.pk).exists())
        for cable, far, origin in ((cable1, far1, origin1), (cable2, far2, origin2)):
            self.assertCurrentPathExists((origin, cable, far), is_complete=True)
            self.assertCurrentPathExists((far, cable, origin), is_complete=True)
        far2.refresh_from_db()
        self.assertEqual(far2._path_id, untouched)
        self.assertEqual(CablePath.objects.count(), 4)

    def test_rebuild_failure_restores_all_candidates_and_references(self):
        interfaces = self._create_interfaces('IF1', 'IF2', 'IF3', 'IF4')
        cables = [
            Cable(a_terminations=[interfaces[0]], b_terminations=[interfaces[1]]),
            Cable(a_terminations=[interfaces[2]], b_terminations=[interfaces[3]]),
        ]
        for cable in cables:
            cable.save()
        original_ids = set(CablePath.objects.values_list('pk', flat=True))
        references = dict(Interface.objects.filter(pk__in=[obj.pk for obj in interfaces]).values_list('pk', '_path_id'))
        traced = CablePath.from_origin
        attempts = 0

        def fail_after_a_replacement(origins):
            nonlocal attempts
            attempts += 1
            if attempts == 2:
                self.assertFalse(CablePath.objects.filter(pk__in=original_ids).exists())
                self.assertTrue(CablePath.objects.exclude(pk__in=original_ids).exists())
                raise UnsupportedCablePath('Simulated rebuild failure')
            return traced(origins)

        with patch.object(CablePath, 'from_origin', side_effect=fail_after_a_replacement):
            with self.assertRaisesMessage(UnsupportedCablePath, 'Simulated rebuild failure'):
                utils.rebuild_paths(cables)

        self.assertEqual(attempts, 2)
        self.assertEqual(set(CablePath.objects.values_list('pk', flat=True)), original_ids)
        for interface in interfaces:
            interface.refresh_from_db()
            self.assertEqual(interface._path_id, references[interface.pk])

    def test_rebuild_removes_rows_for_missing_and_disconnected_origins(self):
        far, origin, detached = self._create_interfaces('IF1', 'IF2', 'Detached')
        cable = Cable(a_terminations=[far], b_terminations=[origin])
        cable.save()
        # Encode a nonexistent interface without creating inconsistent current cable associations.
        missing = Interface(pk=1000000000)
        self.assertFalse(Interface.objects.filter(pk=missing.pk).exists())
        obsolete_ids = []
        for obj in (detached, missing):
            path = CablePath(
                path=[
                    [utils.object_to_path_node(obj)],
                    [utils.object_to_path_node(cable)],
                    [utils.object_to_path_node(far)],
                ],
                is_complete=True,
                is_active=True,
            )
            path.save()
            obsolete_ids.append(path.pk)

        utils.rebuild_paths([cable, cable])

        self.assertFalse(CablePath.objects.filter(pk__in=obsolete_ids).exists())
        self.assertCurrentPathExists((origin, cable, far), is_complete=True)
        self.assertCurrentPathExists((far, cable, origin), is_complete=True)
        detached.refresh_from_db()
        self.assertPathIsNotSet(detached)
        self.assertEqual(CablePath.objects.count(), 2)

    def test_origin_group_uses_the_termination_not_cached_fields(self):
        far, first, second = self._create_interfaces('IF1', 'IF2', 'IF3')
        cable = Cable(a_terminations=[far], b_terminations=[first, second])
        cable.save()
        for cached_fields in ({'cable_end': CableEndChoices.SIDE_A}, {'cable': None, 'cable_end': None}):
            with self.subTest(cached_fields=cached_fields):
                Interface.objects.filter(pk=first.pk).update(**cached_fields)
                first.refresh_from_db()
                groups = utils.get_cablepath_origin_groups([first])
                key, origins = next(iter(groups.items()))
                self.assertEqual(key, (cable.pk, CableEndChoices.SIDE_B))
                self.assertEqual(list(origins), [first, second])

                # Membership resolution does not repair the endpoint's cached cable fields.
                if cached_fields.get('cable', cable) is None:
                    before = list(CablePath.objects.order_by('pk').values_list('pk', 'path'))
                    with self.assertRaisesMessage(UnsupportedCablePath, 'same link'):
                        utils.create_cablepaths(origins)
                    self.assertEqual(list(CablePath.objects.order_by('pk').values_list('pk', 'path')), before)
                else:
                    # Legacy tracing resolves the opposite end through CableTermination, not cached cable_end.
                    utils.create_cablepaths(origins)
                    self._assert_joint_paths(cable, far, [first, second])
                first.refresh_from_db()
                self.assertEqual(first.cable_end, cached_fields['cable_end'])
                if 'cable' in cached_fields:
                    self.assertIsNone(first.cable_id)

    def test_origin_connectors_use_termination_metadata_without_repairing_cached_fields(self):
        near1, near2, far1, far2 = self._create_interfaces('Near1', 'Near2', 'Far1', 'Far2')
        cable = Cable(
            profile=CableProfileChoices.TRUNK_2C1P,
            a_terminations=[near1, near2], b_terminations=[far1, far2],
        )
        cable.clean()
        cable.save()
        # Corrupt only the derived connector fields, not current membership or positions.
        Interface.objects.filter(pk__in=[near1.pk, near2.pk]).update(cable_connector=None)
        near1.refresh_from_db()
        groups = utils.get_cablepath_origin_groups([near1])
        origins = groups[(cable.pk, CableEndChoices.SIDE_A)]
        self.assertEqual([(obj.pk, obj.cable_connector) for obj in origins], [(near1.pk, 1), (near2.pk, 2)])

        with patch.object(CablePath, 'from_origin', wraps=CablePath.from_origin) as traced:
            utils.create_cablepaths(origins)

        self.assertEqual(traced.call_args_list, [call([near1]), call([near2])])
        for near, far in ((near1, far1), (near2, far2)):
            self.assertCurrentPathExists((near, cable, far), is_complete=True, is_active=True)
            self.assertCurrentPathExists((far, cable, near), is_complete=True, is_active=True)
        self.assertEqual(CablePath.objects.count(), 4)
        self.assertEqual(
            list(Interface.objects.filter(pk__in=[near1.pk, near2.pk]).values_list('cable_connector', flat=True)),
            [None, None],
        )

        # The explicit rebuild must use the same grouping without persisting a cache repair.
        utils.rebuild_paths([cable])
        for near, far in ((near1, far1), (near2, far2)):
            self.assertCurrentPathExists((near, cable, far), is_complete=True, is_active=True)
            near.refresh_from_db()
            self.assertIsNone(near.cable_connector)
        self.assertEqual(CablePath.objects.count(), 4)

    def test_recovered_connectors_use_termination_metadata(self):
        """
        Recovery partitions co-origins on the authoritative connector, not the endpoint's cached copy.
        """
        trigger, trigger_far = self._create_interfaces('Trigger', 'TriggerFar')
        near1, near2, far1, far2 = self._create_interfaces('Near1', 'Near2', 'Far1', 'Far2')
        trigger_cable = Cable(a_terminations=[trigger], b_terminations=[trigger_far])
        trigger_cable.save()
        cable = Cable(
            profile=CableProfileChoices.TRUNK_2C1P,
            a_terminations=[near1, near2], b_terminations=[far1, far2],
        )
        cable.clean()
        cable.save()

        # Corrupt only the derived connector fields, not current membership or positions.
        Interface.objects.filter(pk__in=[near1.pk, near2.pk]).update(cable_connector=None)
        far_paths = {}
        for far in (far1, far2):
            far.refresh_from_db()
            far_paths[far.pk] = far._path_id
        for near in (near1, near2):
            near.refresh_from_db()
            near._path.delete()

        # Three members, so requesting the trigger leaves two co-origins for recovery to partition
        superseded = CablePath(
            path=[
                [utils.object_to_path_node(obj) for obj in (trigger, near1, near2)],
                [utils.object_to_path_node(trigger_cable)],
                [utils.object_to_path_node(trigger_far)],
            ],
            is_complete=True,
            is_active=True,
        )
        superseded.save()

        utils.create_cablepaths([Interface.objects.get(pk=trigger.pk)])

        self.assertFalse(CablePath.objects.filter(pk=superseded.pk).exists())
        self.assertCurrentPathExists((trigger, trigger_cable, trigger_far), is_complete=True, is_active=True)
        for near, far in ((near1, far1), (near2, far2)):
            self.assertCurrentPathExists((near, cable, far), is_complete=True, is_active=True)
        for far in (far1, far2):
            far.refresh_from_db()
            self.assertEqual(far._path_id, far_paths[far.pk], msg=f'{far} lost its original path')
        self.assertEqual(
            list(Interface.objects.filter(pk__in=[near1.pk, near2.pk]).values_list('cable_connector', flat=True)),
            [None, None],
        )

    def test_recovery_separates_co_origins_on_opposite_cable_ends(self):
        """
        Recovered co-origins split by cable end, while those sharing one end stay in a single group.
        """
        trigger, trigger_far = self._create_interfaces('Trigger', 'TriggerFar')
        near, far1, far2 = self._create_interfaces('Near', 'Far1', 'Far2')
        trigger_cable = Cable(a_terminations=[trigger], b_terminations=[trigger_far])
        trigger_cable.save()
        cable = Cable(a_terminations=[near], b_terminations=[far1, far2])
        cable.save()
        # far1 and far2 share one joint path, so deleting it clears the reference on both
        for origin in (near, far1):
            origin.refresh_from_db()
            origin._path.delete()

        # Both ends are left for recovery, with the far end holding two members
        superseded = CablePath(
            path=[
                [utils.object_to_path_node(obj) for obj in (trigger, near, far1, far2)],
                [utils.object_to_path_node(trigger_cable)],
                [utils.object_to_path_node(trigger_far)],
            ],
            is_complete=True,
            is_active=True,
        )
        superseded.save()

        utils.create_cablepaths([Interface.objects.get(pk=trigger.pk)])

        self.assertFalse(CablePath.objects.filter(pk=superseded.pk).exists())
        self.assertCurrentPathExists((trigger, trigger_cable, trigger_far), is_complete=True, is_active=True)
        self.assertCurrentPathExists((near, cable, [far1, far2]), is_complete=True, is_active=True)
        # The far end must not be split into one path per member
        joint = self.assertPathExists(([far1, far2], cable, near), is_complete=True, is_active=True)
        for far in (far1, far2):
            far.refresh_from_db()
            self.assertPathIsSet(far, joint)
        near_node = utils.object_to_path_node(near)
        for cable_path in CablePath.objects.all():
            self.assertFalse(
                near_node in cable_path.path[0] and len(cable_path.path[0]) > 1,
                msg=f'{cable_path} merged both ends',
            )
        self.assertEqual(CablePath.objects.count(), 4)

    def test_recovery_skips_a_co_origin_whose_cached_cable_drifted(self):
        """
        A co-origin whose cached cable disagrees with its row is left without a path, not traced.
        """
        trigger, trigger_far = self._create_interfaces('Trigger', 'TriggerFar')
        near, far1, far2 = self._create_interfaces('Near', 'Far1', 'Far2')
        other_a, other_b = self._create_interfaces('OtherA', 'OtherB')
        trigger_cable = Cable(a_terminations=[trigger], b_terminations=[trigger_far])
        trigger_cable.save()
        cable = Cable(a_terminations=[near], b_terminations=[far1, far2])
        cable.save()
        other = Cable(a_terminations=[other_a], b_terminations=[other_b])
        other.save()
        for origin in (near, far1):
            origin.refresh_from_db()
            origin._path.delete()

        # far2 keeps its termination row on the joint end while its cached cable points elsewhere
        Interface.objects.filter(pk=far2.pk).update(cable=other)

        superseded = CablePath(
            path=[
                [utils.object_to_path_node(obj) for obj in (trigger, far1, far2)],
                [utils.object_to_path_node(trigger_cable)],
                [utils.object_to_path_node(trigger_far)],
            ],
            is_complete=True,
            is_active=True,
        )
        superseded.save()

        # Tracing far2 from its stale cable would record a link that does not exist
        with (
            patch.object(CablePath, 'from_origin', wraps=CablePath.from_origin) as traced,
            self.assertLogs('netbox.dcim.utils', level='WARNING') as logs,
        ):
            utils.create_cablepaths([Interface.objects.get(pk=trigger.pk)])

        self.assertEqual([args.args[0] for args in traced.call_args_list if far2 in args.args[0]], [])
        far2.refresh_from_db()
        self.assertIsNone(far2._path_id)
        self.assertTrue(
            any(f'#{far2.pk}' in message and f'#{cable.pk}' in message for message in logs.output),
            msg=logs.output,
        )
        self.assertCurrentPathExists((trigger, trigger_cable, trigger_far), is_complete=True, is_active=True)
        self.assertPathExists(([far1], cable, near), is_complete=True, is_active=True)

    def test_recovery_skips_a_profiled_co_origin_whose_cached_end_drifted(self):
        """
        A profiled co-origin whose cached end disagrees with its row is left without a path, not traced.
        """
        trigger, trigger_far = self._create_interfaces('Trigger', 'TriggerFar')
        near1, near2, far1, far2 = self._create_interfaces('Near1', 'Near2', 'Far1', 'Far2')
        trigger_cable = Cable(a_terminations=[trigger], b_terminations=[trigger_far])
        trigger_cable.save()
        cable = Cable(
            profile=CableProfileChoices.TRUNK_2C1P,
            a_terminations=[near1, near2], b_terminations=[far1, far2],
        )
        cable.clean()
        cable.save()
        for origin in (near1, far1):
            origin.refresh_from_db()
            origin._path.delete()

        # far1's row still says B, but profiled peer lookup reads the cached end
        Interface.objects.filter(pk=far1.pk).update(cable_end=CableEndChoices.SIDE_A)

        superseded = CablePath(
            path=[
                [utils.object_to_path_node(obj) for obj in (trigger, near1, far1)],
                [utils.object_to_path_node(trigger_cable)],
                [utils.object_to_path_node(trigger_far)],
            ],
            is_complete=True,
            is_active=True,
        )
        superseded.save()

        # Tracing far1 from its stale end would resolve its own row as the peer
        with (
            patch.object(CablePath, 'from_origin', wraps=CablePath.from_origin) as traced,
            self.assertLogs('netbox.dcim.utils', level='WARNING') as logs,
        ):
            utils.create_cablepaths([Interface.objects.get(pk=trigger.pk)])

        self.assertEqual([args.args[0] for args in traced.call_args_list if far1 in args.args[0]], [])
        far1.refresh_from_db()
        self.assertIsNone(far1._path_id)
        self.assertEqual(far1.cable_end, CableEndChoices.SIDE_A)
        self.assertTrue(
            any(
                f'#{far1.pk}:' in message and f"end 'A' does not match termination cable #{cable.pk} end 'B'" in message
                for message in logs.output
            ),
            msg=logs.output,
        )
        self.assertCurrentPathExists((trigger, trigger_cable, trigger_far), is_complete=True, is_active=True)
        self.assertCurrentPathExists((near1, cable, far1), is_complete=True, is_active=True)

    def test_recovery_traces_an_unprofiled_co_origin_whose_cached_end_drifted(self):
        """
        Legacy tracing resolves the far end from the row, so an unprofiled co-origin with a drifted end is recovered.
        """
        trigger, trigger_far = self._create_interfaces('Trigger', 'TriggerFar')
        near, far1, far2 = self._create_interfaces('Near', 'Far1', 'Far2')
        trigger_cable = Cable(a_terminations=[trigger], b_terminations=[trigger_far])
        trigger_cable.save()
        cable = Cable(a_terminations=[near], b_terminations=[far1, far2])
        cable.save()
        for origin in (near, far1):
            origin.refresh_from_db()
            origin._path.delete()

        # far2's row still says B, which legacy tracing reads instead of the cached end
        Interface.objects.filter(pk=far2.pk).update(cable_end=CableEndChoices.SIDE_A)

        superseded = CablePath(
            path=[
                [utils.object_to_path_node(obj) for obj in (trigger, far1, far2)],
                [utils.object_to_path_node(trigger_cable)],
                [utils.object_to_path_node(trigger_far)],
            ],
            is_complete=True,
            is_active=True,
        )
        superseded.save()

        with (
            patch.object(CablePath, 'from_origin', wraps=CablePath.from_origin) as traced,
            self.assertNoLogs('netbox.dcim.utils', level='WARNING'),
        ):
            utils.create_cablepaths([Interface.objects.get(pk=trigger.pk)])

        self.assertIn([far1, far2], [args.args[0] for args in traced.call_args_list])
        path = self.assertPathExists(([far1, far2], cable, near), is_complete=True, is_active=True)
        far2.refresh_from_db()
        self.assertPathIsSet(far2, path)
        self.assertEqual(far2.cable_end, CableEndChoices.SIDE_A)

    def test_recovery_separates_profiled_co_origins_sharing_a_connector(self):
        """
        Opposite ends of a profiled cable share a connector number, so the end must still separate them.
        """
        trigger, trigger_far = self._create_interfaces('Trigger', 'TriggerFar')
        near1, near2, far1, far2 = self._create_interfaces('Near1', 'Near2', 'Far1', 'Far2')
        trigger_cable = Cable(a_terminations=[trigger], b_terminations=[trigger_far])
        trigger_cable.save()
        cable = Cable(
            profile=CableProfileChoices.TRUNK_2C1P,
            a_terminations=[near1, near2], b_terminations=[far1, far2],
        )
        cable.clean()
        cable.save()
        for origin in (near1, far1):
            origin.refresh_from_db()
            origin._path.delete()

        # near1 and far1 occupy connector 1 on opposite ends, which connector grouping alone cannot separate
        superseded = CablePath(
            path=[
                [utils.object_to_path_node(obj) for obj in (trigger, near1, far1)],
                [utils.object_to_path_node(trigger_cable)],
                [utils.object_to_path_node(trigger_far)],
            ],
            is_complete=True,
            is_active=True,
        )
        superseded.save()

        utils.create_cablepaths([Interface.objects.get(pk=trigger.pk)])

        self.assertFalse(CablePath.objects.filter(pk=superseded.pk).exists())
        self.assertCurrentPathExists((near1, cable, far1), is_complete=True, is_active=True)
        self.assertCurrentPathExists((far1, cable, near1), is_complete=True, is_active=True)
        co_origins = {utils.object_to_path_node(near1), utils.object_to_path_node(far1)}
        for cable_path in CablePath.objects.all():
            self.assertFalse(co_origins.issubset(cable_path.path[0]), msg=f'{cable_path} merged both ends')

    def test_rebuild_rejects_cached_link_drift_without_losing_candidates(self):
        far, first, second = self._create_interfaces('Far', 'First', 'Second')
        cable = Cable(a_terminations=[far], b_terminations=[first, second])
        cable.save()
        Interface.objects.filter(pk=first.pk).update(cable=None, cable_end=None)
        paths = list(CablePath.objects.order_by('pk').values_list('pk', 'path'))
        references = dict(Interface.objects.values_list('pk', '_path_id'))

        with self.assertRaisesMessage(UnsupportedCablePath, 'same link'):
            utils.rebuild_paths([cable])

        self.assertEqual(list(CablePath.objects.order_by('pk').values_list('pk', 'path')), paths)
        self.assertEqual(dict(Interface.objects.values_list('pk', '_path_id')), references)
        first.refresh_from_db()
        self.assertIsNone(first.cable_id)
        self.assertIsNone(first.cable_end)

    def test_origin_group_keeps_an_uncabled_object_as_a_singleton(self):
        origin, = self._create_interfaces('Detached')
        key, origins = next(iter(utils.get_cablepath_origin_groups([origin]).items()))
        self.assertEqual(key, utils.object_to_path_node(origin))
        self.assertEqual(list(origins), [origin])

    def test_empty_rebuild_does_not_query_the_database(self):
        with self.assertNumQueries(0):
            utils.rebuild_paths(iter(()))

    def test_rebuild_midspan_preserves_remote_joint_origins_and_unrelated_paths(self):
        far, first, second, other_a, other_b, partial = self._create_interfaces(
            'IF1', 'IF2', 'IF3', 'Unrelated A', 'Unrelated B', 'Partial'
        )
        fronts = [FrontPort.objects.create(device=self.device, name=f'FP{i}') for i in range(3)]
        rears = [RearPort.objects.create(device=self.device, name=f'RP{i}') for i in range(3)]
        for front, rear in zip(fronts, rears):
            PortMapping.objects.create(
                device=self.device,
                front_port=front, front_port_position=1,
                rear_port=rear, rear_port_position=1,
            )
        near_cable = Cable(a_terminations=[first, second], b_terminations=[fronts[0]])
        near_cable.save()
        far_cable = Cable(a_terminations=[fronts[1]], b_terminations=[far])
        far_cable.save()
        middle = Cable(a_terminations=[rears[0]], b_terminations=[rears[1]])
        middle.save()
        unrelated = Cable(a_terminations=[other_a], b_terminations=[other_b])
        unrelated.save()
        partial_cable = Cable(a_terminations=[partial], b_terminations=[fronts[2]])
        partial_cable.save()
        route = ([first, second], near_cable, fronts[0], rears[0], middle, rears[1], fronts[1], far_cable, far)
        joint = self.assertPathExists(route, is_complete=True)
        second.refresh_from_db()
        stale = CablePath.from_origin([second])
        stale.save()
        joint.save()
        preserved = {}
        for obj in (other_a, other_b, partial):
            obj.refresh_from_db()
            preserved[obj.pk] = obj._path_id

        utils.rebuild_paths([rears[0], fronts[1]])

        self.assertFalse(CablePath.objects.filter(pk=stale.pk).exists())
        joint = self.assertPathExists(route, is_complete=True, is_active=True)
        for obj in (first, second):
            obj.refresh_from_db()
            self.assertPathIsSet(obj, joint)
        self.assertCurrentPathExists(tuple(reversed(route)), is_complete=True, is_active=True)
        self.assertCurrentPathExists((other_a, unrelated, other_b), pk=preserved[other_a.pk], is_complete=True)
        self.assertCurrentPathExists((other_b, unrelated, other_a), pk=preserved[other_b.pk], is_complete=True)
        self.assertCurrentPathExists(
            (partial, partial_cable, fronts[2], rears[2]), pk=preserved[partial.pk], is_complete=False
        )
        self.assertEqual(CablePath.objects.count(), 5)

    def test_rebuild_preserves_channel_and_connector_origins(self):
        parent = Interface.objects.create(
            device=self.device, name='et0', type='100gbase-x-qsfp28', channels=4
        )
        channels = [
            Interface.objects.create(
                device=self.device, name=f'et0/{i}', type='channel', parent=parent, channel_id=i
            ) for i in range(1, 5)
        ]
        far = [
            Interface.objects.create(device=self.device, name=f'xe{i}', type='10gbase-x-sfpp') for i in range(4)
        ]
        cable = Cable(
            profile=CableProfileChoices.BREAKOUT_1C4P_4C1P,
            a_terminations=[parent], b_terminations=far,
        )
        cable.clean()
        cable.save()
        channels[0].refresh_from_db()
        key, origins = next(iter(utils.get_cablepath_origin_groups([channels[0]]).items()))
        self.assertEqual(key, utils.object_to_path_node(channels[0]))
        self.assertEqual(list(origins), [channels[0]])
        stale = CablePath(
            path=[
                [utils.object_to_path_node(obj) for obj in channels],
                [utils.object_to_path_node(cable)],
                [utils.object_to_path_node(obj) for obj in far],
            ],
            is_complete=True,
            is_active=True,
        )
        stale.save()

        utils.rebuild_paths([cable])

        self.assertFalse(CablePath.objects.filter(pk=stale.pk).exists())
        self.assertEqual(CablePath.objects.count(), 8)
        for channel, peer in zip(channels, far):
            self.assertCurrentPathExists((channel, cable, peer), is_complete=True, is_active=True)
            self.assertCurrentPathExists((peer, cable, channel), is_complete=True, is_active=True)
        parent.refresh_from_db()
        self.assertPathIsNotSet(parent)

    def test_rebuild_does_not_trace_an_unrelated_connector(self):
        near1, near2, far1, far2 = self._create_interfaces('Near1', 'Near2', 'Far1', 'Far2')
        fronts = [FrontPort.objects.create(device=self.device, name=f'FP{i}') for i in range(2)]
        rears = [RearPort.objects.create(device=self.device, name=f'RP{i}') for i in range(2)]
        for front, rear in zip(fronts, rears):
            PortMapping.objects.create(
                device=self.device, front_port=front, front_port_position=1,
                rear_port=rear, rear_port_position=1,
            )
        trunk = Cable(
            profile=CableProfileChoices.TRUNK_2C1P,
            a_terminations=[near1, near2], b_terminations=rears,
        )
        trunk.clean()
        trunk.save()
        drops = []
        for front, far in zip(fronts, (far1, far2)):
            cable = Cable(a_terminations=[front], b_terminations=[far])
            cable.save()
            drops.append(cable)
        affected_route = (near1, trunk, rears[0], fronts[0], drops[0], far1)
        other_route = (near2, trunk, rears[1], fronts[1], drops[1], far2)
        affected = {
            self.assertCurrentPathExists(affected_route, is_complete=True).pk,
            self.assertCurrentPathExists(tuple(reversed(affected_route)), is_complete=True).pk,
        }
        preserved = {
            near2.pk: self.assertCurrentPathExists(other_route, is_complete=True).pk,
            far2.pk: self.assertCurrentPathExists(tuple(reversed(other_route)), is_complete=True).pk,
        }
        trace = CablePath.from_origin

        def reject_unrelated_group(origins):
            if near2 in origins or far2 in origins:
                raise UnsupportedCablePath('The unrelated connector must not be traced')
            return trace(origins)

        with patch.object(CablePath, 'from_origin', side_effect=reject_unrelated_group) as traced:
            utils.rebuild_paths([fronts[0]])

        self.assertCountEqual(traced.call_args_list, [call([near1]), call([far1])])
        self.assertFalse(CablePath.objects.filter(pk__in=affected).exists())
        self.assertEqual(CablePath.objects.count(), 4)
        self.assertCurrentPathExists(affected_route, is_complete=True, is_active=True)
        self.assertCurrentPathExists(tuple(reversed(affected_route)), is_complete=True, is_active=True)
        self.assertCurrentPathExists(other_route, pk=preserved[near2.pk], is_complete=True, is_active=True)
        self.assertCurrentPathExists(
            tuple(reversed(other_route)), pk=preserved[far2.pk], is_complete=True, is_active=True
        )

    def test_rebuild_expands_a_historical_parent_before_selecting_groups(self):
        parent = Interface.objects.create(
            device=self.device, name='et0', type='100gbase-x-qsfp28', channels=2
        )
        channels = [
            Interface.objects.create(
                device=self.device, name=f'et0/{i}', type='channel', parent=parent, channel_id=i
            ) for i in range(1, 3)
        ]
        far = self._create_interfaces('Far1', 'Far2')
        cable = Cable(
            profile=CableProfileChoices.BREAKOUT_1C2P_2C1P, a_terminations=[parent], b_terminations=far,
        )
        cable.clean()
        cable.save()
        preserved = {}
        for channel, peer in zip(channels, far):
            peer.refresh_from_db()
            preserved[peer.pk] = peer._path_id
            channel.refresh_from_db()
            channel._path.delete()
        stale = CablePath(
            path=[
                [utils.object_to_path_node(parent)],
                [utils.object_to_path_node(cable)],
                [utils.object_to_path_node(peer) for peer in far],
            ],
            is_complete=True,
            is_active=True,
        )
        stale.save()
        self.assertEqual(list(CablePath.objects.filter(_nodes__contains=parent)), [stale])

        with patch.object(CablePath, 'from_origin', wraps=CablePath.from_origin) as traced:
            utils.rebuild_paths([parent])

        self.assertCountEqual(traced.call_args_list, [call([channels[0]]), call([channels[1]])])
        self.assertFalse(CablePath.objects.filter(pk=stale.pk).exists())
        self.assertEqual(CablePath.objects.count(), 4)
        parent.refresh_from_db()
        self.assertPathIsNotSet(parent)
        for channel, peer in zip(channels, far):
            self.assertCurrentPathExists((channel, cable, peer), is_complete=True, is_active=True)
            self.assertCurrentPathExists(
                (peer, cable, channel), pk=preserved[peer.pk], is_complete=True, is_active=True
            )

    def test_rebuild_keeps_requested_connectors_in_one_recovery_worklist(self):
        near1, near2, far1, far2, other1, other2 = self._create_interfaces(
            'Near1', 'Near2', 'Far1', 'Far2', 'Other1', 'Other2'
        )
        cable = Cable(
            profile=CableProfileChoices.TRUNK_2C1P,
            a_terminations=[near1, near2], b_terminations=[far1, far2],
        )
        cable.clean()
        cable.save()
        unrelated = Cable(a_terminations=[other1], b_terminations=[other2])
        unrelated.save()
        preserved = {
            obj.pk: self.assertCurrentPathExists((obj, unrelated, peer), is_complete=True).pk
            for obj, peer in ((other1, other2), (other2, other1))
        }
        # This historical hop is not a rebuild candidate: it records a different cable. Replacing the first
        # requested connector retires it and discovers the second, already-requested connector for recovery.
        stale = CablePath(
            path=[
                [utils.object_to_path_node(obj) for obj in (near1, near2)],
                [utils.object_to_path_node(unrelated)],
                [utils.object_to_path_node(obj) for obj in (far1, far2)],
            ],
            is_complete=True,
            is_active=True,
        )
        stale.save()
        self.assertFalse(CablePath.objects.filter(pk=stale.pk, _nodes__contains=cable).exists())

        with patch.object(CablePath, 'from_origin', wraps=CablePath.from_origin) as traced:
            utils.rebuild_paths([cable])

        self.assertCountEqual(traced.call_args_list, [call([obj]) for obj in (near1, near2, far1, far2)])
        self.assertFalse(CablePath.objects.filter(pk=stale.pk).exists())
        self.assertEqual(CablePath.objects.count(), 6)
        for near, far in ((near1, far1), (near2, far2)):
            self.assertCurrentPathExists((near, cable, far), is_complete=True, is_active=True)
            self.assertCurrentPathExists((far, cable, near), is_complete=True, is_active=True)
        for obj, peer in ((other1, other2), (other2, other1)):
            self.assertCurrentPathExists((obj, unrelated, peer), pk=preserved[obj.pk], is_complete=True)

    def test_origin_objects_are_fetched_once_per_content_type(self):
        far, *origins = self._create_interfaces('Far', *(f'IF{i}' for i in range(32)))
        cable = Cable(a_terminations=[far], b_terminations=origins)
        cable.save()
        nodes = [utils.object_to_path_node(obj) for obj in origins]
        # ContentType IDs are already cached by object_to_path_node().
        with self.assertNumQueries(1):
            objects = utils._get_cablepath_origin_objects(nodes)
            self.assertEqual([objects[node].link for node in nodes], [cable] * len(nodes))
        self.assertEqual([objects[node] for node in nodes], origins)

    def test_current_groups_are_resolved_in_bulk(self):
        far, *origins = self._create_interfaces('Far', *(f'IF{i}' for i in range(16)))
        cable = Cable(a_terminations=[far], b_terminations=origins)
        cable.save()
        ContentType.objects.get_for_model(Interface)

        # Membership, end rows, generic targets, and cables are fetched in batches, not per origin.
        with self.assertNumQueries(4):
            groups = utils.get_cablepath_origin_groups(origins)
        self.assertEqual(groups, {(cable.pk, CableEndChoices.SIDE_B): origins})

    def test_known_cable_ends_are_loaded_together(self):
        far, first, second = self._create_interfaces('IF1', 'IF2', 'IF3')
        cable = Cable(a_terminations=[far], b_terminations=[first, second])
        cable.save()
        ContentType.objects.get_for_model(Interface)
        keys = [(cable.pk, CableEndChoices.SIDE_A), (cable.pk, CableEndChoices.SIDE_B)]
        with self.assertNumQueries(3):
            groups = utils.get_cable_end_terminations(keys)
        self.assertEqual(groups, {keys[0]: [far], keys[1]: [first, second]})
        with self.assertNumQueries(0):
            self.assertEqual([obj.cable for group in groups.values() for obj in group], [cable] * 3)

    def test_bulk_end_lookup_does_not_include_the_opposite_ends(self):
        first_a, first_b, second_a, second_b = self._create_interfaces('IF1', 'IF2', 'IF3', 'IF4')
        first = Cable(a_terminations=[first_a], b_terminations=[first_b])
        first.save()
        second = Cable(a_terminations=[second_a], b_terminations=[second_b])
        second.save()
        first_key = (first.pk, CableEndChoices.SIDE_A)
        second_key = (second.pk, CableEndChoices.SIDE_B)
        groups = utils.get_cable_end_terminations([first_key, second_key])
        self.assertEqual(groups, {first_key: [first_a], second_key: [second_b]})

    def test_empty_origin_lookups_do_not_query_the_database(self):
        with self.assertNumQueries(0):
            self.assertEqual(utils._get_cablepath_origin_objects([]), {})
            self.assertEqual(utils.get_cable_end_terminations([]), {})
            self.assertEqual(utils.get_cablepath_origin_groups([]), {})

    def test_missing_generic_target_is_ignored_when_retracing_a_cable_end(self):
        far, origin = self._create_interfaces('IF1', 'IF2')
        cable = Cable(a_terminations=[far], b_terminations=[origin])
        cable.save()
        origin.refresh_from_db()
        origin._path.delete()
        key = (cable.pk, CableEndChoices.SIDE_B)

        # Bypass save-time validation to represent a stale generic reference, without deleting a live endpoint.
        missing_id = Interface.objects.order_by('-pk').values_list('pk', flat=True).first() + 1
        orphan = CableTermination(
            cable=cable,
            cable_end=CableEndChoices.SIDE_B,
            termination_type=ContentType.objects.get_for_model(Interface),
            termination_id=missing_id,
        )
        CableTermination.objects.bulk_create([orphan])
        self.assertIsNone(CableTermination.objects.get(pk=orphan.pk).termination)
        self.assertEqual(utils.get_cable_end_terminations([key]), {key: [origin]})

        out, err = StringIO(), StringIO()
        call_command('trace_paths', stdout=out, stderr=err, no_input=True)

        self.assertCurrentPathExists((origin, cable, far), is_complete=True, is_active=True)
        self.assertEqual(CablePath.objects.count(), 2)
        self.assertIn('Finished.', out.getvalue())
        self.assertEqual(err.getvalue(), '')
        # Tracing tolerates the dangling reference and does not silently delete the CableTermination row.
        self.assertTrue(CableTermination.objects.filter(pk=orphan.pk).exists())

    def test_cable_prefetch_traverses_different_generic_target_types(self):
        far, origin = self._create_interfaces('IF1', 'IF2')
        cable = Cable(a_terminations=[far], b_terminations=[origin])
        cable.save()
        console = ConsolePort.objects.create(device=self.device, name='Console')
        server = ConsoleServerPort.objects.create(device=self.device, name='Console server')
        console_cable = Cable(a_terminations=[console], b_terminations=[server])
        console_cable.save()
        keys = [(cable.pk, CableEndChoices.SIDE_B), (console_cable.pk, CableEndChoices.SIDE_A)]
        for model in (Interface, ConsolePort):
            ContentType.objects.get_for_model(model)

        # End rows, two generic target types, then their shared cable relation: no per-origin queries.
        with self.assertNumQueries(4):
            groups = utils.get_cable_end_terminations(keys)
        self.assertEqual(groups, {keys[0]: [origin], keys[1]: [console]})
        with self.assertNumQueries(0):
            self.assertEqual(
                [obj.cable for key in keys for obj in groups[key]], [cable, console_cable]
            )


class TracePathsRecoveryTestCase(BaseCablePathTestCase):

    def test_progress_bar_updates_for_an_already_retraced_cable_end(self):
        class FakeQuerySet(list):
            def filter(self, *args, **kwargs):
                return self

            def count(self):
                return len(self)

            def annotate(self, **kwargs):
                return self

            def order_by(self, *fields):
                return self

            def iterator(self, chunk_size):
                return iter(self)

        endpoint = SimpleNamespace(pk=1, cable_id=1, _trace_cable_id=1, _trace_cable_end='B')
        origins = FakeQuerySet([endpoint] * 200)
        model = SimpleNamespace(
            objects=SimpleNamespace(filter=lambda *args, **kwargs: origins),
            _meta=SimpleNamespace(verbose_name='interface', verbose_name_plural='interfaces'),
        )
        command = trace_paths.Command(stdout=StringIO())
        with (
            patch.object(trace_paths, 'ENDPOINT_MODELS', (model,)),
            patch.object(trace_paths, 'get_cable_end_terminations', return_value={(1, 'B'): [endpoint]}) as fetch,
            patch.object(trace_paths, 'create_cablepaths') as create,
            patch.object(command, 'draw_progress_bar') as progress,
        ):
            command.handle(force=False, no_input=True)

        create.assert_called_once_with([endpoint])
        fetch.assert_called_once_with([(1, 'B')])
        self.assertEqual(progress.call_args_list, [call(50), call(100), call(100)])

    def test_group_batches_preserve_counts_progress_and_singleton_fallbacks(self):
        class FakeQuerySet(list):
            def filter(self, *args, **kwargs):
                return self

            def count(self):
                return len(self)

            def annotate(self, **kwargs):
                return self

            def order_by(self, *fields):
                return self

            def iterator(self, chunk_size):
                return iter(self)

        origins = FakeQuerySet()
        memberships = {}
        # More than one batch, and a group spanning a progress boundary. Counts must survive buffering.
        for cable_id in range(1, trace_paths.ORIGIN_GROUP_BATCH_SIZE + 3):
            members = [
                SimpleNamespace(
                    pk=len(origins) + offset, _trace_cable_id=cable_id, _trace_cable_end='B'
                ) for offset in range(1, 102 if cable_id == 1 else 2)
            ]
            origins.extend(members)
            memberships[(cable_id, 'B')] = members
        fallbacks = [
            SimpleNamespace(pk=len(origins) + offset, _trace_cable_id=None, _trace_cable_end=None)
            for offset in (1, 2)
        ]
        origins.extend(fallbacks)
        model = SimpleNamespace(
            objects=SimpleNamespace(filter=lambda *args, **kwargs: origins),
            _meta=SimpleNamespace(verbose_name='interface', verbose_name_plural='interfaces'),
        )
        out, err = StringIO(), StringIO()
        command = trace_paths.Command(stdout=out, stderr=err)
        failed_key = (trace_paths.ORIGIN_GROUP_BATCH_SIZE, 'B')

        def fetch_memberships(keys):
            return {key: memberships[key] for key in keys}

        def trace_group(group):
            if group is memberships[failed_key]:
                raise UnsupportedCablePath('Simulated group failure')

        with (
            patch.object(trace_paths, 'ENDPOINT_MODELS', (model,)),
            patch.object(trace_paths, 'get_cable_end_terminations', side_effect=fetch_memberships) as fetch,
            patch.object(trace_paths, 'create_cablepaths', side_effect=trace_group) as trace,
            patch.object(command, 'draw_progress_bar') as progress,
        ):
            with self.assertRaisesMessage(CommandError, 'Unable to trace 1 origin group(s)'):
                command.handle(force=False, no_input=True)

        keys = list(memberships)
        self.assertEqual(fetch.call_args_list, [
            call(keys[:trace_paths.ORIGIN_GROUP_BATCH_SIZE]), call(keys[trace_paths.ORIGIN_GROUP_BATCH_SIZE:]),
        ])
        self.assertEqual(trace.call_args_list, [
            *[call(members) for members in memberships.values()], call([fallbacks[0]]), call([fallbacks[1]]),
        ])
        self.assertEqual(progress.call_args_list, [
            *[call(count * 100 / len(origins)) for count in range(100, len(origins) + 1, 100)], call(100),
        ])
        self.assertIn(f'Retraced {len(origins) - 1} interfaces', out.getvalue())
        self.assertIn('Failed to retrace 1 selected interfaces in 1 origin group(s)', out.getvalue())
        self.assertNotIn('Finished.', out.getvalue())
        self.assertEqual(err.getvalue().count('Unable to trace'), 1)

    def test_batched_end_lookup_continues_real_repairs_after_a_failed_group(self):
        groups = []
        for index, names in enumerate((('A1', 'A2', 'Drifted'), ('B1', 'B2'), ('C1',))):
            far = Interface.objects.create(device=self.device, name=f'Far{index}')
            origins = [Interface.objects.create(device=self.device, name=name) for name in names]
            cable = Cable(a_terminations=[far], b_terminations=origins)
            cable.save()
            origins[0].refresh_from_db()
            origins[0]._path.delete()
            groups.append((cable, far, origins))
        bad, _, bad_origins = groups[0]
        Interface.objects.filter(pk=bad_origins[-1].pk).update(cable=None)
        out, err = StringIO(), StringIO()

        with (
            patch.object(trace_paths, 'ENDPOINT_MODELS', (Interface,)),
            patch.object(trace_paths, 'ORIGIN_GROUP_BATCH_SIZE', 2),
            patch.object(trace_paths, 'get_cable_end_terminations', wraps=utils.get_cable_end_terminations) as fetch,
        ):
            with self.assertRaisesMessage(CommandError, 'Unable to trace 1 origin group(s)'):
                call_command('trace_paths', no_input=True, stdout=out, stderr=err)

        keys = [(cable.pk, CableEndChoices.SIDE_B) for cable, _, _ in groups]
        self.assertEqual(fetch.call_args_list, [call(keys[:2]), call(keys[2:])])
        self.assertEqual(err.getvalue().count(f'Unable to trace cable #{bad.pk} end B:'), 1)
        self.assertIn('Retraced 3 interfaces', out.getvalue())
        self.assertIn('Failed to retrace 2 selected interfaces in 1 origin group(s)', out.getvalue())
        self.assertNotIn('Finished.', out.getvalue())
        for cable, far, origins in groups[1:]:
            path = self.assertPathExists((origins, cable, far), is_complete=True, is_active=True)
            for origin in origins:
                origin.refresh_from_db()
                self.assertPathIsSet(origin, path)
            self.assertCurrentPathExists((far, cable, origins), is_complete=True, is_active=True)
        for origin in bad_origins:
            origin.refresh_from_db()
            self.assertPathIsNotSet(origin)
        self.assertEqual(CablePath.objects.count(), 5)

    def test_empty_resolved_end_is_reported_without_preventing_later_repairs(self):
        missing, missing_peer, good, good_peer = [
            Interface.objects.create(device=self.device, name=name)
            for name in ('Missing', 'Missing peer', 'Good', 'Good peer')
        ]
        missing_cable = Cable(a_terminations=[missing], b_terminations=[missing_peer])
        missing_cable.save()
        good_cable = Cable(a_terminations=[good], b_terminations=[good_peer])
        good_cable.save()
        Interface.objects.filter(pk__in=[missing.pk, good.pk]).update(_path=None)
        missing_key = (missing_cable.pk, CableEndChoices.SIDE_A)
        out, err = StringIO(), StringIO()
        fetch_ends = utils.get_cable_end_terminations

        def lose_membership(keys):
            groups = fetch_ends(keys)
            # Simulate membership disappearing between endpoint selection and the batched end lookup.
            if missing_key in groups:
                groups[missing_key] = []
            return groups

        with (
            patch.object(trace_paths, 'ENDPOINT_MODELS', (Interface,)),
            patch.object(trace_paths, 'get_cable_end_terminations', side_effect=lose_membership),
            patch.object(trace_paths, 'create_cablepaths', wraps=utils.create_cablepaths) as traced,
        ):
            with self.assertRaisesMessage(CommandError, 'Unable to trace 1 origin group(s)'):
                call_command('trace_paths', no_input=True, stdout=out, stderr=err)

        traced.assert_called_once_with([good])
        self.assertIn(f'Unable to trace cable #{missing_cable.pk} end A:', err.getvalue())
        self.assertIn('No current terminations remain', err.getvalue())
        self.assertIn('Retraced 1 interfaces', out.getvalue())
        self.assertIn('Failed to retrace 1 selected interfaces in 1 origin group(s)', out.getvalue())
        self.assertIn('100%', out.getvalue())
        self.assertNotIn('Finished.', out.getvalue())
        missing.refresh_from_db()
        self.assertPathIsNotSet(missing)
        self.assertCurrentPathExists((good, good_cable, good_peer), is_complete=True)
        self.assertCurrentPathExists((good_peer, good_cable, good), is_complete=True)

    def test_unsupported_group_does_not_prevent_later_repairs(self):
        for force in (False, True):
            with self.subTest(force=force), transaction.atomic():
                bad_far, first, second, drifted, good_a, good_b = [
                    Interface.objects.create(device=self.device, name=name)
                    for name in ('A0', 'A1', 'A2', 'A3', 'Z0', 'Z1')
                ]
                bad = Cable(a_terminations=[bad_far], b_terminations=[first, second, drifted])
                bad.save()
                good = Cable(a_terminations=[good_a], b_terminations=[good_b])
                good.save()
                # The CableTermination survives, so grouping the selected siblings exposes this cached-FK drift.
                Interface.objects.filter(pk=drifted.pk).update(cable=None)
                Interface.objects.filter(pk__in=[first.pk, second.pk, good_a.pk]).update(_path=None)
                before_refs = dict(Interface.objects.filter(
                    pk__in=[first.pk, second.pk, drifted.pk]
                ).values_list('pk', '_path_id'))
                before_paths = set(CablePath.objects.filter(_nodes__contains=bad).values_list('pk', flat=True))
                out, err = StringIO(), StringIO()
                create = utils.create_cablepaths
                attempts = []

                def record_attempt(origins):
                    attempts.append(tuple(obj.pk for obj in origins))
                    return create(origins)

                with patch.object(trace_paths, 'create_cablepaths', side_effect=record_attempt):
                    with self.assertRaisesMessage(CommandError, 'Unable to trace 1 origin group(s)'):
                        call_command('trace_paths', force=force, no_input=True, stdout=out, stderr=err)

                failed_group = (first.pk, second.pk, drifted.pk)
                self.assertEqual(attempts.count(failed_group), 1)
                self.assertLess(attempts.index(failed_group), attempts.index((good_a.pk,)))
                self.assertEqual(err.getvalue().count(f'Unable to trace cable #{bad.pk} end B:'), 1)
                self.assertNotIn('Finished.', out.getvalue())
                self.assertCurrentPathExists((good_a, good, good_b), is_complete=True)
                self.assertCurrentPathExists((good_b, good, good_a), is_complete=True)
                if force:
                    # --force's earlier global deletion is deliberately not restored by a failed group.
                    for obj in (first, second, drifted):
                        obj.refresh_from_db()
                        self.assertPathIsNotSet(obj)
                else:
                    self.assertEqual(
                        set(CablePath.objects.filter(_nodes__contains=bad).values_list('pk', flat=True)), before_paths
                    )
                    for obj in (first, second, drifted):
                        obj.refresh_from_db()
                        self.assertEqual(obj._path_id, before_refs[obj.pk])
                    self.assertEqual(CablePath.objects.count(), 4)
                transaction.set_rollback(True)

    def test_force_rebuild_removes_stale_rows_and_preserves_the_joint_hop(self):
        far, first, second = [
            Interface.objects.create(device=self.device, name=f'IF{i}') for i in range(3)
        ]
        cable = Cable(a_terminations=[far], b_terminations=[first, second])
        cable.save()
        second.refresh_from_db()
        CablePath.from_origin([second]).save()
        self.assertEqual(CablePath.objects.count(), 3)
        out = StringIO()

        call_command('trace_paths', force=True, no_input=True, stdout=out)

        self.assertIn('Finished.', out.getvalue())
        self.assertEqual(CablePath.objects.count(), 2)
        self.assertCurrentPathExists((far, cable, [first, second]), is_complete=True)
        joint = self.assertPathExists(([first, second], cable, far), is_complete=True)
        for origin in (first, second):
            origin.refresh_from_db()
            self.assertPathIsSet(origin, joint)
