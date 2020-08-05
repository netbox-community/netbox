## Power Ports

A power port represents the inlet of a device where it draws its power, i.e. the connection port(s) on a device's power supply. Each power port may be assigned a physical type, as well as allocated and maximum draw values (in watts). These values can be used to calculate the overall utilization of an upstream power feed.

!!! info
    When creating a power port on a device which supplies power to downstream devices, the allocated and maximum draw numbers should be left blank. Utilization will be calculated by taking the sum of all power ports of devices connected downstream.

Cables can connect power ports only to power outlets or power feeds. (Pass-through ports cannot be used to model power distribution.)
