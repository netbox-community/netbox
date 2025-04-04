# Inventory Item Templates

!!! warning "Deprecation Warning"
    Beginning in NetBox v4.3, the use of inventory items has been deprecated. They are planned for removal in a future NetBox release. Users are strongly encouraged to begin using [modules](./module.md) and [module types](./moduletype.md) in place of inventory items. Modules provide enhanced functionality and can be configured with user-defined attributes.

A template for an inventory item that will be automatically created when instantiating a new device. All attributes of this object will be copied to the new inventory item, including the associations with a parent item and assigned component, if any. See the [inventory item](./inventoryitem.md) documentation for more detail.
