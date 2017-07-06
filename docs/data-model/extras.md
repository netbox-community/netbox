This section entails features of NetBox which are not crucial to its primary functions, but provide additional value.

# Custom Fields

Each object in NetBox is represented in the database as a discrete table, and each attribute of an object exists as a column within its table. For example, sites are stored in the `dcim_site` table, which has columns named `name`, `facility`, `physical_address`, and so on. As new attributes are added to objects throughout the development of NetBox, tables are expanded to include new rows.

However, some users might want to associate with objects attributes that are somewhat esoteric in nature, and that would not make sense to include in the core NetBox database schema. For instance, suppose your organization needs to associate each device with a ticket number pointing to the support ticket that was opened to have it installed. This is certainly a legitimate use for NetBox, but it's perhaps not a common enough need to warrant expanding the internal data schema. Instead, you can create a custom field to hold this data.

Custom fields must be created through the admin UI under Extras > Custom Fields. To create a new custom field, select the object(s) to which you want it to apply, and the type of field it will be. NetBox supports six field types:

* Free-form text (up to 255 characters)
* Integer
* Boolean (true/false)
* Date
* URL
* Selection

Assign the field a name. This should be a simple database-friendly string, e.g. `tps_report`. You may optionally assign the field a human-friendly label (e.g. "TPS report") as well; the label will be displayed on forms. If a description is provided, it will appear beneath the field in a form.

Marking the field as required will require the user to provide a value for the field when creating a new object or when saving an existing object. A default value for the field may also be provided. Use "true" or "false" for boolean fields. (The default value has no effect for selection fields.)

When creating a selection field, you should create at least two choices. These choices will be arranged first by weight, with lower weights appearing higher in the list, and then alphabetically.

## Using Custom Fields

When a single object is edited, the form will include any custom fields which have been defined for the object type. These fields are included in the "Custom Fields" panel. On the backend, each custom field value is saved separately from the core object as an independent database call, so it's best to avoid adding too many custom fields per object.

When editing multiple objects, custom field values are saved in bulk. There is no significant difference in overhead when saving a custom field value for 100 objects versus one object. However, the bulk operation must be performed separately for each custom field.

# Export Templates

NetBox allows users to define custom templates that can be used when exporting objects. To create an export template, navigate to Extras > Export Templates under the admin interface.

Each export template is associated with a certain type of object. For instance, if you create an export template for VLANs, your custom template will appear under the "Export" button on the VLANs list.

Export templates are written in [Django's template language](https://docs.djangoproject.com/en/1.9/ref/templates/language/), which is very similar to Jinja2. The list of objects returned from the database is stored in the `queryset` variable, which you'll typically want to iterate through using a `for` loop. Object properties can be access by name. For example:

```
{% for rack in queryset %}
Rack: {{ rack.name }}
Site: {{ rack.site.name }}
Height: {{ rack.u_height }}U
{% endfor %}
```

To access custom fields of an object within a template, use the `cf` attribute. For example, `{{ obj.cf.color }}` will return the value (if any) for a custom field named `color` on `obj`.

A MIME type and file extension can optionally be defined for each export template. The default MIME type is `text/plain`.

## Example

Here's an example device export template that will generate a simple Nagios configuration from a list of devices.

```
{% for device in queryset %}{% if device.status and device.primary_ip %}define host{
        use                     generic-switch
        host_name               {{ device.name }}
        address                 {{ device.primary_ip.address.ip }}
}
{% endif %}{% endfor %}
```

The generated output will look something like this:

```
define host{
        use                     generic-switch
        host_name               switch1
        address                 192.0.2.1
}
define host{
        use                     generic-switch
        host_name               switch2
        address                 192.0.2.2
}
define host{
        use                     generic-switch
        host_name               switch3
        address                 192.0.2.3
}
```

# Graphs

NetBox does not have the ability to generate graphs natively, but this feature allows you to embed contextual graphs from an external resources (such as a monitoring system) inside the site, provider, and interface views. Each embedded graph must be defined with the following parameters:

* **Type:** Site, provider, or interface. This determines in which view the graph will be displayed.
* **Weight:** Determines the order in which graphs are displayed (lower weights are displayed first). Graphs with equal weights will be ordered alphabetically by name.
* **Name:** The title to display above the graph.
* **Source URL:** The source of the image to be embedded. The associated object will be available as a template variable named `obj`.
* **Link URL (optional):** A URL to which the graph will be linked. The associated object will be available as a template variable named `obj`.

## Examples

You only need to define one graph object for each graph you want to include when viewing an object. For example, if you want to include a graph of traffic through an interface over the past five minutes, your graph source might looks like this:

```
https://my.nms.local/graphs/?node={{ obj.device.name }}&interface={{ obj.name }}&duration=5m
```

You can define several graphs to provide multiple contexts when viewing an object. For example:

```
https://my.nms.local/graphs/?type=throughput&node={{ obj.device.name }}&interface={{ obj.name }}&duration=60m
https://my.nms.local/graphs/?type=throughput&node={{ obj.device.name }}&interface={{ obj.name }}&duration=24h
https://my.nms.local/graphs/?type=errors&node={{ obj.device.name }}&interface={{ obj.name }}&duration=60m
```

# Topology Maps

NetBox can generate simple topology maps from the physical network connections recorded in its database. First, you'll need to create a topology map definition under the admin UI at Extras > Topology Maps.

Each topology map is associated with a site. A site can have multiple topology maps, which might each illustrate a different aspect of its infrastructure (for example, production versus backend infrastructure).

To define the scope of a topology map, decide which devices you want to include. The map will only include interface connections with both points terminated on an included device. Specify the devices to include in the **device patterns** field by entering a list of [regular expressions](https://en.wikipedia.org/wiki/Regular_expression) matching device names. For example, if you wanted to include "mgmt-switch1" through "mgmt-switch99", you might use the regex `mgmt-switch\d+`.

Each line of the **device patterns** field represents a hierarchical layer within the topology map. For example, you might map a traditional network with core, distribution, and access tiers like this:

```
core-switch-[abcd]
dist-switch\d
access-switch\d+;oob-switch\d+
```

Note that you can combine multiple regexes onto one line using semicolons. The order in which regexes are listed on a line is significant: devices matching the first regex will be rendered first, and subsequent groups will be rendered to the right of those.

# Image Attachments

Certain objects within NetBox (namely sites, racks, and devices) can have photos or other images attached to them. (Note that _only_ image files are supported.) Each attachment may optionally be assigned a name; if omitted, the attachment will be represented by its file name.

!!! note
    If you experience a server error while attempting to upload an image attachment, verify that the system user NetBox runs as has write permission to the media root directory (`netbox/media/`).
