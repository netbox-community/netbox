# Circuits

A communications circuit represents a single _physical_ link connecting exactly two endpoints, commonly referred to as its A and Z terminations. A circuit in NetBox may have zero, one, or two terminations defined. It is common to have only one termination defined when you don't necessarily care about the details of the provider side of the circuit, e.g. for Internet access circuits. Both terminations would likely be modeled for circuits which connect one customer site to another.

Each circuit is associated with a provider and a user-defined type. For example, you might have Internet access circuits delivered to each site by one provider, and private MPLS circuits delivered by another. Each circuit must be assigned a circuit ID, each of which must be unique per provider.

Each circuit is also assigned one of the following operational statuses:

* Planned
* Provisioning
* Active
* Offline
* Deprovisioning
* Decommissioned

Circuits also have optional fields for annotating their installation date and commit rate, and may be assigned to NetBox tenants.

!!! note
    NetBox currently models only physical circuits: those which have exactly two endpoints. It is common to layer virtualized constructs (_virtual circuits_) such as MPLS or EVPN tunnels on top of these, however NetBox does not yet support virtual circuit modeling.
