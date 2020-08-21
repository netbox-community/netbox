# Object Permissions

A permission in NetBox represents a relationship shared by several components:

* Object type(s) - One or more types of object in NetBox
* User(s)/Group(s) - One or more users or groups of users
* Action(s) - The action(s) that can be performed on an object
* Constraints - An arbitrary filter used to limit the granted action(s) to a specific subset of objects

At a minimum, a permission assignment must specify one object type, one user or group, and one action. The specification of constraints is optional: A permission without any constraints specified will apply to all instances of the selected model(s).

## Actions

There are four core actions that can be permitted for each type of object within NetBox, roughly analogous to the CRUD convention (create, read, update, and delete):

* **View** - Retrieve an object from the database
* **Add** - Create a new object
* **Change** - Modify an existing object
* **Delete** - Delete an existing object

In addition to these, permissions can also grant custom actions that may be required by a specific model or plugin. For example, the `napalm_read` permission on the device model allows a user to execute NAPALM queries on a device via NetBox's REST API. These can be specified when granting a permission in the "additional actions" field.

!!! note
    Internally, all actions granted by a permission (both built-in and custom) are stored as strings in an array field named `actions`.

## Constraints

Constraints are expressed as a JSON object or list representing a [Django query filter](https://docs.djangoproject.com/en/stable/ref/models/querysets/#field-lookups). This is the same syntax that you would pass to the QuerySet `filter()` method when performing a query using the Django ORM. As with query filters, double underscores can be used to traverse related objects or invoke lookup expressions. Some example queries and their corresponding definitions are shown below.

All attributes defined within a single JSON object are applied with a logical AND. For example, suppose you assign a permission for the site model with the following constraints.

```json
{
  "status": "active",
  "region__name": "Americas"
}
```

The permission will grant access only to sites which have a status of "active" **and** which are assigned to the "Americas" region.

To achieve a logical OR with a different set of constraints, define multiple objects within a list. For example, if you want to constrain the permission to VLANs with an ID between 100 and 199 _or_ a status of "reserved," do the following:

```json
[
  {
    "vid__gte": 100,
    "vid__lt": 200
  },
  {
    "status": "reserved"
  }
]
```

Additionally, where multiple permissions have been assigned for an object type, their collective constraints will be merged using a logical "OR" operation.
