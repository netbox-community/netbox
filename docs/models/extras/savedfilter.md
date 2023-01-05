# Saved Filters

When filtering lists of objects in NetBox, users can save applied filters for future use. This is handy for complex filter strategies involving multiple discrete filters. For example, you might want to find all planned devices within a region that have a specific platform. Once you've applied the desired filters to the object list, simply create a saved filter with name and optional description. This filter can then be applied directly for future queries via both the UI and REST API.

## Fields

### Name

The filter's human-friendly name.

### Slug

The unique identifier by which this filter will be referenced during application (e.g. `?filter=my-slug`).

### User

The user to which this filter belongs. The current user will be assigned automatically when creating saved filters via the UI, and cannot be changed.

### Weight

A numeric weight used to override alphabetic ordering of filters by name. Saved filters with a lower weight will be listed before those with a higher weight.

### Enabled

Determines whether this filter can be used. Disabled filters will not appear as options in the UI, however they will be included in API results.

### Shared

Determines whether this filter is intended for use by all users or only its owner. Note that disabling this field does **not** hide the filter from other users; it is merely excluded from the list of available filters in UI object list views.

### Parameters

The query parameters to apply when the filter is active. These must be specified as JSON data. For example, the URL query string

```
?status=active&region_id=51&tag=alpha&tag=bravo
```

is represented in JSON as

```json
{
  "tag": ["alpha", "bravo"],
  "status": "active",
  "region_id": 51
}
```
