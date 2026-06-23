# Cooling Outlets

A cooling outlet is a device component which delivers coolant to a downstream [cooling port](./coolingport.md), and generally represents an outlet on a coolant distribution unit (CDU) or manifold. A cooling outlet may optionally be associated with an upstream cooling port on the same device for path tracing.

!!! tip
    Like most device components, cooling outlets are instantiated automatically from [cooling outlet templates](./coolingoutlettemplate.md) assigned to the selected device type when a device is created.

## Fields

### Device

The device to which this cooling outlet belongs.

### Module

The installed module within the assigned device to which this cooling outlet belongs (optional).

### Name

The name of the cooling outlet. Must be unique to the parent device.

### Label

An alternative physical label identifying the cooling outlet.

### Type

Indicates whether the outlet carries supply (cold) or return (warm) coolant.

### Connector Type

The physical coolant connector type (e.g. UQD, UQDB, QDC, camlock, or threaded NPT/BSP).

### Diameter

The connector diameter, expressed as a numeric value with a selectable unit (millimeters, centimeters, or inches).

### Cooling Port

The upstream [cooling port](./coolingport.md) on the same device which feeds this outlet (optional).

### Color

The color of the outlet (for organizational purposes).

### Mark Connected

If selected, this component will be treated as if a cable has been connected.
