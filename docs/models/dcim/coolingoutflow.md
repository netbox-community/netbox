# Cooling Outflows

A cooling outflow is a device component which delivers coolant to a downstream [cooling intake](./coolingintake.md), and generally represents an outlet on a coolant distribution unit (CDU) or manifold. A cooling outflow may optionally be associated with an upstream cooling intake on the same device for path tracing.

A cooling outflow is a **supply** point on the cold, coolant-distribution side of a loop: it passes coolant onward to downstream equipment. It does **not** represent the return of warmed coolant back to the cooling source. The return path is not modeled per-component; instead, a single [cooling feed](./coolingfeed.md) represents the entire loop, covering both the supply (cold) and return (warm) paths.

!!! tip
    Like most device components, cooling outflows are instantiated automatically from [cooling outflow templates](./coolingoutflowtemplate.md) assigned to the selected device type when a device is created.

## Fields

### Device

The device to which this cooling outflow belongs.

### Module

The installed module within the assigned device to which this cooling outflow belongs (optional).

### Name

The name of the cooling outflow. Must be unique to the parent device.

### Label

An alternative physical label identifying the cooling outflow.

### Connector Type

The physical coolant connector type (e.g. UQD, UQDB, QDC, camlock, or threaded NPT/BSP).

### Diameter

The connector diameter, expressed as a numeric value with a selectable unit (millimeters, centimeters, or inches).

### Cooling Intake

The upstream [cooling intake](./coolingintake.md) on the same device which feeds this outlet (optional).

### Mark Connected

If selected, this component will be treated as if a cable has been connected.
