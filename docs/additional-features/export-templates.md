# Export Templates

NetBox allows users to define custom templates that can be used when exporting objects. To create an export template, navigate to Extras > Export Templates under the admin interface.

Each export template is associated with a certain type of object. For instance, if you create an export template for VLANs, your custom template will appear under the "Export" button on the VLANs list.

Export templates may be written in Jinja2 or [Django's template language](https://docs.djangoproject.com/en/stable/ref/templates/language/), which is very similar to Jinja2.

!!! warning
    Support for Django's native templating logic will be removed in NetBox v2.10.

The list of objects returned from the database when rendering an export template is stored in the `queryset` variable, which you'll typically want to iterate through using a `for` loop. Object properties can be access by name. For example:

```jinja2
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
