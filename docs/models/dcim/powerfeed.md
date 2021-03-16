# Power Feed

A power feed represents the distribution of power from a power panel to a particular device, typically a power distribution unit (PDU). The power pot (inlet) on a device can be connected via a cable to a power feed. A power feed may optionally be assigned to a rack to allow more easily tracking the distribution of power among racks.

Each power feed is assigned an operational type (primary or redundant) and one of the following statuses:

* Offline
* Active
* Planned
* Failed

Each power feed also defines the electrical characteristics of the circuit which it represents. These include the following:

* Supply type (AC or DC)
* Phase (single or three-phase)
* Voltage
* Amperage
* Maximum utilization (percentage)

!!! info
    The power utilization of a rack is calculated when one or more power feeds are assigned to the rack and connected to devices that draw power.
