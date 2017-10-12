# Utility Views

Utility views are reusable views that handle common CRUD tasks, such as listing and updating objects. Some views operate on individual objects, whereas others (referred to as "bulk" views) operate on multiple objects at once.

## Individual Views

### ObjectListView

Generates a paginated table of objects from a given queryset, which may optionally be filtered.

### ObjectEditView

Updates an object identified by a primary key (PK) or slug. If no existing object is specified, a new object will be created.

### ObjectDeleteView

Deletes an object. The user is redirected to a confirmation page before the deletion is executed.

## Bulk Views

### BulkCreateView

Creates multiple objects at once based on a given pattern. Currently used only for IP addresses.

### BulkImportView

Accepts CSV-formatted data and creates a new object for each line. Creation is all-or-none.

### BulkEditView

Applies changes to multiple objects at once in a two-step operation. First, the list of PKs for selected objects is POSTed and an edit form is presented to the user. On submission of that form, the specified changes are made to all selected objects.

### BulkDeleteView

Deletes multiple objects. The user selects the objects to be deleted and confirms the deletion.

## Component Views

### ComponentCreateView

Create one or more component objects beloning to a parent object (e.g. interfaces attached to a device).

### ComponentEditView

A subclass of `ObjectEditView`: Updates an individual component object.

### ComponentDeleteView

A subclass of `ObjectDeleteView`: Deletes an individual component object.

### BulkComponentCreateView

Create a set of components objects for each of a selected set of parent objects. This view can be used e.g. to create multiple interfaces on multiple devices at once.
