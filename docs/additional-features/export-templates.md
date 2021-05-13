# Export Templates

NetBox allows users to define custom templates that can be used when exporting objects. To create an export template, navigate to Extras > Export Templates under the admin interface.

Each export template is associated with a certain type of object. For instance, if you create an export template for VLANs, your custom template will appear under the "Export" button on the VLANs list. Each export template must have a name, and may optionally designate a specific export [MIME type](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types) and/or file extension.

!!! note
    The name `table` is reserved for internal use.

Export templates must be written in [Jinja2](https://jinja.palletsprojects.com/).

The list of objects returned from the database when rendering an export template is stored in the `queryset` variable, which you'll typically want to iterate through using a `for` loop. Object properties can be access by name. For example:

```jinja2
{% for rack in queryset %}
Rack: {{ rack.name }}
Site: {{ rack.site.name }}
Height: {{ rack.u_height }}U
{% endfor %}
```

To access custom fields of an object within a template, use the `cf` attribute. For example, `{{ obj.cf.color }}` will return the value (if any) for a custom field named `color` on `obj`.

If you need to use the config context data in an export template, you'll should use the function `get_config_context` to get all the config context data. For example:
```
{% for server in queryset %}
{% set data = server.get_config_context() %}
{{ data.syslog }}
{% endfor %}
```

The `as_attachment` attribute of an export template controls its behavior when rendered. If true, the rendered content will be returned to the user as a downloadable file. If false, it will be displayed within the browser. (This may be handy e.g. for generating HTML content.)

A MIME type and file extension can optionally be defined for each export template. The default MIME type is `text/plain`.

## REST API Integration

When it is necessary to provide authentication credentials (such as when [`LOGIN_REQUIRED`](../configuration/optional-settings.md#login_required) has been enabled), it is recommended to render export templates via the REST API. This allows the client to specify an authentication token. To render an export template via the REST API, make a `GET` request to the model's list endpoint and append the `export` parameter specifying the export template name. For example:

```
GET /api/dcim/sites/?export=MyTemplateName
```

Note that the body of the response will contain only the rendered export template content, as opposed to a JSON object or list.

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
