# Tags

Tags are free-form text labels which can be applied to a variety of objects within NetBox. Tags are created on-demand as they are assigned to objects. Use commas to separate tags when adding multiple tags to an object 9for example: `Inventoried, Monitored`). Use double quotes around a multi-word tag when adding only one tag, e.g. `"Core Switch"`.

Each tag has a label and a URL-friendly slug. For example, the slug for a tag named "Dunder Mifflin, Inc." would be `dunder-mifflin-inc`. The slug is generated automatically and makes tags easier to work with as URL parameters.

Objects can be filtered by the tags they have applied. For example, the following API request will retrieve all devices tagged as "monitored":

```
GET /api/dcim/devices/?tag=monitored
```

Tags are included in the API representation of an object as a list of plain strings:

```
{
    ...
    "tags": [
        "Core Switch",
        "Monitored"
    ],
    ...
}
```
