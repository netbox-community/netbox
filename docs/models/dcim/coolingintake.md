# Cooling Ports

A cooling intake is a device component which represents a coolant intake on a device, such as a server cold-plate inlet or a coolant distribution unit (CDU) intake. A cooling intake references the upstream [cooling outlet](./coolingoutflow.md) or [cooling feed](./coolingfeed.md) which supplies it.

!!! tip
    Like most device components, cooling ports are instantiated automatically from [cooling port templates](./coolingintaketemplate.md) assigned to the selected device type when a device is created.

## Fields

### Device

The device to which this cooling port belongs.

### Module

The installed module within the assigned device to which this cooling port belongs (optional).

### Name

The name of the cooling port. Must be unique to the parent device.

### Label

An alternative physical label identifying the cooling port.

### Connector Type

The physical coolant connector type (e.g. UQD, UQDB, QDC, camlock, or threaded NPT/BSP).

### Diameter

The connector diameter, expressed as a numeric value with a selectable unit (millimeters, centimeters, or inches).

### Maximum Flow

The maximum coolant flow rate this port supports, expressed as a numeric value with a selectable unit (litres per minute, cubic meters per hour, or gallons per minute).
