from dcim.choices import CableProfileChoices
from dcim.models import *
from dcim.svg import CableTraceSVG
from dcim.tests.utils import CablePathTestCase


class CablePathTests(CablePathTestCase):
    """
    Test the creation of CablePaths for Cables with different profiles applied.

    Tests are numbered as follows:
        1XX: Test direct connections using each profile
    """

    def test_101_cable_profile_straight_single(self):
        """
        [IF1] --C1-- [IF2]

        Cable profile: Straight single
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
        ]

        # Create cable 1
        cable1 = Cable(
            profile=CableProfileChoices.STRAIGHT_SINGLE,
            a_terminations=[interfaces[0]],
            b_terminations=[interfaces[1]],
        )
        cable1.clean()
        cable1.save()

        path1 = self.assertPathExists(
            (interfaces[0], cable1, interfaces[1]),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            (interfaces[1], cable1, interfaces[0]),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 2)
        interfaces[0].refresh_from_db()
        interfaces[1].refresh_from_db()
        self.assertPathIsSet(interfaces[0], path1)
        self.assertPathIsSet(interfaces[1], path2)
        self.assertEqual(interfaces[0].cable_position, 1)
        self.assertEqual(interfaces[1].cable_position, 1)

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_102_cable_profile_straight_multi(self):
        """
        [IF1] --C1-- [IF3]
        [IF2]        [IF4]

        Cable profile: Straight multi
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
            Interface.objects.create(device=self.device, name='Interface 3'),
            Interface.objects.create(device=self.device, name='Interface 4'),
        ]

        # Create cable 1
        cable1 = Cable(
            profile=CableProfileChoices.STRAIGHT_MULTI,
            a_terminations=[interfaces[0], interfaces[1]],
            b_terminations=[interfaces[2], interfaces[3]],
        )
        cable1.clean()
        cable1.save()

        path1 = self.assertPathExists(
            (interfaces[0], cable1, interfaces[2]),
            is_complete=True,
            is_active=True
        )
        path2 = self.assertPathExists(
            (interfaces[1], cable1, interfaces[3]),
            is_complete=True,
            is_active=True
        )
        path3 = self.assertPathExists(
            (interfaces[2], cable1, interfaces[0]),
            is_complete=True,
            is_active=True
        )
        path4 = self.assertPathExists(
            (interfaces[3], cable1, interfaces[1]),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        for interface in interfaces:
            interface.refresh_from_db()
        self.assertPathIsSet(interfaces[0], path1)
        self.assertPathIsSet(interfaces[1], path2)
        self.assertPathIsSet(interfaces[2], path3)
        self.assertPathIsSet(interfaces[3], path4)
        self.assertEqual(interfaces[0].cable_position, 1)
        self.assertEqual(interfaces[1].cable_position, 2)
        self.assertEqual(interfaces[2].cable_position, 1)
        self.assertEqual(interfaces[3].cable_position, 2)

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_103_cable_profile_a_to_many(self):
        """
        [IF1] --C1-- [IF2]
                     [IF3]
                     [IF4]

        Cable profile: A to many
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
            Interface.objects.create(device=self.device, name='Interface 3'),
            Interface.objects.create(device=self.device, name='Interface 4'),
        ]

        # Create cable 1
        cable1 = Cable(
            profile=CableProfileChoices.A_TO_MANY,
            a_terminations=[interfaces[0]],
            b_terminations=[interfaces[1], interfaces[2], interfaces[3]],
        )
        cable1.clean()
        cable1.save()

        # A-to-B path leads to all interfaces
        path1 = self.assertPathExists(
            (interfaces[0], cable1, [interfaces[1], interfaces[2], interfaces[3]]),
            is_complete=True,
            is_active=True
        )
        # B-to-A paths are incomplete because A side has null position
        path2 = self.assertPathExists(
            (interfaces[1], cable1, []),
            is_complete=False,
            is_active=True
        )
        path3 = self.assertPathExists(
            (interfaces[2], cable1, []),
            is_complete=False,
            is_active=True
        )
        path4 = self.assertPathExists(
            (interfaces[3], cable1, []),
            is_complete=False,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        for interface in interfaces:
            interface.refresh_from_db()
        self.assertPathIsSet(interfaces[0], path1)
        self.assertPathIsSet(interfaces[1], path2)
        self.assertPathIsSet(interfaces[2], path3)
        self.assertPathIsSet(interfaces[3], path4)
        self.assertIsNone(interfaces[0].cable_position)
        self.assertEqual(interfaces[1].cable_position, 1)
        self.assertEqual(interfaces[2].cable_position, 2)
        self.assertEqual(interfaces[3].cable_position, 3)

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_104_cable_profile_b_to_many(self):
        """
        [IF1] --C1-- [IF4]
        [IF2]
        [IF3]

        Cable profile: B to many
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1'),
            Interface.objects.create(device=self.device, name='Interface 2'),
            Interface.objects.create(device=self.device, name='Interface 3'),
            Interface.objects.create(device=self.device, name='Interface 4'),
        ]

        # Create cable 1
        cable1 = Cable(
            profile=CableProfileChoices.B_TO_MANY,
            a_terminations=[interfaces[0], interfaces[1], interfaces[2]],
            b_terminations=[interfaces[3]],
        )
        cable1.clean()
        cable1.save()

        # A-to-B paths are incomplete because A side has null position
        path1 = self.assertPathExists(
            (interfaces[0], cable1, []),
            is_complete=False,
            is_active=True
        )
        path2 = self.assertPathExists(
            (interfaces[1], cable1, []),
            is_complete=False,
            is_active=True
        )
        path3 = self.assertPathExists(
            (interfaces[2], cable1, []),
            is_complete=False,
            is_active=True
        )
        # B-to-A path leads to all interfaces
        path4 = self.assertPathExists(
            (interfaces[3], cable1, [interfaces[0], interfaces[1], interfaces[2]]),
            is_complete=True,
            is_active=True
        )
        self.assertEqual(CablePath.objects.count(), 4)

        for interface in interfaces:
            interface.refresh_from_db()
        self.assertPathIsSet(interfaces[0], path1)
        self.assertPathIsSet(interfaces[1], path2)
        self.assertPathIsSet(interfaces[2], path3)
        self.assertPathIsSet(interfaces[3], path4)
        self.assertEqual(interfaces[0].cable_position, 1)
        self.assertEqual(interfaces[1].cable_position, 2)
        self.assertEqual(interfaces[2].cable_position, 3)
        self.assertIsNone(interfaces[3].cable_position)

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)

    def test_105_cable_profile_2x2_mpo(self):
        """
        [IF1:1] --C1-- [IF3:1]
        [IF1:2]        [IF3:2]
        [IF1:3]        [IF3:3]
        [IF1:4]        [IF3:4]
        [IF2:1]        [IF4:1]
        [IF2:2]        [IF4:2]
        [IF2:3]        [IF4:3]
        [IF2:4]        [IF4:4]

        Cable profile: Shuffle (2x2 MPO)
        """
        interfaces = [
            Interface.objects.create(device=self.device, name='Interface 1:1'),
            Interface.objects.create(device=self.device, name='Interface 1:2'),
            Interface.objects.create(device=self.device, name='Interface 1:3'),
            Interface.objects.create(device=self.device, name='Interface 1:4'),
            Interface.objects.create(device=self.device, name='Interface 2:1'),
            Interface.objects.create(device=self.device, name='Interface 2:2'),
            Interface.objects.create(device=self.device, name='Interface 2:3'),
            Interface.objects.create(device=self.device, name='Interface 2:4'),
            Interface.objects.create(device=self.device, name='Interface 3:1'),
            Interface.objects.create(device=self.device, name='Interface 3:2'),
            Interface.objects.create(device=self.device, name='Interface 3:3'),
            Interface.objects.create(device=self.device, name='Interface 3:4'),
            Interface.objects.create(device=self.device, name='Interface 4:1'),
            Interface.objects.create(device=self.device, name='Interface 4:2'),
            Interface.objects.create(device=self.device, name='Interface 4:3'),
            Interface.objects.create(device=self.device, name='Interface 4:4'),
        ]

        # Create cable 1
        cable1 = Cable(
            profile=CableProfileChoices.SHUFFLE_2X2_MPO,
            a_terminations=interfaces[0:8],
            b_terminations=interfaces[8:16],
        )
        cable1.clean()
        cable1.save()

        paths = [
            # A-to-B paths
            self.assertPathExists(
                (interfaces[0], cable1, interfaces[8]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[1], cable1, interfaces[9]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[2], cable1, interfaces[12]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[3], cable1, interfaces[13]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[4], cable1, interfaces[10]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[5], cable1, interfaces[11]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[6], cable1, interfaces[14]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[7], cable1, interfaces[15]), is_complete=True, is_active=True
            ),
            # B-to-A paths
            self.assertPathExists(
                (interfaces[8], cable1, interfaces[0]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[9], cable1, interfaces[1]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[10], cable1, interfaces[4]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[11], cable1, interfaces[5]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[12], cable1, interfaces[2]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[13], cable1, interfaces[3]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[14], cable1, interfaces[6]), is_complete=True, is_active=True
            ),
            self.assertPathExists(
                (interfaces[15], cable1, interfaces[7]), is_complete=True, is_active=True
            ),
        ]
        self.assertEqual(CablePath.objects.count(), len(paths))

        for i, (interface, path) in enumerate(zip(interfaces, paths)):
            interface.refresh_from_db()
            self.assertPathIsSet(interface, path)
            self.assertEqual(interface.cable_end, 'A' if i < 8 else 'B')
            self.assertEqual(interface.cable_position, (i % 8) + 1)

        # Test SVG generation
        CableTraceSVG(interfaces[0]).render()

        # Delete cable 1
        cable1.delete()

        # Check that all CablePaths have been deleted
        self.assertEqual(CablePath.objects.count(), 0)
