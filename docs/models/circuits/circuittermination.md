# Circuit Terminations

A circuit may have one or two terminations, annotated as the "A" and "Z" sides of the circuit. A single-termination circuit can be used when you don't know (or care) about the far end of a circuit (for example, an Internet access circuit which connects to a transit provider). A dual-termination circuit is useful for tracking circuits which connect two sites.

Each circuit termination is tied to a site, and may optionally be connected via a cable to a specific device interface or pass-through port. Each termination can be assigned a separate downstream and upstream speed independent from one another. Fields are also available to track cross-connect and patch panel details.

!!! note
    A circuit represents a physical link, and cannot have more than two endpoints. When modeling a multi-point topology, each leg of the topology must be defined as a discrete circuit.

!!! note
    A circuit may terminate only to a physical interface. Circuits may not terminate to LAG interfaces, which are virtual interfaces: You must define each physical circuit within a service bundle separately and terminate it to its actual physical interface.
