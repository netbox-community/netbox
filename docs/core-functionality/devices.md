{!docs/models/dcim/devicetype.md!}
{!docs/models/dcim/manufacturer.md!}

---

## Device Component Templates

Each device type is assigned a number of component templates which define the physical components within a device. These are:

* Console ports
* Console server ports
* Power ports
* Power outlets
* Network interfaces
* Front ports
* Rear ports
* Device bays (which house child devices)

Whenever a new device is created, its components are automatically created per the templates assigned to its device type. For example, a Juniper EX4300-48T device type might have the following component templates defined:

* One template for a console port ("Console")
* Two templates for power ports ("PSU0" and "PSU1")
* 48 templates for 1GE interfaces ("ge-0/0/0" through "ge-0/0/47")
* Four templates for 10GE interfaces ("xe-0/2/0" through "xe-0/2/3")

Once component templates have been created, every new device that you create as an instance of this type will automatically be assigned each of the components listed above.

!!! note
    Assignment of components from templates occurs only at the time of device creation. If you modify the templates of a device type, it will not affect devices which have already been created. However, you always have the option of adding, modifying, or deleting components on existing devices.

---

{!docs/models/dcim/device.md!}
{!docs/models/dcim/devicerole.md!}
{!docs/models/dcim/platform.md!}

---

## Device Components

There are eight types of device components which comprise all of the interconnection logic with NetBox:

* Console ports
* Console server ports
* Power ports
* Power outlets
* Network interfaces
* Front ports
* Rear ports
* Device bays

### Console

Console ports connect only to console server ports. Console connections can be marked as either *planned* or *connected*.

### Power

Power ports connect only to power outlets. Power connections can be marked as either *planned* or *connected*.

### Interfaces

Interfaces connect to one another in a symmetric manner: If interface A connects to interface B, interface B therefore connects to interface A. Each type of connection can be classified as either *planned* or *connected*.

Each interface is a assigned a type denoting its physical properties. Two special types exist: the "virtual" type can be used to designate logical interfaces (such as SVIs), and the "LAG" type can be used to desinate link aggregation groups to which physical interfaces can be assigned.

Each interface can also be enabled or disabled, and optionally designated as management-only (for out-of-band management). Fields are also provided to store an interface's MTU and MAC address.

VLANs can be assigned to each interface as either tagged or untagged. (An interface may have only one untagged VLAN.)

### Pass-through Ports

Pass-through ports are used to model physical terminations which comprise part of a longer path, such as a cable terminated to a patch panel. Each front port maps to a position on a rear port. A 24-port UTP patch panel, for instance, would have 24 front ports and 24 rear ports. Although this relationship is typically one-to-one, a rear port may have multiple front ports mapped to it. This can be useful for modeling instances where multiple paths share a common cable (for example, six different fiber connections sharing a 12-strand MPO cable).

Pass-through ports can also be used to model "bump in the wire" devices, such as a media convertor or passive tap.

### Device Bays

Device bays represent the ability of a device to house child devices. For example, you might install four blade servers into a 2U chassis. The chassis would appear in the rack elevation as a 2U device with four device bays. Each server within it would be defined as a 0U device installed in one of the device bays. Child devices do not appear within rack elevations or the "Non-Racked Devices" list within the rack view.

Child devices are first-class Devices in their own right: that is, fully independent managed entities which don't share any control plane with the parent.  Just like normal devices, child devices have their own platform (OS), role, tags, and interfaces.  You cannot create a LAG between interfaces in different child devices.

Therefore, Device bays are **not** suitable for modeling chassis-based switches and routers.  These should instead be modeled as a single Device, with the line cards as Inventory Items.

{!docs/models/dcim/inventoryitem.md!}

---

{!docs/models/dcim/virtualchassis.md!}

---

{!docs/models/dcim/cable.md!}
