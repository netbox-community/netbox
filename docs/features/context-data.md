# Context Data

Configuration context data (or "config contexts" for short) is a powerful feature that enables users to define arbitrary data that applies to device and virtual machines based on certain characteristics. For example, suppose you want to define syslog servers for devices assigned to sites within a particular region. In NetBox, you can create a config context instance containing this data and apply it to the desired region. All devices within this region will now include this data when fetched via an API.

```json
{
    "syslog-servers": [
        "192.168.43.107",
        "192.168.48.112"
    ]
}
```

Context data can be consumed by remote API clients, or it can be employed natively to render [configuration templates](./configuration-rendering.md).

Config contexts can be computed for objects based on the following criteria:

| Type          | Devices          | Virtual Machines |
|---------------|------------------|------------------|
| Region        | :material-check: | :material-check: |
| Site group    | :material-check: | :material-check: |
| Site          | :material-check: | :material-check: |
| Location      | :material-check: |                  |
| Device type   | :material-check: |                  |
| Role          | :material-check: | :material-check: |
| Platform      | :material-check: | :material-check: |
| Cluster type  |                  | :material-check: |
| Cluster group |                  | :material-check: |
| Cluster       |                  | :material-check: |
| Tenant group  | :material-check: | :material-check: |
| Tenant        | :material-check: | :material-check: |
| Tag           | :material-check: | :material-check: |

There are no restrictions around what data can be stored in a configuration context, so long as it can be expressed in JSON.

## Hierarchical Rendering

While this is handy on its own, the real power of context data stems from its ability to be merged and overridden using multiple instances. For example, perhaps you need to define _different_ syslog servers within the region for a particular device role. You can create a second config context with the appropriate data and a higher weight, and apply it to the desired role. This will override the lower-weight data that applies to the entire region. As you can imagine, this flexibility can cater to many complex use cases.

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

Devices and virtual machines may also have a local context data defined. This local context will _always_ take precedence over any separate config context objects which apply to the device/VM. This is useful in situations where we need to call out a specific deviation in the data for a particular object.

!!! warning
    If you find that you're routinely defining local context data for many individual devices or virtual machines, [custom fields](./customization.md#custom-fields) may offer a more effective solution.
