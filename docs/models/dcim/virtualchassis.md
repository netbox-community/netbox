# Virtual Chassis

A virtual chassis represents a set of devices which share a single control plane: a stack of switches which are managed as a single device, for example. Each device in the virtual chassis is assigned a position and (optionally) a priority. Exactly one device is designated the virtual chassis master: This device will typically be assigned a name, secrets, services, and other attributes related to its management.

It's important to recognize the distinction between a virtual chassis and a chassis-based device. For instance, a virtual chassis is not used to model a chassis switch with removable line cards such as the Juniper EX9208, as its line cards are _not_ physically separate devices capable of operating independently.
