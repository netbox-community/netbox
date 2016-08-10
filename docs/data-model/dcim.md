Data center infrastructure management (DCIM) entails all physical assets: sites, racks, devices, cabling, etc.

# Sites

How you define sites will depend on the nature of your organization, but typically a site will equate a building or campus. For example, a chain of banks might create a site to represent each of its branches, a site for its corporate headquarters, and two additional sites for its presence in two colocation facilities.

Sites can be assigned an optional facility ID to identify the actual facility housing colocated equipment.

---

# Racks

Within each site exist one or more racks. Each rack within NetBox represents a physical two- or four-post equipment rack in which equipment is mounted. Rack height is measured in *rack units* (U); most racks are between 42U and 48U, but NetBox allows you to define racks of any height. Each rack has two faces (front and rear) on which devices can be mounted.

Each rack is assigned a name and (optionally) a separate facility ID. This is helpful when leasing space in a data center your organization does not own: The facility will often assign a seemingly arbitrary ID to a rack (for example, M204.313) whereas internally you refer to is simply as "R113." The facility ID can alternatively be used to store a rack's serial number.

The available rack types include 2- and 4-post frames, 4-post cabinet, and wall-mounted frame and cabinet. Rail-to-rail width may be 19 or 23 inches.

### Rack Groups

Racks can be arranged into groups. As with sites, how you choose to designate rack groups will depend on the nature of your organization. For example, if each site is a campus, each group might be a building. If each site is a building, each rack group might be a floor or room.

Each group is assigned to a parent site for easy navigation. Hierarchical recursion of rack groups is not supported.

### Rack Roles

Each rak can optionally be assigned to a functional role. For example, you might designate a rack for compute or storage resources, or to house colocated customer devices.

---

# Device Types

A device type represents a particular manufacturer and model of equipment. Device types describe the physical attributes of a device (rack height and depth), its class (e.g. console server, PDU, etc.), and its individual components (console, power, and data).

### Manufacturers

Each device type belongs to one manufacturer; e.g. Cisco, Opengear, or APC. Manufacturers are used to group different models of device.

### Component Templates

Each device type is assigned a number of component templates which describe the console, power, and data ports a device has. These are:

* Console port templates
* Console server port templates
* Power port templates
* Power outlet templates
* Interface templates
* Device bay templates

Whenever a new device is created, it is automatically assigned console, power, and interface components per the templates assigned to its device type. For example, suppose your network employs Juniper EX4300-48T switches. You would create a device type with a model name "EX4300-48T" and assign it to the manufacturer "Juniper." You might then also create the following templates for it:

* One template for a console port ("Console")
* Two templates for power ports ("PSU0" and "PSU1")
* 48 templates for 1GE interfaces ("ge-0/0/0" through "ge-0/0/47")
* Four templates for 10GE interfaces ("xe-0/2/0" through "xe-0/2/3")

Once you've done this, every new device that you create as an instance of this type will automatically be assigned each of the components listed above.

Note that assignment of components from templates occurs only at the time of device creation: If you modify the templates of a device type, it will not affect devices which have already been created. However, you always have the option of adding, modifying, or deleting components of existing devices individually.

---

# Devices

Every piece of hardware which is installed within a rack exists in NetBox as a device. Devices are measured in rack units (U) and depth. 0U devices which can be installed in a rack but don't consume vertical rack space (such as a vertically-mounted power distribution unit) can also be defined.

When assigning a multi-U device to a rack, it is considered to be mounted in the lowest-numbered rack unit which it occupies. For example, a 3U device which occupies U8 through U10 shows as being mounted in U8.

A device is said to be "full depth" if its installation on one rack face prevents the installation of any other device on the opposite face within the same rack unit(s). This could be either because the device is physically too deep to allow a device behind it, or because the installation of an opposing device would impede air flow.

### Roles

NetBox allows for the definition of arbitrary device roles by which devices can be organized. For example, you might create roles for core switches, distribution switches, and access switches. In the interest of simplicity, device can only belong to one device role.

### Platforms

A device's platform is used to denote the type of software running on it. This can be helpful when it is necessary to distinguish between, for instance, different feature sets. Note that two devices of same type may be assigned different platforms: for example, one Juniper MX240 running Junos 14 and another running Junos 15.

The assignment of platforms to devices is an entirely optional feature, and may be disregarded if not desired.

### Modules

A device can be assigned modules which represent internal components. Currently, these are used merely for inventory tracking, although future development might see their functionality expand. Each module can optionally be assigned to a manufacturer.

### Components

There are six types of device components which comprise all of the interconnection logic with NetBox:

* Console ports
* Console server ports
* Power ports
* Power outlets
* Interfaces
* Device bays

Console ports connect only to console server ports, and power ports connect only to power outlets. Interfaces connect to one another in a symmetric manner: If interface A connects to interface B, interface B therefore connects to interface A. (The relationship between two interfaces is actually represented in the database by an InterfaceConnection object, but this is transparent to the user.)

Each type of connection can be classified as either *planned* or *connected*. This allows for easily denoting connections which have not yet been installed. In addition to a connecting peer, interfaces are also assigned a form factor and may be designated as management-only (for out-of-band management). Interfaces may also be assigned a short description.

Device bays represent the ability of a device to house child devices. For example, you might install four blade servers into a 2U chassis. The chassis would appear in the rack elevation as a 2U device with four device bays. Each server within it would be defined as a 0U device installed in one of the device bays. Child devices do not appear on rack elevations, but they are included in the "Non-Racked Devices" list within the rack view.

Note that child devices differ from modules in that they are still treated as independent devices, with their own console/power/data components, modules, and IP addresses. Modules, on the other hand, are parts within a device, such as a hard disk or power supply.
