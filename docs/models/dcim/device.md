# Devices

Every piece of hardware which is installed within a rack exists in NetBox as a device. Devices are measured in rack units (U) and can be half depth or full depth. A device may have a height of 0U: These devices do not consume vertical rack space and cannot be assigned to a particular rack unit. A common example of a 0U device is a vertically-mounted PDU.

When assigning a multi-U device to a rack, it is considered to be mounted in the lowest-numbered rack unit which it occupies. For example, a 3U device which occupies U8 through U10 is said to be mounted in U8. This logic applies to racks with both ascending and descending unit numbering.

A device is said to be full depth if its installation on one rack face prevents the installation of any other device on the opposite face within the same rack unit(s). This could be either because the device is physically too deep to allow a device behind it, or because the installation of an opposing device would impede airflow.
