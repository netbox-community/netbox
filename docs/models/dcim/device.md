# Devices

Every piece of hardware which is installed within a site or rack exists in NetBox as a device. Devices are measured in rack units (U) and can be half depth or full depth. A device may have a height of 0U: These devices do not consume vertical rack space and cannot be assigned to a particular rack unit. A common example of a 0U device is a vertically-mounted PDU.

When assigning a multi-U device to a rack, it is considered to be mounted in the lowest-numbered rack unit which it occupies. For example, a 3U device which occupies U8 through U10 is said to be mounted in U8. This logic applies to racks with both ascending and descending unit numbering.

A device is said to be full-depth if its installation on one rack face prevents the installation of any other device on the opposite face within the same rack unit(s). This could be either because the device is physically too deep to allow a device behind it, or because the installation of an opposing device would impede airflow.

Each device must be instantiated from a pre-created device type, and its default components (console ports, power ports, interfaces, etc.) will be created automatically. (The device type associated with a device may be changed after its creation, however its components will not be updated retroactively.)

Each device must be assigned a site, device role, and operational status, and may optionally be assigned to a specific rack within a site. A platform, serial number, and asset tag may optionally be assigned to each device.

Device names must be unique within a site, unless the device has been assigned to a tenant. Devices may also be unnamed.

When a device has one or more interfaces with IP addresses assigned, a primary IP for the device can be designated, for both IPv4 and IPv6.
