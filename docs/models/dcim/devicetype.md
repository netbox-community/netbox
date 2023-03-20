# Device Types

A device type represents a particular make and model of hardware that exists in the real world. Device types define the physical attributes of a device (rack height and depth) and its individual components (console, power, network interfaces, and so on).

Device types are instantiated as devices installed within sites and/or equipment racks. For example, you might define a device type to represent a Juniper EX4300-48T network switch with 48 Ethernet interfaces. You can then create multiple _instances_ of this type named "switch1," "switch2," and so on. Each device will automatically inherit the components (such as interfaces) of its device type at the time of creation. However, changes made to a device type will **not** apply to instances of that device type retroactively.

!!! note
    This parent/child relationship is **not** suitable for modeling chassis-based devices, wherein child members share a common control plane. Instead, line cards and similarly non-autonomous hardware should be modeled as modules or inventory items within a device.

## Fields

### Manufacturer

The [manufacturer](./manufacturer.md) which produces this type of device.

### Model

The model number assigned to this device type by its manufacturer. Must be unique to the manufacturer.

### Slug

A unique URL-friendly representation of the model identifier. (This value can be used for filtering.)

### Default Platform

If defined, devices instantiated from this type will automatically inherit the selected platform. (This assignment can be changed after the device has been created.)

### Part Number

An alternative part number to uniquely identify the device type.

### Height

The height of the physical device in rack units. (For device types that are not rack-mountable, this should be `0`.)

### Is Full Depth

If selected, this device type is considered to occupy both the front and rear faces of a rack, regardless of which face it is assigned.

### Parent/Child Status

Indicates whether this is a parent type (capable of housing child devices), a child type (which must be installed within a device bay), or neither.

### Airflow

The default direction in which airflow circulates within the device chassis. This may be configured differently for instantiated devices (e.g. because of different fan modules).

### Weight

The numeric weight of the device, including a unit designation (e.g. 10 kilograms or 20 pounds).

### Front & Rear Images

Users can upload illustrations of the device's front and rear panels. If present, these will be used to render the device in [rack](./rack.md) elevation diagrams.
