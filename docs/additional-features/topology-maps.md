# Topology Maps

NetBox can generate simple topology maps from the physical network connections recorded in its database. First, you'll need to create a topology map definition under the admin UI at Extras > Topology Maps.

Each topology map is associated with a site. A site can have multiple topology maps, which might each illustrate a different aspect of its infrastructure (for example, production versus backend infrastructure).

To define the scope of a topology map, decide which devices you want to include. The map will only include interface connections with both points terminated on an included device. Specify the devices to include in the **device patterns** field by entering a list of [regular expressions](https://en.wikipedia.org/wiki/Regular_expression) matching device names. For example, if you wanted to include "mgmt-switch1" through "mgmt-switch99", you might use the regex `mgmt-switch\d+`.

Each line of the **device patterns** field represents a hierarchical layer within the topology map. For example, you might map a traditional network with core, distribution, and access tiers like this:

```
core-switch-[abcd]
dist-switch\d
access-switch\d+;oob-switch\d+
```

Note that you can combine multiple regexes onto one line using semicolons. The order in which regexes are listed on a line is significant: devices matching the first regex will be rendered first, and subsequent groups will be rendered to the right of those.
