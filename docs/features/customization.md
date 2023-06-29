# Customization

While NetBox strives to meet the needs of every network, the needs of users to cater to their own unique environments cannot be ignored. NetBox was built with this in mind, and can be customized in many ways to better suit your particular needs.

## Tags

Most objects in NetBox can be assigned user-created tags to aid with organization and filtering. Tag values are completely arbitrary: They may be used to store data in key-value pairs, or they may be employed simply as labels against which objects can be filtered. Each tag can also be assigned a color for quicker differentiation in the user interface.

Objects can be filtered by the tags they have applied. For example, the following API request will retrieve all devices tagged as "monitored":

```no-highlight
GET /api/dcim/devices/?tag=monitored
```

The `tag` filter can be specified multiple times to match only objects which have _all_ the specified tags assigned:

```no-highlight
GET /api/dcim/devices/?tag=monitored&tag=deprecated
```

## Bookmarks

Users can bookmark their most commonly visited objects for convenient access. Bookmarks are listed under a user's profile, and can be displayed with custom filtering and ordering on the user's personal dashboard.

## Custom Fields

While NetBox provides a rather extensive data model out of the box, the need may arise to store certain additional data associated with NetBox objects. For example, you might need to record the invoice ID alongside an installed device, or record an approving authority when creating a new IP prefix. NetBox administrators can create custom fields on built-in objects to meet these needs.

NetBox supports many types of custom field, from basic data types like strings and integers, to complex structures like selection lists or raw JSON. It's even possible to add a custom field which references other NetBox objects. Custom field data is stored directly alongside the object to which it is applied in the database, which ensures minimal performance impact. And custom field data can be written and read via the REST API, just like built-in fields.

To learn more about this feature, check out the [custom field documentation](../customization/custom-fields.md).

## Custom Links

Custom links allow you to conveniently reference external resources related to NetBox objects from within the NetBox UI. For example, you might wish to link each virtual machine modeled in NetBox to its corresponding view in some orchestration application. You can do this by creating a templatized custom link for the virtual machine model, specifying something like the following for the link URL:

```no-highlight
http://server.local/vms/?name={{ object.name }}
```

Now, when viewing a virtual machine in NetBox, a user will see a handy button with the chosen title and link (complete with the name of the VM being viewed). Both the text and URL of custom links can be templatized in this manner, and custom links can be grouped together into dropdowns for more efficient display.

To learn more about this feature, check out the [custom link documentation](../customization/custom-links.md).

## Custom Validation

While NetBox employs robust built-in object validation to ensure the integrity of its database, you might wish to enforce additional rules governing the creation and modification of certain objects. For example, perhaps you require that every device defined in NetBox adheres to a particular naming scheme and includes an asset tag. You can configure a custom validation rule in NetBox to enforce these requirements for the device model:

```python
CUSTOM_VALIDATORS = {
    "dcim.device": [
        {
            "name": {
                "regex": "[a-z]+\d{3}"
            },
            "asset_tag": {
                "required": True
            }
        }
    ]
}
```

To learn more about this feature, check out the [custom validation documentation](../customization/custom-validation.md).

## Export Templates

Most NetBox objects can be exported in bulk in two built-in CSV formats: The current view (what the user currently sees in the objects list), or all available data. NetBox also provides the capability to define your own custom data export formats via export templates. An export template is essentially [Jinja2](https://jinja.palletsprojects.com/) template code associated with a particular object type. From the objects list in the NetBox UI, a user can select any of the created export templates to export the objects according to the template logic.

An export template doesn't have to render CSV data: Its output can be in any character-based format. For example, you might want to render data using tabs as delimiters, or even create DNS address records directly from the IP addresses list. Export templates are a great way to get the data you need in the format you need quickly.

To learn more about this feature, check out the [export template documentation](../customization/export-templates.md).

## Reports

NetBox administrators can install custom Python scripts, known as _reports_, which run within NetBox and can be executed and analyzed within the NetBox UI. Reports are a great way to evaluate NetBox objects against a set of arbitrary rules. For example, you could write a report to check that every router has a loopback interface with an IP address assigned, or that every site has a minimum set of VLANs defined.

When a report runs, its logs messages pertaining to the operations being performed, and will ultimately result in either a pass or fail. Reports can be executed via the UI, REST API, or CLI (as a management command). They can be run immediately or scheduled to run at a future time.

To learn more about this feature, check out the [documentation for reports](../customization/reports.md).

## Custom Scripts

Custom scripts are similar to reports, but more powerful. A custom script can prompt the user for input via a form (or API data), and is built to do much more than just reporting. Custom scripts are generally used to automate tasks, such as the population of new objects in NetBox, or exchanging data with external systems. As with reports, they can be run via the UI, REST API, or CLI, and be scheduled to execute at a future time.

The complete Python environment is available to a custom script, including all of NetBox's internal mechanisms: There are no artificial restrictions on what a script can do. As such, custom scripting is considered an advanced feature and requires sufficient familiarity with Python and NetBox's data model.

To learn more about this feature, check out the [documentation for custom scripts](../customization/custom-scripts.md).
