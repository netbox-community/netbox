# Devices and Cabling

{!models/dcim/device.md!}
{!models/dcim/devicerole.md!}
{!models/dcim/platform.md!}

---

## Device Components

Device components represent discrete objects within a device which are used to terminate cables, house child devices, or track resources.

{!models/dcim/consoleport.md!}
{!models/dcim/consoleserverport.md!}
{!models/dcim/powerport.md!}
{!models/dcim/poweroutlet.md!}
{!models/dcim/interface.md!}
{!models/dcim/frontport.md!}
{!models/dcim/rearport.md!}
{!models/dcim/devicebay.md!}
{!models/dcim/inventoryitem.md!}

---

{!models/dcim/virtualchassis.md!}

---

{!models/dcim/cable.md!}

In the example below, three individual cables comprise a path between devices A and D:

![Cable path](../media/models/dcim_cable_trace.png)

Traced from Interface 1 on Device A, NetBox will show the following path:

* Cable 1: Interface 1 to Front Port 1
* Cable 2: Rear Port 1 to Rear Port 2
* Cable 3: Front Port 2 to Interface 2
