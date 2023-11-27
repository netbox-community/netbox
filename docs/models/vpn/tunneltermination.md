# Tunnel Terminations

A tunnel termination connects a device or virtual machine interface to a [tunnel](./tunnel.md). The tunnel must be created before any terminations may be added.

## Fields

### Tunnel

The [tunnel](./tunnel.md) to which this termination is made.

### Role

The functional role of the attached interface. The following options are available:

| Name  | Description                                      |
|-------|--------------------------------------------------|
| Peer  | An endpoint in a point-to-point or mesh topology |
| Hub   | A central point in a hub-and-spoke topology      |
| Spoke | An edge point in a hub-and-spoke topology        |

!!! note
    Multiple hub terminations may be attached to a tunnel.

### Termination

The device or virtual machine interface terminated to the tunnel.

### Outside IP

The public or underlay IP address with which this termination is associated. This is the IP to which peers will route tunneled traffic.
