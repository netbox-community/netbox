# Object Permissions

Assigning a permission in NetBox entails defining a relationship among several components:

* Object type(s) - One or more types of object in NetBox
* User(s) - One or more users or groups of users
* Actions - The actions that can be performed (view, add, change, and/or delete)
* Constraints - An arbitrary filter used to limit the granted action(s) to a specific subset of objects

At a minimum, a permission assignment must specify one object type, one user or group, and one action. The specification of constraints is optional: A permission without any constraints specified will apply to all instances of the selected model(s).

## Actions

There are four core actions that can be permitted for each type of object within NetBox, roughly analogous to the CRUD convention (create, read, update, and delete):

* View - Retrieve an object from the database
* Add - Create a new object
* Change - Modify an existing object
* Delete - Delete an existing object

Some models introduce additional permissions that can be granted to allow other actions. For example, the `napalm_read` permission on the device model allows a user to execute NAPALM queries on a device via NetBox's REST API. These can be specified when granting a permission in the "additional actions" field.

## Constraints

Constraints are defined as a JSON object representing a [Django query filter](https://docs.djangoproject.com/en/stable/ref/models/querysets/#field-lookups). This is the same syntax that you would pass to the QuerySet `filter()` method when performing a query using the Django ORM. As with query filters, double underscores can be used to traverse related objects or invoke lookup expressions. Some example queries and their corresponding definitions are shown below.

All constraints defined on a permission are applied with a logic AND. For example, suppose you assign a permission for the site model with the following constraints.

```json
{
  "status": "active",
  "region__name": "Americas"
}
```

The permission will grant access only to sites which have a status of "active" **and** which are assigned to the "Americas" region. To achieve a logical OR with a different set of constraints, simply create another permission assignment for the same model and user/group. 
