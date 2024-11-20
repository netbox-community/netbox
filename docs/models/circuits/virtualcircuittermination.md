# Virtual Circuit Terminations

This model represents the connection of a virtual [interface](../dcim/interface.md) to a [virtual circuit](./virtualcircuit.md).

## Fields

### Virtual Circuit

The [virtual circuit](./virtualcircuit.md) to which the interface is connected.

### Interface

The [interface](../dcim/interface.md) connected to the virtual circuit.

### Role

The functional role of the termination. This depends on the virtual circuit's topology, which is typically either peer-to-peer or hub-and-spoke (multipoint). Valid choices include:

* Peer
* Hub
* Spoke
