# Virtual Circuits

!!! info "This feature was introduced in NetBox v4.2."

A virtual circuit can connect two or more interfaces atop a set of decoupled physical connections. For example, it's very common to form a virtual connection between two virtual interfaces, each of which is bound to a physical interface on its respective device and physically connected to a [provider network](./providernetwork.md) via an independent [physical circuit](./circuit.md).

## Fields

### Provider Network

The [provider network](./providernetwork.md) across which the virtual circuit is formed.

### Provider Account

The [provider account](./provideraccount.md) with which the virtual circuit is associated (if any).

### Circuit ID

The unique identifier assigned to the virtual circuit by its [provider](./provider.md).

### Type

The assigned [virtual circuit type](./virtualcircuittype.md).

### Status

The operational status of the virtual circuit. By default, the following statuses are available:

| Name           |
|----------------|
| Planned        |
| Provisioning   |
| Active         |
| Offline        |
| Deprovisioning |
| Decommissioned |

!!! tip "Custom circuit statuses"
    Additional circuit statuses may be defined by setting `Circuit.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.
