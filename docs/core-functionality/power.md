{!docs/models/dcim/powerpanel.md!}
{!docs/models/dcim/powerfeed.md!}

# Power Outlet

Power outlets represent the ports on a PDU that supply power to other devices. Power outlets are downstream-facing towards power ports. A power outlet can be associated with a power port on the same device and a feed leg (i.e. in a case of a three-phase supply). This indicates which power port supplies power to a power outlet.

# Power Port

A power port is the inlet of a device where it draws its power. Power ports are upstream-facing towards power outlets. Alternatively, a power port can connect to a power feed – as mentioned in the power feed section – to indicate the power source of a PDU's inlet.

!!! info
    If the draw of a power port is left empty, it will be dynamically calculated based on the power outlets associated with that power port. This is usually the case on the power ports of devices that supply power, like a PDU.

# Example

Below is a simple diagram demonstrating how power is modelled in NetBox.

!!! note
    The power feeds are connected to the same power panel for illustrative purposes; usually, you would have such feeds diversely connected to panels to avoid the single point of failure.

```
          +---------------+
          | Power panel 1 |
          +---------------+
            |           |
            |           |
+--------------+     +--------------+
| Power feed 1 |     | Power feed 2 |
+--------------+     +--------------+
       |                     |
       |                     |
       |                     |    <-- Power ports
     +---------+     +---------+
     |  PDU 1  |     |  PDU 2  |
     +---------+     +---------+
       |       \     /       |    <-- Power outlets
       |        \   /        |
       |         \ /         |
       |          X          |
       |         / \         |
       |        /   \        |
       |       /     \       |    <-- Power ports
      +--------+     +--------+
      | Server |     | Router |
      +--------+     +--------+
```
