# MAC Addresses

A MAC address object in NetBox represents a single Ethernet link-layer address as reported by or assigned to a network interface. MAC addresses can be assigned to [device interfaces](./interface.md) and [virtual machine interfaces](../virtualization/vminterface.md), and any one of an interface's assigned MAC addresses may be designated as its **primary** MAC address.

Most physical interfaces have only a single MAC address, hard-coded at the factory. However, some interfaces (particularly virtual interfaces and modular hardware) support multiple or reassignable MAC addresses. To accommodate this, NetBox models MAC addresses as first-class objects which may be created, modified, and reassigned independently of any specific interface.

## Fields

### MAC Address

The 48-bit MAC address, expressed in colon-hexadecimal notation (for example, `aa:bb:cc:11:22:33`).

### Assigned Object

A generic reference to the [device interface](./interface.md) or [virtual machine interface](../virtualization/vminterface.md) to which this MAC address is assigned. A MAC address may exist without being assigned to any interface.

A MAC address that is currently designated as the primary MAC of its parent interface cannot be reassigned to (or unassigned from) another interface without first clearing the primary designation.

### Description

An optional human-readable description of the MAC address.

### Comments

Free-form Markdown-supported notes regarding the MAC address.
