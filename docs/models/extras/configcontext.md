# Configuration Contexts

Sometimes it is desirable to associate additional data with a group of devices or virtual machines to aid in automated configuration. For example, you might want to associate a set of syslog servers for all devices within a particular region. Context data enables the association of extra user-defined data with devices and virtual machines grouped by one or more of the following assignments:

* Region
* Site group
* Site
* Device type (devices only)
* Role
* Platform
* Cluster group (VMs only)
* Cluster (VMs only)
* Tenant group
* Tenant
* Tag

## Hierarchical Rendering

Context data is arranged hierarchically, so that data with a higher weight can be entered to override lower-weight data. Multiple instances of data are automatically merged by NetBox to present a single dictionary for each object.

For example, suppose we want to specify a set of syslog and NTP servers for all devices within a region. We could create a config context instance with a weight of 1000 assigned to the region, with the following JSON data:

```json
{
    "ntp-servers": [
        "172.16.10.22",
        "172.16.10.33"
    ],
    "syslog-servers": [
        "172.16.9.100",
        "172.16.9.101"
    ]
}
```

But suppose there's a problem at one particular site within this region preventing traffic from reaching the regional syslog server. Devices there need to use a local syslog server instead of the two defined above. We'll create a second config context assigned only to that site with a weight of 2000 and the following data:

```json
{
    "syslog-servers": [
        "192.168.43.107"
    ]
}
```

When the context data for a device at this site is rendered, the second, higher-weight data overwrite the first, resulting in the following:

```json
{
    "ntp-servers": [
        "172.16.10.22",
        "172.16.10.33"
    ],
    "syslog-servers": [
        "192.168.43.107"
    ]
}
```

Data from the higher-weight context overwrites conflicting data from the lower-weight context, while the non-conflicting portion of the lower-weight context (the list of NTP servers) is preserved.

## Local Context Data

Devices and virtual machines may also have a local config context defined. This local context will _always_ take precedence over any separate config context objects which apply to the device/VM. This is useful in situations where we need to call out a specific deviation in the data for a particular object.

!!! warning
    If you find that you're routinely defining local context data for many individual devices or virtual machines, custom fields may offer a more effective solution.
