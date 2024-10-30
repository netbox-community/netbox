# Circuit Terminations

Each circuit may have up to two terminations, designated A and Z. At either termination, a circuit may connect to a site, device interface (via a cable), or to a provider network.

In adherence with NetBox's philosophy of closely modeling the real world, a circuit may be connected only to a physical interface. For example, circuits may not terminate to LAG interfaces, which are virtual in nature. In such cases, a separate physical circuit is associated with each LAG member interface and each needs to be modeled discretely.

!!! note
    A circuit in NetBox represents a physical link, and cannot have more than two endpoints. When modeling a multi-point topology, each leg of the topology must be defined as a discrete circuit, with one end terminating within the provider's infrastructure. The provider network model is ideal for representing these networks.

## Fields

### Circuit

The [circuit](./circuit.md) to which this termination belongs.

### Termination Side

Designates the termination as forming either the A or Z end of the circuit.

### Mark Connected

If selected, the circuit termination will be considered "connected" even if no cable has been connected to it in NetBox.

### Termination

The [region](../dcim/region.md), [site group](../dcim/sitegroup.md), [site](../dcim/site.md), [location](../dcim/location.md) or [provider network](./providernetwork.md) with which this circuit termination is associated. Once created, a cable can be connected between the circuit termination and a device interface (or similar component).

### Port Speed

The operating speed of the terminated interface, in kilobits per second. This is useful for documenting the speed of a circuit when the actual interface to which it terminates is not being modeled in NetBox.

### Upstream Speed

The upstream speed of the terminated interface (in kilobits per second), if different from the downstream speed (a common scenario with e.g. DOCSIS cable modems).

### Cross-connect ID

In a data center environment, circuits are often delivered via a local cross-connect. While it may not be appropriate to model the cross-connect itself in NetBox, it's a good idea to record its ID for reference where applicable.

### Patch Panel & Port(s)

Similar to the cross-connect ID, this field can be used to track physical connection details which may be outside the scope of what is being modeled in NetBox.
