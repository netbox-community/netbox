# REST API Overview

## What is a REST API?

REST stands for [representational state transfer](https://en.wikipedia.org/wiki/Representational_state_transfer). It's a particular type of API which employs HTTP requests and [JavaScript Object Notation (JSON)](http://www.json.org/) to facilitate create, retrieve, update, and delete (CRUD) operations on objects within an application. Each type of operation is associated with a particular HTTP verb:

* `GET`: Retrieve an object or list of objects
* `POST`: Create an object
* `PUT` / `PATCH`: Modify an existing object. `PUT` requires all mandatory fields to be specified, while `PATCH` only expects the field that is being modified to be specified.
* `DELETE`: Delete an existing object

Additionally, the `OPTIONS` verb can be used to inspect a particular REST API endpoint and return all supported actions and their available parameters.

One of the primary benefits of a REST API is its human-friendliness. Because it utilizes HTTP and JSON, it's very easy to interact with NetBox data on the command line using common tools. For example, we can request an IP address from NetBox and output the JSON using `curl` and `jq`. The following command makes an HTTP `GET` request for information about a particular IP address, identified by its primary key, and uses `jq` to present the raw JSON data returned in a more human-friendly format. (Piping the output through `jq` isn't strictly required but makes it much easier to read.)

```no-highlight
curl -s http://netbox/api/ipam/ip-addresses/2954/ | jq '.'
```

```json
{
  "id": 2954,
  "url": "http://netbox/api/ipam/ip-addresses/2954/",
  "family": {
    "value": 4,
    "label": "IPv4"
  },
  "address": "192.168.0.42/26",
  "vrf": null,
  "tenant": null,
  "status": {
    "value": "active",
    "label": "Active"
  },
  "role": null,
  "assigned_object_type": "dcim.interface",
  "assigned_object_id": 114771,
  "assigned_object": {
    "id": 114771,
    "url": "http://netbox/api/dcim/interfaces/114771/",
    "device": {
      "id": 2230,
      "url": "http://netbox/api/dcim/devices/2230/",
      "name": "router1",
      "display_name": "router1"
    },
    "name": "et-0/1/2",
    "cable": null,
    "connection_status": null
  },
  "nat_inside": null,
  "nat_outside": null,
  "dns_name": "",
  "description": "Example IP address",
  "tags": [],
  "custom_fields": {},
  "created": "2020-08-04",
  "last_updated": "2020-08-04T14:12:39.666885Z"
}
```

Each attribute of the IP address is expressed as an attribute of the JSON object. Fields may include their own nested objects, as in the case of the `assigned_object` field above. Every object includes a primary key named `id` which uniquely identifies it in the database.

## Interactive Documentation

Comprehensive, interactive documentation of all REST API endpoints is available on a running NetBox instance at `/api/docs/`. This interface provides a convenient sandbox for researching and experimenting with specific endpoints and request types. The API itself can also be explored using a web browser by navigating to its root at `/api/`.

## Endpoint Hierarchy

NetBox's entire REST API is housed under the API root at `https://<hostname>/api/`. The URL structure is divided at the root level by application: circuits, DCIM, extras, IPAM, plugins, secrets, tenancy, users, and virtualization. Within each application exists a separate path for each model. For example, the provider and circuit objects are located under the "circuits" application:

* `/api/circuits/providers/`
* `/api/circuits/circuits/`

Likewise, the site, rack, and device objects are located under the "DCIM" application:

* `/api/dcim/sites/`
* `/api/dcim/racks/`
* `/api/dcim/devices/`

The full hierarchy of available endpoints can be viewed by navigating to the API root in a web browser.

Each model generally has two views associated with it: a list view and a detail view. The list view is used to retrieve a list of multiple objects and to create new objects. The detail view is used to retrieve, update, or delete an single existing object. All objects are referenced by their numeric primary key (`id`).

* `/api/dcim/devices/` - List existing devices or create a new device
* `/api/dcim/devices/123/` - Retrieve, update, or delete the device with ID 123

Lists of objects can be filtered using a set of query parameters. For example, to find all interfaces belonging to the device with ID 123:

```
GET /api/dcim/interfaces/?device_id=123
```

See the [filtering documentation](filtering.md) for more details.

## Serialization

The REST API employs two types of serializers to represent model data: base serializers and nested serializers. The base serializer is used to present the complete view of a model. This includes all database table fields which comprise the model, and may include additional metadata. A base serializer includes relationships to parent objects, but **does not** include child objects. For example, the `VLANSerializer` includes a nested representation its parent VLANGroup (if any), but does not include any assigned Prefixes.

