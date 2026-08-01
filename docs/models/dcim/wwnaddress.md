# WWN Addresses

A WWN address object in NetBox represents a single Fibre Channel World Wide Name (WWN) as reported by or assigned to a network interface. WWN addresses can be assigned to [device interfaces](./interface.md) and [virtual machine interfaces](../virtualization/vminterface.md), and any one of an interface's assigned WWN addresses may be designated as its **primary** WWN address.

Most physical Fibre Channel interfaces have only a single WWN address, hard-coded at the factory. However, some interfaces (particularly virtual interfaces and modular hardware) support multiple or reassignable WWN addresses. To accommodate this, NetBox models WWN addresses as first-class objects which may be created, modified, and reassigned independently of any specific interface.

## Fields

### WWN Address

The 64-bit WWN address, expressed in colon-hexadecimal notation (for example, `aa:bb:cc:dd:11:22:33:44`).

### Assigned Object

A generic reference to the [device interface](./interface.md) or [virtual machine interface](../virtualization/vminterface.md) to which this WWN address is assigned. A WWN address may exist without being assigned to any interface.

A WWN address that is currently designated as the primary WWN of its parent interface cannot be reassigned to (or unassigned from) another interface without first clearing the primary designation.

### Description

An optional human-readable description of the WWN address.

### Comments

Free-form Markdown-supported notes regarding the WWN address.
