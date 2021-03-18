# Circuit Terminations

The association of a circuit with a particular site and/or device is modeled separately as a circuit termination. A circuit may have up to two terminations, labeled A and Z. A single-termination circuit can be used when you don't know (or care) about the far end of a circuit (for example, an Internet access circuit which connects to a transit provider). A dual-termination circuit is useful for tracking circuits which connect two sites.

Each circuit termination is attached to either a site or a cloud. Site terminations may optionally be connected via a cable to a specific device interface or port within that site. Each termination must be assigned a port speed, and can optionally be assigned an upstream speed if it differs from the downstream speed (a common scenario with e.g. DOCSIS cable modems). Fields are also available to track cross-connect and patch panel details.

In adherence with NetBox's philosophy of closely modeling the real world, a circuit may be connected only to a physical interface. For example, circuits may not terminate to LAG interfaces, which are virtual in nature. In such cases, a separate physical circuit is associated with each LAG member interface and each needs to be modeled discretely.

!!! note
    A circuit in NetBox represents a physical link, and cannot have more than two endpoints. When modeling a multi-point topology, each leg of the topology must be defined as a discrete circuit, with one end terminating within the provider's infrastructure. The cloud model is ideal for representing these networks.
