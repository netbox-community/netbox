# Power Panel

A power panel represents the origin point in NetBox for electrical power being disseminated by one or more power feeds. In a data center environment, one power panel often serves a group of racks, with an individual power feed extending to each rack, though this is not always the case. It is common to have two sets of panels and feeds arranged in parallel to provide redundant power to each rack.

Each power panel must be assigned to a site, and may optionally be assigned to a particular rack group.

!!! note
    NetBox does not model the mechanism by which power is delivered to a power panel. Power panels define the root level of the power distribution hierarchy in NetBox.
