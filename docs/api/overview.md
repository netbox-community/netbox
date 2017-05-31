NetBox v2.0 and later includes a full-featured REST API that allows its data model to be read and manipulated externally.

# URL Hierarchy

NetBox's entire REST API is housed under the API root, `/api/`. The API's URL structure is divided at the root level by application: circuits, DCIM, extras, IPAM, secrets, and tenancy. Within each application, each model has its own path. For example, the provider and circuit objects are located under the "circuits" application:

* /api/circuits/providers/
* /api/circuits/circuits/

Likewise, the site, rack, and device objects are located under the "DCIM" application:

* /api/dcim/sites/
* /api/dcim/racks/
* /api/dcim/devices/

The full hierarchy of available endpoints can be viewed by navigating to the API root (e.g. /api/) in a web browser.

Each model generally has two URLs associated with it: a list URL and a detail URL. The list URL is used to request a list of multiple objects or to create a new object. The detail URL is used to retrieve, update, or delete an existing object. All objects are referenced by their numeric primary key (ID).

* /api/dcim/devices/ - List devices or create a new device
* /api/dcim/devices/123/ - Retrieve, update, or delete the device with ID 123

Lists of objects can be filtered using a set of query parameters. For example, to find all interfaces belonging to the device with ID 123:

```
GET /api/dcim/interfaces/?device_id=123
```

# Serialization

The NetBox API employs three types of serializers to represent model data:

* Base serializer
* Nested serializer
* Writable serializer

The base serializer is used to represent the default view of a model. This includes all database table fields which comprise the model, and may include additional metadata. A base serializer includes relationships to parent objects, but **does not** include child objects. For example, the `VLANSerializer` includes a nested representation its parent VLANGroup (if any), but does not include any assigned Prefixes.

```
{
    "id": 1048,
    "site": {
        "id": 7,
        "url": "http://localhost:8000/api/dcim/sites/7/",
        "name": "Corporate HQ",
        "slug": "corporate-hq"
    },
    "group": {
        "id": 4,
        "url": "http://localhost:8000/api/ipam/vlan-groups/4/",
        "name": "Production",
        "slug": "production"
    },
    "vid": 101,
    "name": "Users-Floor1",
    "tenant": null,
    "status": [
        1,
        "Active"
    ],
    "role": {
        "id": 9,
        "url": "http://localhost:8000/api/ipam/roles/9/",
        "name": "User Access",
        "slug": "user-access"
    },
    "description": "",
    "display_name": "101 (Users-Floor1)",
    "custom_fields": {}
}
```

Related objects (e.g. `ForeignKey` fields) are represented using a nested serializer. A nested serializer provides a minimal representation of an object, including only its URL and enough information to construct its name.

When a base serializer includes one or more nested serializers, the hierarchical structure precludes it from being used for write operations. Thus, a flat representation of an object may be provided using a writable serializer. This serializer includes only raw database values and is not typically used for retrieval, except as part of the response to the creation or updating of an object.

```
{
    "id": 1201,
    "site": 7,
    "group": 4,
    "vid": 102,
    "name": "Users-Floor2",
    "tenant": null,
    "status": 1,
    "role": 9,
    "description": ""
}
```

# Pagination

API responses which contain a list of objects (for example, a request to `/api/dcim/devices/`) will be paginated to avoid unnecessary overhead. The root JSON object will contain the following attributes:

* `count`: The total count of all objects matching the query
* `next`: A hyperlink to the next page of results (if applicable)
* `previous`: A hyperlink to the previous page of results (if applicable)
* `results`: The list of returned objects

Here is an example of a paginated response:

```
HTTP 200 OK
Allow: GET, POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "count": 2861,
    "next": "http://localhost:8000/api/dcim/devices/?limit=50&offset=50",
    "previous": null,
    "results": [
        {
            "id": 123,
            "name": "DeviceName123",
            ...
        },
        ...
    ]
}
```

The default page size derives from the [`PAGINATE_COUNT`](../configuration/optional-settings/#paginate_count) configuration setting, which defaults to 50. However, this can be overridden per request by specifying the desired `offset` and `limit` query parameters. For example, if you wish to retrieve a hundred devices at a time, you would make a request for:

```
http://localhost:8000/api/dcim/devices/?limit=100
```

The response will return devices 1 through 100. The URL provided in the `next` attribute of the response will return devices 101 through 200:

```
{
    "count": 2861,
    "next": "http://localhost:8000/api/dcim/devices/?limit=100&offset=100",
    "previous": null,
    "results": [...]
}
```

The maximum number of objects that can be returned is limited by the [`MAX_PAGE_SIZE`](../configuration/optional-settings/#max_page_size) setting, which is 1000 by default. Setting this to `0` or `None` will remove the maximum limit. An API consumer can then pass `?limit=0` to retrieve _all_ matching objects with a single request.

!!! warning
    Disabling the page size limit introduces a potential for very resource-intensive requests, since one API request can effectively retrieve an entire table from the database.
