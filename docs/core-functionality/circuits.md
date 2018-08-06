# Providers

A provider is any entity which provides some form of connectivity. While this obviously includes carriers which offer Internet and private transit service, it might also include Internet exchange (IX) points and even organizations with whom you peer directly.

Each provider may be assigned an autonomous system number (ASN), an account number, and relevant contact information.

---

# Circuits

A circuit represents a single _physical_ link connecting exactly two endpoints. (A circuit with more than two endpoints is a virtual circuit, which is not currently supported by NetBox.) Each circuit belongs to a provider and must be assigned a circuit ID which is unique to that provider.

## Circuit Types

Circuits are classified by type. For example, you might define circuit types for:

* Internet transit
* Out-of-band connectivity
* Peering
* Private backhaul

Circuit types are fully customizable.

## Circuit Terminations

A circuit may have one or two terminations, annotated as the "A" and "Z" sides of the circuit. A single-termination circuit can be used when you don't know (or care) about the far end of a circuit (for example, an Internet access circuit which connects to a transit provider). A dual-termination circuit is useful for tracking circuits which connect two sites.

Each circuit termination is tied to a site, and optionally to a specific device and interface within that site. Each termination can be assigned a separate downstream and upstream speed independent from one another. Fields are also available to track cross-connect and patch panel details.

!!! note
    A circuit represents a physical link, and cannot have more than two endpoints. When modeling a multi-point topology, each leg of the topology must be defined as a discrete circuit.

!!! note
    A circuit may terminate only to a physical interface. Circuits may not terminate to LAG interfaces, which are virtual interfaces: You must define each physical circuit within a service bundle separately and terminate it to its actual physical interface.
