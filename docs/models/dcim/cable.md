# Cables

All connections between device components in NetBox are represented using cables. A cable represents a direct physical connection between two sets of endpoints (A and B), such as a console port and a patch panel port, or between two network interfaces. Cables may be connected to the following objects:

* Network interfaces
* Console ports
* Console server ports
* Pass-through ports (front and rear)
* Circuit terminations
* Power ports
* Power outlets
* Power feeds

## Fields

### Status

The cable's operational status. Choices include:

* Active (default)
* Planned
* Decommissioning

### Profile

!!! note "This field was introduced in NetBox v4.5."

The profile to which the cable conforms. The profile determines the mapping of termination between the two ends and enables logical tracing across complex connections, such as breakout cables. Supported profiles are listed below.

* Straight (single position)
* Straight (multi-position)
* Shuffle (2x2 MPO8)
* Shuffle (4x4 MPO8)

A single-position cable is allowed only one termination point at each end. There is no limit to the number of terminations a multi-position cable may have. Each end of a cable must have the same number of terminations, unless connected to a pass-through port or to a circuit termination.

The assignment of a cable profile is optional. If no profile is assigned, legacy tracing behavior will be preserved.

### Type

The cable's physical medium or classification.

### Label

An arbitrary label used to identify the cable.

### Color

The color of the cable.

### Length

The numeric length of the cable, including a unit designation (e.g. 100 meters or 25 feet).

## Tracing Cables

A cable may be traced from any of its endpoints by clicking the "trace" button. (A REST API endpoint also provides this functionality.) NetBox will follow the path of connected cables from this termination across the directly connected cable to the far-end termination. If the cable connects to a pass-through port, and the peer port has another cable connected, NetBox will continue following the cable path until it encounters a non-pass-through or unconnected termination point. The entire path will be displayed to the user.
