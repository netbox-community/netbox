# Clusters

A cluster is a logical grouping of physical resources within which [virtual machines](./virtualmachine.md) run. Physical [devices](../dcim/device.md) may be associated with clusters as hosts. This allows users to track on which host(s) a particular virtual machine may reside.

## Fields

### Name

A human-friendly name for the cluster. Must be unique within the assigned group and site.

### Type

The [cluster type](./clustertype.md) assigned for this cluster.

### Group

The [cluster group](./clustergroup.md) to which this cluster belongs.

### Status

The cluster's operational status.

!!! tip
    Additional statuses may be defined by setting `Cluster.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Scope

!!! info "This field replaced the `site` field in NetBox v4.2."

The [region](../dcim/region.md), [site](../dcim/site.md), [site group](../dcim/sitegroup.md) or [location](../dcim/location.md) with which this cluster is associated.
