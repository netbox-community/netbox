# Inventory Item Roles

!!! warning "Deprecation Warning"
    Beginning in NetBox v4.3, the use of inventory items has been deprecated. They are planned for removal in a future NetBox release. Users are strongly encouraged to begin using [modules](./module.md) and [module types](./moduletype.md) in place of inventory items. Modules provide enhanced functionality and can be configured with user-defined attributes.

Inventory items can be organized by functional roles, which are fully customizable by the user. For example, you might create roles for power supplies, fans, interface optics, etc.

## Fields

### Name

A unique human-friendly name.

### Slug

A unique URL-friendly identifier. (This value can be used for filtering.)

### Color

The color used when displaying the role in the NetBox UI.