```json
{
    "id": 1048,
    "site": {
        "id": 7,
        "url": "http://netbox/api/dcim/sites/7/",
        "name": "Corporate HQ",
        "slug": "corporate-hq"
    },
    "group": {
        "id": 4,
        "url": "http://netbox/api/ipam/vlan-groups/4/",
        "name": "Production",
        "slug": "production"
    },
    "vid": 101,
    "name": "Users-Floor1",
    "tenant": null,
    "status": {
        "value": 1,
        "label": "Active"
    },
    "role": {
        "id": 9,
        "url": "http://netbox/api/ipam/roles/9/",
        "name": "User Access",
        "slug": "user-access"
    },
    "description": "",
    "display_name": "101 (Users-Floor1)",
    "custom_fields": {}
}
```

### Related Objects

Related objects (e.g. `ForeignKey` fields) are represented using nested serializers. A nested serializer provides a minimal representation of an object, including only its direct URL and enough information to display the object to a user. When performing write API actions (`POST`, `PUT`, and `PATCH`), related objects may be specified by either numeric ID (primary key), or by a set of attributes sufficiently unique to return the desired object.

For example, when creating a new device, its rack can be specified by NetBox ID (PK):

```json
{
    "name": "MyNewDevice",
    "rack": 123,
    ...
}
```

Or by a set of nested attributes which uniquely identify the rack:

```json
{
    "name": "MyNewDevice",
    "rack": {
        "site": {
            "name": "Equinix DC6"
        },
        "name": "R204"
    },
    ...
}
```

Note that if the provided parameters do not return exactly one object, a validation error is raised.

### Generic Relations

Some objects within NetBox have attributes which can reference an object of multiple types, known as _generic relations_. For example, an IP address can be assigned to either a device interface _or_ a virtual machine interface. When making this assignment via the REST API, we must specify two attributes:

* `assigned_object_type` - The content type of the assigned object, defined as `<app>.<model>`
* `assigned_object_id` - The assigned object's unique numeric ID

Together, these values identify a unique object in NetBox. The assigned object (if any) is represented by the `assigned_object` attribute on the IP address model.

```no-highlight
curl -X POST \
-H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json; indent=4" \
http://netbox/api/ipam/ip-addresses/ \
--data '{
    "address": "192.0.2.1/24",
    "assigned_object_type": "dcim.interface",
    "assigned_object_id": 69023
}'
```

```json
{
    "id": 56296,
    "url": "http://netbox/api/ipam/ip-addresses/56296/",
    "assigned_object_type": "dcim.interface",
    "assigned_object_id": 69000,
    "assigned_object": {
        "id": 69000,
        "url": "http://netbox/api/dcim/interfaces/69023/",
        "device": {
            "id": 2174,
            "url": "http://netbox/api/dcim/devices/2174/",
            "name": "device105",
            "display_name": "device105"
        },
        "name": "ge-0/0/0",
        "cable": null,
        "connection_status": null
    },
    ...
}
```

If we wanted to assign this IP address to a virtual machine interface instead, we would have set `assigned_object_type` to `virtualization.vminterface` and updated the object ID appropriately.

### Brief Format

Most API endpoints support an optional "brief" format, which returns only a minimal representation of each object in the response. This is useful when you need only a list of available objects without any related data, such as when populating a drop-down list in a form. As an example, the default (complete) format of an IP address looks like this:

```
GET /api/ipam/prefixes/13980/

{
    "id": 13980,
    "url": "http://netbox/api/ipam/prefixes/13980/",
    "family": {
        "value": 4,
        "label": "IPv4"
    },
    "prefix": "192.0.2.0/24",
    "site": {
        "id": 3,
        "url": "http://netbox/api/dcim/sites/17/",
        "name": "Site 23A",
        "slug": "site-23a"
    },
    "vrf": null,
    "tenant": null,
    "vlan": null,
    "status": {
        "value": "container",
        "label": "Container"
    },
    "role": {
        "id": 17,
        "url": "http://netbox/api/ipam/roles/17/",
        "name": "Staging",
        "slug": "staging"
    },
    "is_pool": false,
    "description": "Example prefix",
    "tags": [],
    "custom_fields": {},
    "created": "2018-12-10",
    "last_updated": "2019-03-01T20:02:46.173540Z"
}
```

The brief format is much more terse:

```
GET /api/ipam/prefixes/13980/?brief=1

{
    "id": 13980,
    "url": "http://netbox/api/ipam/prefixes/13980/",
    "family": 4,
    "prefix": "10.40.3.0/24"
}
```

The brief format is supported for both lists and individual objects.

### Excluding Config Contexts

