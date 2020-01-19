# Power Panel

A power panel represents distribution board where power circuits – and their circuit breakers – terminate on. If you have multiple power panels in your data center, you should model them as such in NetBox to assist you in determining the redundancy of your power allocation.

# Power Feed

A power feed identifies the power outlet/drop that goes to a rack and is terminated to a power panel. Power feeds have a supply type (AC/DC), voltage, amperage, and phase type (single/three).

Power feeds are optionally assigned to a rack. In addition, a power port – and only one – can connect to a power feed; in the context of a PDU, the power feed is analogous to the power outlet that a PDU's power port/inlet connects to.

!!! info
    The power usage of a rack is calculated when a power feed (or multiple) is assigned to that rack and connected to a power port.

# Power Outlet

Power outlets represent the ports on a PDU that supply power to other devices. Power outlets are downstream-facing towards power ports. A power outlet can be associated with a power port on the same device and a feed leg (i.e. in a case of a three-phase supply). This can be used to indicate which power port of a PDU is used to supply power through its power outlets.

# Power Port

A power port is the inlet of a device where it draws its power. Power ports are upstream-facing towards power outlets. Alternatively, a power port can connect to a power feed – as mentioned in the power feed section – to indicate the power source of a PDU's inlet.

!!! info
    If the draw of a power port is left empty, it will be dynamically calculated based on the power outlets associated with that power port. This is usually the case on the power ports of devices that supply power, like a PDU.


# Example

Below is a simple diagram demonstrating how power is modelled in NetBox.

!!! note
    The power feeds are connected to the same power panel to illustrative purposes; usually, you would have such feeds diversely connected to panels to avoid the single point of failure.

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
