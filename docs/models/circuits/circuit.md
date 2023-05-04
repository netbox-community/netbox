# Circuits

A circuit represents a physical point-to-point data connection, typically used to interconnect sites across considerable distances (e.g. to deliver Internet connectivity).

## Fields

### Provider

The [provider](./provider.md) to which this circuit belongs.

### Provider Account

Circuits may optionally be assigned to a specific [provider account](./provideraccount.md).

### Circuit ID

An identifier for this circuit. This must be unique to the assigned provider. (Circuits assigned to different providers may have the same circuit ID.)

### Circuit Type

Each circuit is classified by a user-defined [circuit type](./circuittype.md). Generally this is something like "Internet access," "MPLS/VPN," etc.

### Status

The operational status of the circuit. By default, the following statuses are available:

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

### Description

A brief description of the circuit.

### Installation Date

The date on which the circuit was installed.

### Termination Date

The date on which the circuit is scheduled to be disconnected.

### Commit Rate

The committed rate (throughput) of the circuit, in kilobits per second.
