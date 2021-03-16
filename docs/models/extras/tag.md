# Tags

Tags are user-defined labels which can be applied to a variety of objects within NetBox. They can be used to establish dimensions of organization beyond the relationships built into NetBox. For example, you might create a tag to identify a particular ownership or condition across several types of objects.

Each tag has a label, color, and a URL-friendly slug. For example, the slug for a tag named "Dunder Mifflin, Inc." would be `dunder-mifflin-inc`. The slug is generated automatically and makes tags easier to work with as URL parameters. Each tag can also be assigned a description indicating its purpose.

Objects can be filtered by the tags they have applied. For example, the following API request will retrieve all devices tagged as "monitored":

```no-highlight
GET /api/dcim/devices/?tag=monitored
```

The `tag` filter can be specified multiple times to match only objects which have _all_ of the specified tags assigned:

```no-highlight
GET /api/dcim/devices/?tag=monitored&tag=deprecated
```

!!! note
    Tags have changed substantially in NetBox v2.9. They are no longer created on-demand when editing an object, and their representation in the REST API now includes a complete depiction of the tag rather than only its label.
