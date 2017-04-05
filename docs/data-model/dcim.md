Data center infrastructure management (DCIM) entails all physical assets: sites, racks, devices, cabling, etc.

# Sites

How you choose to use sites will depend on the nature of your organization, but typically a site will equate to a building or campus. For example, a chain of banks might create a site to represent each of its branches, a site for its corporate headquarters, and two additional sites for its presence in two colocation facilities.

Sites can be assigned an optional facility ID to identify the actual facility housing colocated equipment, and an Autonomous System (AS) number.

### Regions

Sites can be arranged geographically using regions. A region might represent a continent, country, city, campus, or other area depending on your use case. Regions can be nested recursively to construct a hierarchy. For example, you might define several country regions, and within each of those several state or city regions to which sites are assigned.

---

# Racks

The rack model represents a physical two- or four-post equipment rack in which equipment is mounted. Each rack is assigned to a site. Rack height is measured in *rack units* (U); racks are commonly between 42U and 48U, but NetBox allows you to define racks of arbitrary height. Each rack has two faces (front and rear) on which devices can be mounted.

Each rack is assigned a name and (optionally) a separate facility ID. This is helpful when leasing space in a data center your organization does not own: The facility will often assign a seemingly arbitrary ID to a rack (for example, "M204.313") whereas internally you refer to is simply as "R113." The facility ID can alternatively be used to store a rack's serial number.

The available rack types include 2- and 4-post frames, 4-post cabinet, and wall-mounted frame and cabinet. Rail-to-rail width may be 19 or 23 inches.

### Rack Groups

Racks can be arranged into groups. As with sites, how you choose to designate rack groups will depend on the nature of your organization. For example, if each site represents a campus, each group might represent a building within a campus. If each site represents a building, each rack group might equate to a floor or room.

Each group is assigned to a parent site for easy navigation. Hierarchical recursion of rack groups is not supported.

### Rack Roles

Each rack can optionally be assigned a functional role. For example, you might designate a rack for compute or storage resources, or to house colocated customer devices. Rack roles are fully customizable.

### Rack Space Reservations

Users can reserve units within a rack for future use. Multiple non-contiguous rack units can be associated with a single reservation (but reservations cannot span multiple racks).

---

# Device Types

A device type represents a particular hardware model that exists in the real world. Device types describe the physical attributes of a device (rack height and depth), its class (e.g. console server, PDU, etc.), and its individual components (console, power, and data).

Device types are instantiated as devices installed within racks. For example, you might define a device type to represent a Juniper EX4300-48T network switch with 48 Ethernet interfaces. You can then create multiple devices of this type named "switch1," "switch2," and so on. Each device will inherit the components (such as interfaces) of its device type.

### Manufacturers

Each device type belongs to one manufacturer; e.g. Cisco, Opengear, or APC. The model number of a device type must be unique to its manufacturer.

### Component Templates

Each device type is assigned a number of component templates which define the physical interfaces a device has. These are:

* Console ports
* Console server ports
* Power ports
* Power outlets
* Interfaces
* Device bays

Whenever a new device is created, it is automatically assigned components per the templates assigned to its device type. For example, a Juniper EX4300-48T device type might have the following component templates:

* One template for a console port ("Console")
* Two templates for power ports ("PSU0" and "PSU1")
* 48 templates for 1GE interfaces ("ge-0/0/0" through "ge-0/0/47")
* Four templates for 10GE interfaces ("xe-0/2/0" through "xe-0/2/3")

Once component templates have been created, every new device that you create as an instance of this type will automatically be assigned each of the components listed above.

!!! note
    Assignment of components from templates occurs only at the time of device creation. If you modify the templates of a device type, it will not affect devices which have already been created. However, you always have the option of adding, modifying, or deleting components of existing devices individually.

---

# Devices

Every piece of hardware which is installed within a rack exists in NetBox as a device. Devices are measured in rack units (U) and depth. 0U devices which can be installed in a rack but don't consume vertical rack space (such as a vertically-mounted power distribution unit) can also be defined.

When assigning a multi-U device to a rack, it is considered to be mounted in the lowest-numbered rack unit which it occupies. For example, a 3U device which occupies U8 through U10 shows as being mounted in U8. This logic applies to racks with both ascending and descending unit numbering.

A device is said to be "full depth" if its installation on one rack face prevents the installation of any other device on the opposite face within the same rack unit(s). This could be either because the device is physically too deep to allow a device behind it, or because the installation of an opposing device would impede air flow.

### Roles

NetBox allows for the definition of arbitrary device roles by which devices can be organized. For example, you might create roles for core switches, distribution switches, and access switches. In the interest of simplicity, a device can belong to only one role.

### Platforms

A device's platform is used to denote the type of software running on it. This can be helpful when it is necessary to distinguish between, for instance, different feature sets. Note that two devices of same type may be assigned different platforms: for example, one Juniper MX240 running Junos 14 and another running Junos 15.

The assignment of platforms to devices is an optional feature, and may be disregarded if not desired.

### Inventory Items

Inventory items represent hardware components installed within a device, such as a power supply or CPU. Currently, these are used merely for inventory tracking, although future development might see their functionality expand. Each item can optionally be assigned a manufacturer.

!!! note
    Prior to version 2.0, inventory items were called modules.

### Components

There are six types of device components which comprise all of the interconnection logic with NetBox:

* Console ports
* Console server ports
* Power ports
* Power outlets
* Interfaces
* Device bays

Console ports connect only to console server ports, and power ports connect only to power outlets. Interfaces connect to one another in a symmetric manner: If interface A connects to interface B, interface B therefore connects to interface A. (The relationship between two interfaces is actually represented in the database by an InterfaceConnection object, but this is transparent to the user.) Each type of connection can be classified as either *planned* or *connected*. This allows for easily denoting connections which have not yet been installed.

Each interface is a assigned a form factor denoting its physical properties. Two special form factors exist: the "virtual" form factor can be used to designate logical interfaces (such as SVIs), and the "LAG" form factor can be used to desinate link aggregation groups to which physical interfaces can be assigned. Each interface can also be designated as management-only (for out-of-band management) and assigned a short description.

Device bays represent the ability of a device to house child devices. For example, you might install four blade servers into a 2U chassis. The chassis would appear in the rack elevation as a 2U device with four device bays. Each server within it would be defined as a 0U device installed in one of the device bays. Child devices do not appear on rack elevations, but they are included in the "Non-Racked Devices" list within the rack view.
