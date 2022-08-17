# Custom Links

Users can add custom links to object views in NetBox to reference external resources. For example, you might create a custom link for devices pointing to a monitoring system. See the [custom links documentation](../../customization/custom-links.md) for more information.

## Fields

### Name

The name of the custom link. This is used primarily for administrative purposes only, although custom links of the same weight are ordered alphabetically by name when being rendered in the UI.

### Content Type

The type of NetBox object to which this custom link applies.

### Weight

A numeric weight used to override alphabetic ordering of links by name. Custom fields with a lower weight will be listed before those with a higher weight. (Note that weight applies within the context of a custom link group, if defined.)

### Group Name

If this custom link should be grouped with others, specify the name of the group here. Grouped custom links will be listed in a dropdown menu attached to a single button bearing the group name.

### Button Class

The color of the UI button.

### Enabled

If not selected, the custom link will not be rendered. This can be useful for temporarily disabling a custom link.

### New Window

If selected, this will force the link to open in a new browser tab or window.

### Link Text

Jinja2 template code for rendering the button text. (Note that this does not _need_ to contain any template variables.) See below for available context data.

!!! note
    Custom links which render an empty text value will not be displayed in the UI. This can be used to toggle the inclusion of a link based on object attributes.

### Link URL

Jinja2 template code for rendering the hyperlink. See below for available context data.

## Context Data

The following context variables are available in to the text and link templates.

| Variable  | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| `object`  | The NetBox object being displayed                                           |
| `debug`   | A boolean indicating whether debugging is enabled                           |
| `request` | The current WSGI request                                                    |
| `user`    | The current user (if authenticated)                                         |
| `perms`   | The [permissions](../../administration/permissions.md) assigned to the user |