When retrieving devices and virtual machines via the REST API, each will included its rendered [configuration context data](../models/extras/configcontext/) by default. Users with large amounts of context data will likely observe suboptimal performance when returning multiple objects, particularly with very high page sizes. To combat this, context data may be excluded from the response data by attaching the query parameter `?exclude=config_context` to the request. This parameter works for both list and detail views.

## Pagination

API responses which contain a list of many objects will be paginated for efficiency. The root JSON object returned by a list endpoint contains the following attributes:

* `count`: The total number of all objects matching the query
* `next`: A hyperlink to the next page of results (if applicable)
* `previous`: A hyperlink to the previous page of results (if applicable)
* `results`: The list of objects on the current page

Here is an example of a paginated response:

```
HTTP 200 OK
Allow: GET, POST, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "count": 2861,
    "next": "http://netbox/api/dcim/devices/?limit=50&offset=50",
    "previous": null,
    "results": [
        {
            "id": 231,
            "name": "Device1",
            ...
        },
        {
            "id": 232,
            "name": "Device2",
            ...
        },
        ...
    ]
}
```

The default page is determined by the [`PAGINATE_COUNT`](../../configuration/optional-settings/#paginate_count) configuration parameter, which defaults to 50. However, this can be overridden per request by specifying the desired `offset` and `limit` query parameters. For example, if you wish to retrieve a hundred devices at a time, you would make a request for:

```
http://netbox/api/dcim/devices/?limit=100
```

The response will return devices 1 through 100. The URL provided in the `next` attribute of the response will return devices 101 through 200:

```json
{
    "count": 2861,
    "next": "http://netbox/api/dcim/devices/?limit=100&offset=100",
    "previous": null,
    "results": [...]
}
```

The maximum number of objects that can be returned is limited by the [`MAX_PAGE_SIZE`](../../configuration/optional-settings/#max_page_size) configuration parameter, which is 1000 by default. Setting this to `0` or `None` will remove the maximum limit. An API consumer can then pass `?limit=0` to retrieve _all_ matching objects with a single request.

!!! warning
    Disabling the page size limit introduces a potential for very resource-intensive requests, since one API request can effectively retrieve an entire table from the database.

## Interacting with Objects

### Retrieving Multiple Objects

To query NetBox for a list of objects, make a `GET` request to the model's _list_ endpoint. Objects are listed under the response object's `results` parameter.

```no-highlight
curl -s -X GET http://netbox/api/ipam/ip-addresses/ | jq '.'
```

```json
{
  "count": 42031,
  "next": "http://netbox/api/ipam/ip-addresses/?limit=50&offset=50",
  "previous": null,
  "results": [
    {
      "id": 5618,
      "address": "192.0.2.1/24",
      ...
    },
    {
      "id": 5619,
      "address": "192.0.2.2/24",
      ...
    },
    {
      "id": 5620,
      "address": "192.0.2.3/24",
      ...
    },
    ...
  ]
}
```

### Retrieving a Single Object

To query NetBox for a single object, make a `GET` request to the model's _detail_ endpoint specifying its unique numeric ID.

!!! note
    Note that the trailing slash is required. Omitting this will return a 302 redirect.

```no-highlight
curl -s -X GET http://netbox/api/ipam/ip-addresses/5618/ | jq '.'
```

```json
{
  "id": 5618,
  "address": "192.0.2.1/24",
  ...
}
```

### Creating a New Object

To create a new object, make a `POST` request to the model's _list_ endpoint with JSON data pertaining to the object being created. Note that a REST API token is required for all write operations; see the [authentication documentation](../authentication/) for more information. Also be sure to set the `Content-Type` HTTP header to `application/json`.

```no-highlight
curl -s -X POST \
-H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
http://netbox/api/ipam/prefixes/ \
--data '{"prefix": "192.0.2.0/24", "site": 6}' | jq '.'
```

```json
{
  "id": 18691,
  "url": "http://netbox/api/ipam/prefixes/18691/",
  "family": {
    "value": 4,
    "label": "IPv4"
  },
  "prefix": "192.0.2.0/24",
  "site": {
    "id": 6,
    "url": "http://netbox/api/dcim/sites/6/",
    "name": "US-East 4",
    "slug": "us-east-4"
  },
  "vrf": null,
  "tenant": null,
  "vlan": null,
  "status": {
    "value": "active",
    "label": "Active"
  },
  "role": null,
  "is_pool": false,
  "description": "",
  "tags": [],
  "custom_fields": {},
  "created": "2020-08-04",
  "last_updated": "2020-08-04T20:08:39.007125Z"
}
```

### Creating Multiple Objects

To create multiple instances of a model using a single request, make a `POST` request to the model's _list_ endpoint with a list of JSON objects representing each instance to be created. If successful, the response will contain a list of the newly created instances. The example below illustrates the creation of three new sites.

```no-highlight
curl -X POST -H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json; indent=4" \
http://netbox/api/dcim/sites/ \
--data '[
{"name": "Site 1", "slug": "site-1", "region": {"name": "United States"}},
{"name": "Site 2", "slug": "site-2", "region": {"name": "United States"}},
{"name": "Site 3", "slug": "site-3", "region": {"name": "United States"}}
]'
```

```json
[
    {
        "id": 21,
        "url": "http://netbox/api/dcim/sites/21/",
        "name": "Site 1",
        ...
    },
    {
        "id": 22,
        "url": "http://netbox/api/dcim/sites/22/",
        "name": "Site 2",
        ...
    },
    {
        "id": 23,
        "url": "http://netbox/api/dcim/sites/23/",
        "name": "Site 3",
        ...
    }
]
```

### Updating an Object

To modify an object which has already been created, make a `PATCH` request to the model's _detail_ endpoint specifying its unique numeric ID. Include any data which you wish to update on the object. As with object creation, the `Authorization` and `Content-Type` headers must also be specified.

```no-highlight
curl -s -X PATCH \
-H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
http://netbox/api/ipam/prefixes/18691/ \
--data '{"status": "reserved"}' | jq '.'
```

```json
{
  "id": 18691,
  "url": "http://netbox/api/ipam/prefixes/18691/",
  "family": {
    "value": 4,
    "label": "IPv4"
  },
  "prefix": "192.0.2.0/24",
  "site": {
    "id": 6,
    "url": "http://netbox/api/dcim/sites/6/",
    "name": "US-East 4",
    "slug": "us-east-4"
  },
  "vrf": null,
  "tenant": null,
  "vlan": null,
  "status": {
    "value": "reserved",
    "label": "Reserved"
  },
  "role": null,
  "is_pool": false,
  "description": "",
  "tags": [],
  "custom_fields": {},
  "created": "2020-08-04",
  "last_updated": "2020-08-04T20:14:55.709430Z"
}
```

!!! note "PUT versus PATCH"
    The NetBox REST API support the use of either `PUT` or `PATCH` to modify an existing object. The difference is that a `PUT` request requires the user to specify a _complete_ representation of the object being modified, whereas a `PATCH` request need include only the attributes that are being updated. For most purposes, using `PATCH` is recommended.

### Updating Multiple Objects

Multiple objects can be updated simultaneously by issuing a `PUT` or `PATCH` request to a model's list endpoint with a list of dictionaries specifying the numeric ID of each object to be deleted and the attributes to be updated. For example, to update sites with IDs 10 and 11 to a status of "active", issue the following request:

```no-highlight
curl -s -X PATCH \
-H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
http://netbox/api/dcim/sites/ \
--data '[{"id": 10, "status": "active"}, {"id": 11, "status": "active"}]'
```

Note that there is no requirement for the attributes to be identical among objects. For instance, it's possible to update the status of one site along with the name of another in the same request.

!!! note
    The bulk update of objects is an all-or-none operation, meaning that if NetBox fails to successfully update any of the specified objects (e.g. due a validation error), the entire operation will be aborted and none of the objects will be updated.

### Deleting an Object

To delete an object from NetBox, make a `DELETE` request to the model's _detail_ endpoint specifying its unique numeric ID. The `Authorization` header must be included to specify an authorization token, however this type of request does not support passing any data in the body.

```no-highlight
curl -s -X DELETE \
-H "Authorization: Token $TOKEN" \
http://netbox/api/ipam/prefixes/18691/
```

Note that `DELETE` requests do not return any data: If successful, the API will return a 204 (No Content) response.

!!! note
    You can run `curl` with the verbose (`-v`) flag to inspect the HTTP response codes.

### Deleting Multiple Objects

NetBox supports the simultaneous deletion of multiple objects of the same type by issuing a `DELETE` request to the model's list endpoint with a list of dictionaries specifying the numeric ID of each object to be deleted. For example, to delete sites with IDs 10, 11, and 12, issue the following request:

```no-highlight
curl -s -X DELETE \
-H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
http://netbox/api/dcim/sites/ \
--data '[{"id": 10}, {"id": 11}, {"id": 12}]'
```

!!! note
    The bulk deletion of objects is an all-or-none operation, meaning that if NetBox fails to delete any of the specified objects (e.g. due a dependency by a related object), the entire operation will be aborted and none of the objects will be deleted.
