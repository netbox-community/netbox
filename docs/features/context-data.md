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

While this is handy on its own, the real power of context data stems from its ability to be merged and overridden using multiple instances. For example, perhaps you need to define _different_ syslog servers within the region for a particular device role. You can create a second config context with the appropriate data and a higher weight, and apply it to the desired role. This will override the lower-weight data that applies to the entire region. As you can imagine, this flexibility can cater to many complex use cases.

There are no restrictions around what data can be stored in a configuration context, so long as it can be expressed in JSON. Additionally, each device and VM may have local context data defined: This data is stored directly on the assigned object, and applies to it only. This is a convenient way for "attaching" miscellaneous data to a single device or VM as needed.

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
