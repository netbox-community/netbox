# Tags

Tags are user-defined labels which can be applied to a variety of objects within NetBox. They can be used to establish dimensions of organization beyond the relationships built into NetBox. For example, you might create a tag to identify a particular ownership or condition across several types of objects.

## Fields

### Name

A unique human-friendly label for the tag.

### Slug

A unique URL-friendly identifier. (This value will be used for filtering.) This is automatically generated from the tag's name, but can be altered as needed.

### Color

The color to use when displaying the tag in the NetBox UI.

### Weight

A numeric weight employed to influence the ordering of tags. Tags with a lower weight will be listed before those with higher weights. Values must be within the range **0** to **32767**.

### Object Types

The assignment of a tag may be limited to a prescribed set of objects. For example, it may be desirable to limit the application of a specific tag to only devices and virtual machines.

If no object types are specified, the tag will be assignable to any type of object.
