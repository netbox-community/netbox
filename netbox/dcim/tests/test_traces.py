from django.test import TestCase

from circuits.choices import CircuitTerminationSideChoices
from circuits.models import Circuit, CircuitTermination, CircuitType, Provider
from dcim.choices import *
from dcim.models import *


class TraceTestCase(TestCase):

    def setUp(self):
        """
        This builds quite a convoluted connection between two routers to try and cover all the edge cases that might
        go wrong, such as mixing up Front/RearPorts on a single device. We therefore loop the path through the same
        patch panel's ports multiple times.

                                    +-------------------------------------------------------------------+
                                    |                                                                   |
                                    |   +-----------------------------------------------------------+   |
                                    |   |                                                           |   |
                                    |   |   +------------------------+                              |   |
                                    |   |   |                        |                              |   |
        +---------------------+     |   |   |  +------------------+  |                              |   |
        |       Router1       |     |   |   |  |      Panel1      |  |                              |   |
        |                     |     |   |   |  |                  |  |                              |   |
        | +-----------------+ |     |   |   |  | +-----+  +-----+ |  |                              |   |
        | | SomeEthernet1/0 +--------------------+ RP1 +--+ FP1 +----+       +-------------------+  |   |
        | +-----------------+ |     |   |   |  | +-----+  +-----+ |          |       MUX1        |  |   |
        |                     |     |   |   |  |                  |          |                   |  |   |
        | +-----------------+ |     |   |   |  | +-----+  +-----+ |          | +-----+           |  |   |
        | | SomeEthernet1/1 | |     |   |   +----+ RP2 +--+ FP2 +--------------+ CH1 +----+      |  |   |
        | +-----------------+ |     |   |      | +-----+  +-----+ |          | +-----+  +------+ |  |   |
        |                     |     |   |      |                  |          |          | DWDM +----+   |
        +---------------------+     |   |      | +-----+  +-----+ |          | +-----+  +------+ |      |
                                    |   +--------+ RP3 +--+ FP3 +--------+   | | CH2 +----+      |      |
                                    |          | +-----+  +-----+ |      |   | +-----+           |      |
                                    |          |                  |      |   |                   |      |
                                    |          | +-----+  +-----+ |      |   +-------------------+      |
                                    +------------+ RP4 +--+ FP4 +----+   |                              |
                                               | +-----+  +-----+ |  |   |   +-------------------+      |
                                               |                  |  |   |   |       MUX2        |      |
                                               +------------------+  |   |   |                   |      |
                                                                     |   |   | +-----+           |      |
                                                                     |   |   | | CH1 +----+      |      |
                                                                     |   |   | +-----+  +------+ |      |
                                                                     |   |   |          | DWDM +--------+
                                                                     |   |   | +-----+  +------+ |
                                                                     |   +-----+ CH2 +----+      |
                                                                     |       | +-----+           |
                                                                     |       |                   |
                          +------------------------------------------+       +-------------------+
                          |
                          |
                          |                                                       +---------------------+
                          |                                                       |       Router2       |
                          |                                                       |                     |
                          |                                                       | +-----------------+ |
                          |                                                       | | SomeEthernet2/0 | |
                          |                       +-------------------+           | +-----------------+ |
                          |                       |       MUX3        |           |                     |
                          |  +--------------+     |                   |           | +-----------------+ |
                          |  |   Circuit1   |     |           +-----+ |      +------+ SomeEthernet2/1 | |
                          |  |              |     |      +----+ CH1 | |      |    | +-----------------+ |
                          |  | +---+  +---+ |     | +------+  +-----+ |      |    |                     |
                          +----+ A |  | Z +---------+ DWDM |          |      |    +---------------------+
                             | +---+  +---+ |     | +------+  +-----+ |      |
                             |              |     |      +----+ CH2 +----+   |
                             +--------------+     |           +-----+ |  |   |
                                                  |                   |  |   |
                                                  +-------------------+  |   |
                                                                         |   |
                                               +-------------------------+   |
                                               |                             |
                                               |  +-------------------+      |
                                               |  |       MUX4        |      |
                                               |  |                   |      |
                                               |  |           +-----+ |      |
                                               |  |      +----+ CH1 +--------+
                                               |  | +------+  +-----+ |
                                               +----+ DWDM |          |
                                                  | +------+  +-----+ |
                                                  |      +----+ CH2 | |
                                                  |           +-----+ |
                                                  |                   |
                                                  +-------------------+
        """
        self.site = Site.objects.create(
            name='TestSite',
            slug='test-site'
        )

        self.manufacturer = Manufacturer.objects.create(
            name='Acme',
            slug='acme'
        )

        self.device_type = {
            'router': DeviceType.objects.create(
                manufacturer=self.manufacturer,
                model='ManyASIC 128',
                slug='manyasic128'
            ),
            'patch': DeviceType.objects.create(
                manufacturer=self.manufacturer,
                model='LotsOfPorts 12',
                slug='lotsofports12'
            ),
            'mux': DeviceType.objects.create(
                manufacturer=self.manufacturer,
                model='ManyLotsDWDM 8',
                slug='manylotsdwdm8'
            ),
        }

        self.device_role = {
            'router': DeviceRole.objects.create(
                name='Router',
                slug='router',
            ),
            'patch': DeviceRole.objects.create(
                name='Patch panel',
                slug='patch-panel',
            ),
            'mux': DeviceRole.objects.create(
                name='MUX',
                slug='mux',
            ),
        }

        # Two routers
        self.router = {}
        self.router_interface = {}
        for router_nr in (1, 2):
            self.router[router_nr] = Device.objects.create(
                name='Router{}'.format(router_nr),
                site=self.site,
                device_type=self.device_type['router'],
                device_role=self.device_role['router']
            )
            self.router_interface[router_nr] = {}
            for intf_nr in (0, 1):
                self.router_interface[router_nr][intf_nr] = Interface.objects.create(
                    device=self.router[router_nr],
                    name='SomeEthernet{}/{}'.format(router_nr, intf_nr),
                    type=InterfaceTypeChoices.TYPE_1GE_FIXED
                )

        # Patch panels with 1-on-1 mapping
        self.patch = {}
        self.patch_fp = {}
        self.patch_rp = {}
        for patch_nr in (1,):
            self.patch[patch_nr] = Device.objects.create(
                name="Panel{}".format(patch_nr),
                site=self.site,
                device_type=self.device_type['patch'],
                device_role=self.device_role['patch'],
            )
            self.patch_rp[patch_nr] = {}
            self.patch_fp[patch_nr] = {}
            for port_nr in (1, 2, 3, 4):
                self.patch_rp[patch_nr][port_nr] = RearPort.objects.create(
                    device=self.patch[patch_nr],
                    name="Panel{} RP{}".format(patch_nr, port_nr),
                    type=PortTypeChoices.TYPE_SC,
                    positions=1
                )
                self.patch_fp[patch_nr][port_nr] = FrontPort.objects.create(
                    device=self.patch[patch_nr],
                    name="Panel{} FP{}".format(patch_nr, port_nr),
                    type=PortTypeChoices.TYPE_SC,
                    rear_port=self.patch_rp[patch_nr][port_nr],
                    rear_port_position=1
                )

        # DWDM MUXes with 2 channels each
        self.mux = {}
        self.mux_rp = {}
        self.mux_fp = {}
        for mux_nr in (1, 2, 3, 4):
            self.mux[mux_nr] = Device.objects.create(
                name="MUX{}".format(mux_nr),
                site=self.site,
                device_type=self.device_type['mux'],
                device_role=self.device_role['mux'],
            )

            self.mux_rp[mux_nr] = RearPort.objects.create(
                device=self.mux[mux_nr],
                name="MUX{} DWDM".format(mux_nr),
                type=PortTypeChoices.TYPE_LC,
                positions=8
            )

            self.mux_fp[mux_nr] = {}
            for port_nr in (1, 2):
                self.mux_fp[mux_nr][port_nr] = FrontPort.objects.create(
                    device=self.mux[mux_nr],
                    name="MUX{} CH{}".format(mux_nr, port_nr),
                    type=PortTypeChoices.TYPE_LC,
                    rear_port=self.mux_rp[mux_nr],
                    rear_port_position=port_nr
                )

        # And a circuit
        self.provider = Provider.objects.create(
            name='Provider 1',
            slug='provider-1',
        )
        self.circuit_type = CircuitType.objects.create(
            name='Circuit Type 1',
            slug='circuit-type-1'
        )
        self.circuit = Circuit.objects.create(
            cid='Circuit 1',
            provider=self.provider,
            type=self.circuit_type
        )
        self.circuit_term_a = CircuitTermination.objects.create(
            circuit=self.circuit,
            port_speed=1,
            term_side=CircuitTerminationSideChoices.SIDE_A,
            site=self.site
        )
        self.circuit_term_z = CircuitTermination.objects.create(
            circuit=self.circuit,
            port_speed=1,
            term_side=CircuitTerminationSideChoices.SIDE_Z,
            site=self.site
        )

        # And connect everything together in a way that covers all combinations:
        # Router 1 interface 0 to patch panel rear port 1 (interface to 1-on-1 rear port)
        Cable.objects.create(termination_a=self.router_interface[1][0], termination_b=self.patch_rp[1][1])

        # patch panel front port 1 to patch panel rear port 2 (1-on-1 front port to 1-on-1 rear port)
        Cable.objects.create(termination_a=self.patch_fp[1][1], termination_b=self.patch_rp[1][2])

        # patch panel front port 2 to mux 1 channel 1 (1-on-1 front port to mux front port)
        Cable.objects.create(termination_a=self.patch_fp[1][2], termination_b=self.mux_fp[1][1])

        # Mux 1 rear port to patch panel front port 3 (mux rear port to 1-on-1 front port)
        Cable.objects.create(termination_a=self.mux_rp[1], termination_b=self.patch_fp[1][3])

        # Patch panel rear port 3 to mux 2 channel 2 (1-on-1 rear port to mux front port)
        Cable.objects.create(termination_a=self.patch_rp[1][3], termination_b=self.mux_fp[2][2])

        # Mux 2 rear port to patch panel rear port 4 (mux rear port to 1-on-1 rear port)
        Cable.objects.create(termination_a=self.mux_rp[2], termination_b=self.patch_rp[1][4])

        # Patch panel rear port 4 to circuit termination A (1-on-1 rear port to circuit)
        Cable.objects.create(termination_a=self.patch_fp[1][4], termination_b=self.circuit_term_a)

        # Circuit termination Z to mux rear port (1-on-1 rear port to circuit)
        Cable.objects.create(termination_a=self.circuit_term_z, termination_b=self.mux_rp[3])

        # Mux 3 channel 2 to mux 4 rear port (mux front port to mux rear port)
        Cable.objects.create(termination_a=self.mux_fp[3][2], termination_b=self.mux_rp[4])

        # Mux 4 channel 1 to Router 2 interface 1 (mux front port to interface)
        Cable.objects.create(termination_a=self.mux_fp[4][1], termination_b=self.router_interface[2][1])

    def test_full_trace(self):
        trace = self.router_interface[1][0].trace(follow_circuits=True)

        # Check trace length, we created 10 cables
        self.assertEqual(len(trace), 10)

        # Check that it starts with the given interface and ends with the remote interface
        self.assertEqual(trace[0][0], self.router_interface[1][0])
        self.assertEqual(trace[-1][2], self.router_interface[2][1])

    def test_full_trace_no_circuit(self):
        trace = self.router_interface[1][0].trace(follow_circuits=False)

        # Check trace length, there are 7 cables from this side
        self.assertEqual(len(trace), 7)

        # Check that it starts with the given interface and ends with the circuit termination
        self.assertEqual(trace[0][0], self.router_interface[1][0])
        self.assertEqual(trace[-1][2], self.circuit_term_a)

    def test_full_trace_no_circuit2(self):
        trace = self.router_interface[2][1].trace(follow_circuits=False)

        # Check trace length, there are 3 cables from this side
        self.assertEqual(len(trace), 3)

        # Check that it starts with the given interface and ends with the circuit termination
        self.assertEqual(trace[0][0], self.router_interface[2][1])
        self.assertEqual(trace[-1][2], self.circuit_term_z)

    def test_from_rp_to_interface(self):
        trace = self.patch_rp[1][1].trace(follow_circuits=True)

        # This should be the interface in one hop
        self.assertEqual(len(trace), 1)
        self.assertEqual(trace[0][0], self.patch_rp[1][1])
        self.assertEqual(trace[0][2], self.router_interface[1][0])

    def test_from_second_rp_to_interface(self):
        trace = self.patch_rp[1][2].trace(follow_circuits=True)

        # This should be the interface in two hops
        self.assertEqual(len(trace), 2)
        self.assertEqual(trace[0][0], self.patch_rp[1][2])
        self.assertEqual(trace[0][2], self.patch_fp[1][1])
        self.assertEqual(trace[1][0], self.patch_rp[1][1])
        self.assertEqual(trace[1][2], self.router_interface[1][0])

    def test_from_rp_to_rp(self):
        trace = self.mux_rp[2].trace(follow_circuits=True)

        # It is 3 hops to the corresponding RP
        self.assertEqual(len(trace), 3)
        self.assertEqual(trace[0][0], self.mux_rp[2])
        self.assertEqual(trace[-1][2], self.mux_rp[3])

    def test_from_nested_rp_to_rp(self):
        trace = self.mux_rp[1].trace(follow_circuits=True)

        # It is 6 hops to the corresponding RP
        self.assertEqual(len(trace), 6)
        self.assertEqual(trace[0][0], self.mux_rp[1])
        self.assertEqual(trace[-1][2], self.mux_rp[4])
