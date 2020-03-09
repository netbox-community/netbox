# Cables

A cable represents a physical connection between two termination points, such as between a console port and a patch panel port, or between two network interfaces. Cables can be traced through pass-through ports to form a complete path between two endpoints. In the example below, three individual cables comprise a path between the two connected endpoints.

```
|<------------------------------------------ Cable Path ------------------------------------------->|

  Device A                   Patch Panel A                 Patch Panel B                  Device B
+-----------+               +-------------+               +-------------+               +-----------+
| Interface | --- Cable --- | Front Port  |               | Front Port  | --- Cable --- | Interface |
+-----------+               +-------------+               +-------------+               +-----------+
                            +-------------+               +-------------+
                            |  Rear Port  | --- Cable --- |  Rear Port  |
                            +-------------+               +-------------+
```

All connections between device components in NetBox are represented using cables. However, defining the actual cable plant is optional: Components can be be directly connected using cables with no type or other attributes assigned.

Cables are also used to associated ports and interfaces with circuit terminations. To do this, first create the circuit termination, then navigate the desired component and connect a cable between the two.
