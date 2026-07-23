# Cooling Intakes

A cooling intake is a device component which consumes coolant, such as a server cold-plate inlet or a coolant distribution unit (CDU) intake. A cooling intake optionally references the upstream [cooling outflow](./coolingoutflow.md) which supplies it. The [cooling feed](./coolingfeed.md) an intake belongs to is derived from the rack in which its device is installed, rather than referenced directly.

!!! tip
    Like most device components, cooling intakes are instantiated automatically from [cooling intake templates](./coolingintaketemplate.md) assigned to the selected device type when a device is created.

## Fields

### Device

The device to which this cooling intake belongs.

### Module

The installed module within the assigned device to which this cooling intake belongs (optional).

### Name

The name of the cooling intake. Must be unique to the parent device.

### Label

An alternative physical label identifying the cooling intake.

### Connector Type

The physical coolant connector type (e.g. UQD, UQDB, QDC, camlock, or threaded NPT/BSP).

### Diameter

The connector diameter, expressed as a numeric value with a selectable unit (millimeters, centimeters, or inches).

### Maximum Flow

The maximum coolant flow rate this port supports, expressed as a numeric value with a selectable unit (litres per minute, cubic meters per hour, or gallons per minute).
