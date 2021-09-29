{!models/extras/customfield.md!}

## Custom Fields in Templates

Several features within NetBox, such as export templates and webhooks, utilize Jinja2 templating. For convenience, objects which support custom field assignment expose custom field data through the `cf` property. This is a bit cleaner than accessing custom field data through the actual field (`custom_field_data`).

For example, a custom field named `foo123` on the Site model is accessible on an instance as `{{ site.cf.foo123 }}`.

## Custom Fields and the REST API

When retrieving an object via the REST API, all of its custom data will be included within the `custom_fields` attribute. For example, below is the partial output of a site with two custom fields defined:

```json
{
    "id": 123,
    "url": "http://localhost:8000/api/dcim/sites/123/",
    "name": "Raleigh 42",
    ...
    "custom_fields": {
        "deployed": "2018-06-19",
        "site_code": "US-NC-RAL42"
    },
    ...
```

To set or change these values, simply include nested JSON data. For example:

```json
{
    "name": "New Site",
    "slug": "new-site",
    "custom_fields": {
        "deployed": "2019-03-24"
    }
}
```
