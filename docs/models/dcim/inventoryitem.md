# Inventory Items

Inventory items represent hardware components installed within a device, such as a power supply or CPU or line card. They are intended to be used primarily for inventory purposes.

Each inventory item can be assigned a functional role, manufacturer, part ID, serial number, and asset tag (all optional). A boolean toggle is also provided to indicate whether each item was entered manually or discovered automatically (by some process outside NetBox).

Inventory items are hierarchical in nature, such that any individual item may be designated as the parent for other items. For example, an inventory item might be created to represent a line card which houses several SFP optics, each of which exists as a child item within the device. An inventory item may also be associated with a specific component within the same device. For example, you may wish to associate a transceiver with an interface.
