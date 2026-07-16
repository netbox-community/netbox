# Service Port Mappings

!!! info "This model was introduced in NetBox v4.7."

A service port mapping pairs a single wire protocol with one or more port numbers, and belongs to an [application service](./service.md) or [application service template](./servicetemplate.md). A service or template may have multiple port mappings — one per protocol — which allows the same port to be exposed on more than one protocol (for example, DNS on both `TCP/53` and `UDP/53`).

Port mappings are managed inline from the parent service or service template.

## Fields

### Protocol

The wire protocol on which the service runs. Choices include UDP, TCP, and SCTP.

### Ports

One or more numeric ports to which the service is bound. Multiple ports can be expressed using commas and/or hyphens. For example, `80,8001-8003` specifies ports 80, 8001, 8002, and 8003.

## Bulk Import (CSV)

When importing services or service templates via CSV, all port mappings for a row are given in a single `port_mappings` column, formatted as `protocol:ports` pairs separated by semicolons. Within each pair, ports use the same comma/hyphen syntax as above. For example:

```
port_mappings
tcp:80,443;udp:53
```

specifies TCP on ports 80 and 443, and UDP on port 53.
