# Rack Reservations

Users can reserve specific units within a [rack](./rackreservation.md) for future use. An arbitrary set of units within a rack can be associated with a single reservation, but reservations cannot span multiple racks. A description is required for each reservation, reservations may optionally be associated with a specific tenant.

## Fields

### Rack

The [rack](./rack.md) being reserved.

### Units

The rack unit or units being reserved. Multiple units can be expressed using commas and/or hyphens. For example, `1,3,5-7` specifies units 1, 3, 5, 6, and 7.

### User

The NetBox user account associated with the reservation. Note that users with sufficient permission can make rack reservations for other users.

### Description

Every rack reservation must include a description of its purpose.
