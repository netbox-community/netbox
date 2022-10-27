# Populating Data

This section covers the mechanisms which are available to populate data in NetBox.

## Manual Object Creation

The simplest and most direct way of populating data in NetBox is to use the object creation forms in the user interface.

!!! warning "Not Ideal for Large Imports"
    While convenient and readily accessible to even novice users, creating objects one at a time by manually completing these forms obviously does not scale well. For large imports, you're generally best served by using one of the other methods discussed in this section.

To create a new object in NetBox, find the object type in the navigation menu and click the green "Add" button.

!!! info "Missing Button?"
    If you don't see an "add" button for certain object types, it's likely that your account does not have sufficient permission to create these types. Ask your NetBox administrator to grant the required permissions.
    
    Also note that some object types, such as device components, cannot be created directly from the navigation menu. These must be created within the context of a parent object (such as a parent device).

<!-- TODO: Screenshot -->

## Bulk Import (CSV/YAML)

NetBox supports the bulk import of new objects, and updating of existing objects using CSV-formatted data. This method can be ideal for importing spreadsheet data, which is very easy to convert to CSV data. CSV data can be imported either as raw text using the form field, or by uploading a properly formatted CSV file.

When viewing the CSV import form for an object type, you'll notice that the headers for the required columns have been pre-populated. Each form has a table beneath it titled "CSV Field Options," which lists _all_ supported columns for your reference. (Generally, these map to the fields you see in the corresponding creation form for individual objects.)

<!-- TODO: Screenshot -->

If an "id" field is added the data will be used to update existing records instead of importing new objects.

Note that some models (namely device types and module types) do not support CSV import. Instead, they accept YAML-formatted data to facilitate the import of both the parent object as well as child components.

## Scripting

Sometimes you'll find that data you need to populate in NetBox can be easily reduced to a pattern. For example, suppose you have one hundred branch sites and each site gets five VLANs, numbered 101 through 105. While it's certainly possible to explicitly define each of these 500 VLANs in a CSV file for import, it may be quicker to draft a simple custom script to automatically create these VLANs according to the pattern. This ensures a high degree of confidence in the validity of the data, since it's impossible for a script to "miss" a VLAN here or there.

!!! tip "Reconstruct Existing Data with Scripts"
    Sometimes, you might want to write a script to populate objects even if you have the necessary data ready for import. This is because using a script eliminates the need to manually verify existing data prior to import.

## REST API

You can also use the REST API to facilitate the population of data in NetBox. The REST API offers full programmatic control over the creation of objects, subject to the same validation rules enforced by the UI forms. Additionally, the REST API supports the bulk creation of multiple objects using a single request.

For more information about this option, see the [REST API documentation](../integrations/rest-api.md).
