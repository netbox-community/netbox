# Contextual Configuration Data

Sometimes it is desirable to associate arbitrary data with a group of devices to aid in their configuration. For example, you might want to associate a set of syslog servers for all devices at a particular site. Context data enables the association of arbitrary data to devices and virtual machines grouped by region, site, role, platform, and/or tenant. Context data is arranged hierarchically, so that data with a higher weight can be entered to override more general lower-weight data. Multiple instances of data are automatically merged by NetBox to present a single dictionary for each object.

Devices and Virtual Machines may also have a local config context defined. This local context will always overwrite the rendered config context objects for the Device/VM. This is useful in situations were the device requires a one-off value different from the rest of the environment.
