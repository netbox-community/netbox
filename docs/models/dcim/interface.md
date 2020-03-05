## Interfaces

Interfaces connect to one another in a symmetric manner: If interface A connects to interface B, interface B therefore connects to interface A. Each type of connection can be classified as either *planned* or *connected*.

Each interface is a assigned a type denoting its physical properties. Two special types exist: the "virtual" type can be used to designate logical interfaces (such as SVIs), and the "LAG" type can be used to desinate link aggregation groups to which physical interfaces can be assigned.

Each interface can also be enabled or disabled, and optionally designated as management-only (for out-of-band management). Fields are also provided to store an interface's MTU and MAC address.

VLANs can be assigned to each interface as either tagged or untagged. (An interface may have only one untagged VLAN.)
