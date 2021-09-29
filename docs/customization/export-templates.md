{!models/extras/exporttemplate.md!}

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
