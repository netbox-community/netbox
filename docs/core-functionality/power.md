# Power Tracking

{!docs/models/dcim/powerpanel.md!}
{!docs/models/dcim/powerfeed.md!}

# Example Power Topology

Below is a simple diagram demonstrating how power is modeled in NetBox.

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
