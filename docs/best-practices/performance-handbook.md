# Performance Handbook

The purpose of this handbook is to help users and administrators use NetBox efficiently. It contains assorted recommendations and best practices compiled over time, intending to serve a wide variety of use cases. 

## Server Configuration

### WSGI Server Configuration

NetBox operates as a [Web Server Gateway Interface (WSGI)](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) application, which sits behind a frontend HTTP server such as nginx or Apache. The HTTP server handles low-level HTTP request processing and serving static assets, and forwards application-level requests to NetBox via WSGI.

A backend WSGI server (typically [Gunicorn](https://gunicorn.org/) or [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/)) is responsible for running the NetBox application. This is accomplished by initializing a number of WSGI worker processes which accept WSGI requests relayed from the frontend HTTP server.

Tuning your WSGI server is crucial to realizing optimal performance from NetBox. Below are some recommended configuration parameters.

#### Provision Multiple Workers

General guidance is to set the number of worker processes to double the number of CPU cores available, plus one (`2 * CPUs + 1`).

#### Limit the Worker Lifetime

Set a maximum number of requests that a worker can service before being respawned. This helps protect against potential memory leaks.

#### Set a Request Timeout

Limit the time a worker may spend processing any request. This prevents a long-running request from tying up a worker beyond an acceptable threshold. We suggest a limit of 120 seconds as a reasonable safeguard.

#### Bind Using a Unix Socket

When running the HTTP frontend and WSGI server on the same machine, binding via a Unix socket (instead of a TCP socket) may yield slight performance gains.

### NetBox Configuration

NetBox ships with a reasonable default configuration for most environments, but administrators are encouraged to explore all the [available parameters](../configuration/index.md) to tune their installation. Some of the most notable parameters impacting performance are called out below.

#### Reduce the Maximum Page Size

NetBox paginates large result sets to reduce the overall response size. The [`MAX_PAGE_SIZE`](../configuration/miscellaneous.md#max_page_size) parameter specifies the maximum number of results per page that a client can request. This is set to 1,000 by default. Consider lowering this number if you find that API clients are frequently requesting very large result sets.

#### Limit GraphQL Aliases

By default, NetBox restricts a GraphQL query to 10 aliases. Consider reducing this number by setting [`GRAPHQL_MAX_ALIASES`](../configuration/graphql-api.md#graphql_max_aliases) to a lower value.

#### Designate Isolated Deployments

If your NetBox installation does not have Internet access, set [`ISOLATED_DEPLOYMENT`](../configuration/system.md#isolated_deployment) to True. This will prevent the application from attempting routine external requests.

#### Reduce Sentry Sampling

If [Sentry](https://sentry.io/) has been enabled for error reporting and analytics, consider lowering its sampling rate. This can be accomplished by modifying the values for `sample_rate` and `traces_sample_rate` under [`SENTRY_CONFIG`](../configuration/error-reporting.md#sentry_config).

#### Remove Unneeded Event Handlers

Check whether any custom event handlers have been added under [`EVENTS_PIPELINE`](../configuration/miscellaneous.md#events_pipeline). Remove any that are no longer needed.

### Background Task Workers

NetBox defers the execution of certain tasks to background workers via Redis queues serviced by one or more background workers. These workers operate asynchronously from the frontend WSGI workers, and process tasks in the order they are enqueued.

NetBox creates three default queues for background tasks: `high`, `default`, and `low`. Additional queues can be configured via the [`QUEUE_MAPPINGS`](../configuration/miscellaneous.md#queue_mappings) configuration parameter.

By default, a background worker (spawned via `manage.py rqworker`) will listen to all available queues. To improve responsiveness to high-priority background tasks, consider dedicating one or more workers to service the `high` queue only:

```
$ ./manage.py rqworker high
19:31:20 Worker 861be45b32214afc95c235beeb19c9fa: started with PID 2300029, version 2.6.0
19:31:20 Worker 861be45b32214afc95c235beeb19c9fa: subscribing to channel rq:pubsub:861be45b32214afc95c235beeb19c9fa
19:31:20 *** Listening on high...
19:31:20 Worker 861be45b32214afc95c235beeb19c9fa: cleaning registries for queue: high
19:31:20 Scheduler for high started with PID 2300096
```

## API Clients

### REST API

NetBox's [REST API](../integrations/rest-api.md) is the primary means of integration with external systems, allowing full create, read, update, and delete (CRUD) operations. There are a few performance considerations to keep in mind when dealing with very large data sets.

#### Use "Brief" Mode for Simple Lists

In cases where you need to retrieve only a minimal representation of objects, append `?brief=True` to the URL. This instructs NetBox to omit all fields except the following:

* ID
* URL
* Display text
* Name (or similar identifier)
* Slug (if present)
* Description
* Counts of notable related objects (where applicable)

For example, a site fetched using brief mode returns only the following:

```json
{
    "id": 2,
    "url": "https://netbox/api/dcim/sites/2/",
    "display": "DM-Akron",
    "name": "DM-Akron",
    "slug": "dm-akron",
    "description": ""
}
```

Omitting all other fields (especially those which fetch and return related objects) often results in much faster queries.

#### Declare Selected Fields

If you need more flexibility regarding the fields to be returned for an object type, you can specify a list of fields to include using the `fields` query parameter. For example, a request for `/api/dcim/sites/?fields=id,name,status,region` will return the following:

```json
{
    "id": 2,
    "name": "DM-Akron",
    "status": {
        "value": "active",
        "label": "Active"
    },
    "region": {
        "id": 51,
        "url": "https://netbox/api/dcim/regions/51/",
        "display": "Ohio",
        "name": "Ohio",
        "slug": "us-oh",
        "description": "",
        "site_count": 0,
        "_depth": 2
    }
}
```

Like brief mode, this approach can significantly reduce the response time of an API request by omitting unneeded data.

#### Employ Pagination

Like the user interface, the REST API employs pagination to limit the number of objects returned in a single response. If a page size is not specified by the request (i.e. by passing `?limit=10`), NetBox will use the default size defined by [`PAGINATE_COUNT`](../configuration/default-values.md#paginate_count). The default page size is 50.

For some requests, especially those using brief mode or a minimal selection of fields, it may be desirable to specify a higher page size, so that fewer requests are needed to retrieve all objects. Appending `?limit=0` to the request effectively seeks to disable pagination. (Note, however, that the requested page size cannot exceed the value of [`MAX_PAGE_SIZE`](../configuration/miscellaneous.md#max_page_size), which defaults to 1,000.)

Complex API requests, which pull in many related objects, generate a relatively high load on the application, and generally benefit from reduced page size. If you find that your API requests are taking an inordinate amount of time, try reducing the page size from the default value so that fewer objects need to be returned for each request.

### GraphQL API

NetBox's read-only [GraphQL API](../integrations/graphql-api.md) offers an alternative to its REST API, and provides a very flexible means of retrieving data. GraphQL enables the client to request any object from a single endpoint, specifying only the desired attributes and relations. Many users prefer this to the more rigid structure of the REST API, but it's important to understand the trade-offs of crafting complex queries.

#### Request Only the Necessary Fields

For optimal performance, craft your GraphQL queries to return only the fields needed by the client. This will reduce the overall query time, especially when omitting related objects.

#### Avoid Overly Complex Queries

The primary benefit of the GraphQL API is that it allows the client to offload to the server the work of stitching together various related objects, which would require the client to make multiple requests to different endpoints if using the REST API. However, this advantage does not come for free: The more information that is requested in a single query, the more work the server needs to do to fetch the raw data from the database and render it into a GraphQL response. Very complex queries can yield dozens or hundreds of SQL queries on the backend, which increase the time it takes to render a response.

While it can be tempting to pack as much data as possible into a single GraphQL query, realize that there is a balance to be struck between minimizing the number of queries needed and avoiding complexity in the interest of performance. For example, while it is possible to retrieve via a single GraphQL API request all the IP addresses and all attached cables for every device in a site, it is probably more efficient (often _much_ more efficient) to make two or three separate requests and correlate the data locally.

#### Use Filters

You can specify filters when making a GraphQL query to limit the set of objects returned. This works a bit differently from the REST API, as filters are declared inside the query statement rather than appended to the URL, but the concept is the same. For example, to return only active sites:

```graphql
query {
  site_list(
    filters: {
      status: STATUS_ACTIVE
    }
  ) {
    name
  }
}
```

This returns only sites with a status of "active" and avoid needing to parse through all the others. For further information about filters, see the [GraphQL API documentation](../integrations/graphql-api.md).

#### Employ Pagination

Like the REST API, the GraphQL API supports pagination. Queries which return a large number of objects should employ pagination to limit the size of each response.

```graphql
{
  device_list(
    pagination: {limit: 100}
  ) {
    id
    name
    serial
    status
  }
}
```
