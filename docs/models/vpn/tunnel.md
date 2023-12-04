# Tunnels

A tunnel represents a private virtual connection established among two or more endpoints across a shared infrastructure by employing protocol encapsulation. Common encapsulation techniques include [Generic Routing Encapsulation (GRE)](https://en.wikipedia.org/wiki/Generic_Routing_Encapsulation), [IP-in-IP](https://en.wikipedia.org/wiki/IP_in_IP), and [IPSec](https://en.wikipedia.org/wiki/IPsec). NetBox supports modeling both peer-to-peer and hub-and-spoke tunnel topologies.

Device and virtual machine interfaces are associated to tunnels by creating [tunnel terminations](./tunneltermination.md).

## Fields

### Name

A unique name assigned to the tunnel for identification.

### Status

The operational status of the tunnel. By default, the following statuses are available:

* Planned
* Active
* Disabled

!!! tip "Custom tunnel statuses"
    Additional tunnel statuses may be defined by setting `Tunnel.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Group

The [administrative group](./tunnelgroup.md) to which this tunnel is assigned (optional).

### Encapsulation

The encapsulation protocol or technique employed to effect the tunnel. NetBox supports GRE, IP-in-IP, and IPSec encapsulations.

### Tunnel ID

An optional numeric identifier for the tunnel.

### IPSec Profile

For IPSec tunnels, this is the [IPSec Profile](./ipsecprofile.md) employed to negotiate security associations.
