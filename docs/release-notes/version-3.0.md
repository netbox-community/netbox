# NetBox v3.0

## v3.0.0 (FUTURE)

!!! warning "Existing Deployments Must Upgrade from v2.11"
    Upgrading an existing NetBox deployment to version 3.0 **must** be done from version 2.11.0 or later. If attempting to upgrade a deployment of NetBox v2.10 or earlier, first upgrade to a NetBox v2.11 release, and then upgrade from v2.11 to v3.0. This will avoid any problems with the database migration optimizations implemented in version 3.0.

### Breaking Changes

* Python 3.6 is no longer supported. NetBox v3.0 supports Python 3.7, 3.8, and 3.9.
* The secrets functionality present in prior releases of NetBox has been removed. The NetBox maintainers strongly recommend the adoption of [Hashicorp Vault](https://github.com/hashicorp/vault) in place of this feature. Development of a NetBox plugin to replace the legacy secrets functionality is also underway.
* The default CSV export format for all objects now includes all available data from the object list. Additionally, the CSV headers now use human-friendly titles rather than raw field names. If backward compatibility with the old format is desired, export templates can be written to reproduce it.
* The `invalidate` management command (which clears cached database queries) is no longer needed and has been removed (see [#6639](https://github.com/netbox-community/netbox/issues/6639)).
* Support for queryset caching configuration (`caching_config`) has been removed from the plugins API (see [#6639](https://github.com/netbox-community/netbox/issues/6639)).
* The `cacheops_*` metrics have been removed from the Prometheus exporter (see [#6639](https://github.com/netbox-community/netbox/issues/6639)).
* The `display_field` keyword argument has been removed from custom script ObjectVar and MultiObjectVar fields. These widgets will use the `display` value provided by the REST API.
* The deprecated `display_name` field has been removed from all REST API serializers. (API clients should reference the `display` field instead.)
* The redundant REST API endpoints for console, power, and interface connections have been removed. The same data can be retrieved by querying the respective model endpoints with the `?connected=True` filter applied.

### New Features

#### Updated User Interface ([#5893](https://github.com/netbox-community/netbox/issues/5893))

The NetBox user interface has been completely overhauled with a fresh new look! Beyond the cosmetic improvements, this initiative has allowed us to modernize the entire front end, upgrading from Bootstrap 3 to Bootstrap 5, and eliminating dependencies on outdated libraries such as jQuery and jQuery-UI. The new user interface also features a dark mode option.

![NetBox v3.0 user interface](../media/release-notes/netbox30_ui.png)

A huge thank you to NetBox maintainer [Matt Love](https://github.com/thatmattlove) for his tremendous work on this!

#### GraphQL API ([#2007](https://github.com/netbox-community/netbox/issues/2007))

A new [GraphQL API](https://graphql.org/) has been added to complement NetBox's REST API. GraphQL allows the client to specify which fields of the available data to return in each request. NetBox's implementation, which employs [Graphene](https://graphene-python.org/), also includes a user-friendly query interface known as GraphiQL.

Here's an example GraphQL request:

```
{
  circuit_list {
    cid
    provider {
      name
    }
    termination_a {
      id
    }
    termination_z {
      id
    }
  }
}
```

And the response:

```
{
  "data": {
    "circuit_list": [
      {
        "cid": "1002840283",
        "provider": {
          "name": "CenturyLink"
        },
        "termination_a": null,
        "termination_z": {
          "id": "23"
        }
      },
...
```

All GraphQL requests are made at the `/graphql` URL (which also serves the GraphiQL UI). The API is currently read-only, however users who wish to disable it until needed can do so by setting the `GRAPHQL_ENABLED` configuration parameter to False. For more detail on NetBox's GraphQL implementation, see [the GraphQL API documentation](../graphql-api/overview.md).

#### IP Ranges ([#834](https://github.com/netbox-community/netbox/issues/834))

NetBox now supports modeling arbitrary IP ranges, which are defined by specifying a starting and ending IP address (e.g. to denote DHCP pools). Similar to prefixes, each IP range may optionally be assigned to a VRF and/or tenant, and can be assigned a functional role. An IP range must be assigned a status of active, reserved, or deprecated. The REST API implementation for this model also includes an "available IPs" endpoint which functions similarly to the endpoint for prefixes.

More information about IP ranges is available [in the documentation](../models/ipam/iprange.md).

#### Custom Model Validation ([#5963](https://github.com/netbox-community/netbox/issues/5963))

This release introduces the [`CUSTOM_VALIDATORS`](../configuration/optional-settings.md#custom_validators) configuration parameter, which allows administrators to map NetBox models to custom validator classes to enforce custom validation logic. For example, the following configuration requires every site to have a name of at least ten characters and a description:

```python
from extras.validators import CustomValidator

CUSTOM_VALIDATORS = {
    'dcim.site': (
        CustomValidator({
            'name': {
                'min_length': 10,
            },
            'description': {
                'required': True,
            }
        }),
    )
}
```

CustomValidator can also be subclassed to enforce more complex logic by overriding its `validate()` method. See the [custom validation](../customization/custom-validation.md) documentation for more details.

#### SVG Cable Traces ([#6000](https://github.com/netbox-community/netbox/issues/6000))

Cable trace diagrams are now rendered as atomic SVG images, similar to rack elevations. These images are embedded in the UI and can be easily downloaded for use outside NetBox. SVG images can also be generated directly through the REST API, by specifying SVG as the render format for the `trace` endpoint on a cable termination:

```no-highlight
GET /api/dcim/interfaces/<ID>>/trace/?render=svg
```

The width of the rendered image in pixels may optionally be specified by appending the `&width=<width>` parameter to the request. The default width is 400px.

#### New Views for Models Previously Under the Admin UI ([#6466](https://github.com/netbox-community/netbox/issues/6466))

New UI views have been introduced to manage the following models:

* Custom fields
* Custom links
* Export templates
* Webhooks

These models were previously managed under the admin section of the UI. Moving them to dedicated views ensures a more consistent and convenient user experience.

#### REST API Token Provisioning ([#5264](https://github.com/netbox-community/netbox/issues/5264))

The new REST API endpoint `/api/users/tokens/` has been added, which includes a child endpoint for provisioning new REST API tokens using a username and password. This allows a user to gain REST API access without needing to first create a token via the web UI.

```
$ curl -X POST \
-H "Content-Type: application/json" \
-H "Accept: application/json; indent=4" \
https://netbox/api/users/tokens/provision/ \
--data '{
    "username": "hankhill",
    "password: "I<3C3H8",
}'
```

If the supplied credentials are valid, NetBox will create and return a new token for the user.

#### New Housekeeping Command ([#6590](https://github.com/netbox-community/netbox/issues/6590))

A new management command has been added: `manage.py housekeeping`. This command is intended to be run nightly via a system cron job. It performs the following tasks:

* Clear expired authentication sessions from the database
* Delete change log records which have surpassed the configured retention period (if configured)
* Check for new NetBox releases (if enabled)

A convenience script for calling this command via an automated scheduler has been included at `/contrib/netbox-housekeeping.sh`. Please see the [housekeeping documentation](../administration/housekeeping.md) for further details.

#### Custom Queue Support for Plugins ([#6651](https://github.com/netbox-community/netbox/issues/6651))

NetBox uses Redis and Django-RQ for background task queuing. Whereas previous releases employed only a single default queue, NetBox now provides a high-, medium- (default), and low-priority queue for use by plugins. (These will also likely be used internally as new functionality is added in future releases.)

Plugins can also now create their own custom queues by defining a `queues` list within their PluginConfig class:

```python
class MyPluginConfig(PluginConfig):
    name = 'myplugin'
    ...
    queues = [
        'queue1',
        'queue2',
        'queue-whatever-the-name'
    ]
```

Note that NetBox's `rqworker` process will _not_ service custom queues by default, since it has no way to infer the priority of each queue. Plugin authors should be diligent in including instructions for proper worker configuration in their plugin's documentation.

### Enhancements

* [#2434](https://github.com/netbox-community/netbox/issues/2434) - Add option to assign IP address upon creating a new interface
* [#3665](https://github.com/netbox-community/netbox/issues/3665) - Enable rendering export templates via REST API
* [#3682](https://github.com/netbox-community/netbox/issues/3682) - Add `color` field to front and rear ports
* [#4609](https://github.com/netbox-community/netbox/issues/4609) - Allow marking prefixes as fully utilized
* [#5203](https://github.com/netbox-community/netbox/issues/5203) - Remember user preference when toggling display of device images in rack elevations
* [#5806](https://github.com/netbox-community/netbox/issues/5806) - Add kilometer and mile as choices for cable length unit
* [#6154](https://github.com/netbox-community/netbox/issues/6154) - Allow decimal values for cable lengths
* [#6328](https://github.com/netbox-community/netbox/issues/6328) - Build and serve documentation locally

### Bug Fixes (from v3.2-beta2)

* [#6977](https://github.com/netbox-community/netbox/issues/6977) - Truncate global search dropdown on small screens
* [#6979](https://github.com/netbox-community/netbox/issues/6979) - Hide "create & add another" button for circuit terminations
* [#6982](https://github.com/netbox-community/netbox/issues/6982) - Fix styling of empty dropdown list under dark mode
* [#6996](https://github.com/netbox-community/netbox/issues/6996) - Global search bar should be full width on mobile
* [#7001](https://github.com/netbox-community/netbox/issues/7001) - Fix page focus on load
* [#7034](https://github.com/netbox-community/netbox/issues/7034) - Fix toggling of VLAN group scope selector fields
* [#7045](https://github.com/netbox-community/netbox/issues/7045) - Fix navigation menu rendering under Chrome

### Other Changes

* [#5223](https://github.com/netbox-community/netbox/issues/5223) - Remove the console/power/interface connections REST API endpoints
* [#5278](https://github.com/netbox-community/netbox/issues/5278) - Remove the secrets functionality from NetBox core
* [#5532](https://github.com/netbox-community/netbox/issues/5532) - Drop support for Python 3.6
* [#5994](https://github.com/netbox-community/netbox/issues/5994) - Drop support for `display_field` argument on ObjectVar
* [#6068](https://github.com/netbox-community/netbox/issues/6068) - Drop support for legacy static CSV export
* [#6338](https://github.com/netbox-community/netbox/issues/6338) - Decimal fields are no longer coerced to strings in REST API
* [#6471](https://github.com/netbox-community/netbox/issues/6471) - Optimize database migrations
* [#6639](https://github.com/netbox-community/netbox/issues/6639) - Drop support for queryset caching (django-cacheops)
* [#6713](https://github.com/netbox-community/netbox/issues/6713) - Checking for new releases is now done as part of the housekeeping routine
* [#6767](https://github.com/netbox-community/netbox/issues/6767) - Add support for Python 3.9

### Configuration Changes

* The `CACHE_TIMEOUT` configuration parameter has been removed.
* The `RELEASE_CHECK_TIMEOUT` configuration parameter has been removed.

### REST API Changes

* Removed all endpoints related to the secrets functionality:
    * `/api/secrets/generate-rsa-key-pair/`
    * `/api/secrets/get-session-key/`
    * `/api/secrets/secrets/`
    * `/api/secrets/secret-roles/`
* Removed the following "connections" endpoints:
    * `/api/dcim/console-connections/`
    * `/api/dcim/power-connections/`
    * `/api/dcim/interface-connections/`
* Added the `/api/ipam/ip-ranges/` endpoint
* Added the `/api/users/tokens/` endpoint
    * The `provision/` child endpoint can be used to provision new REST API tokens by supplying a valid username and password
* dcim.Cable
    * `length` is now a decimal value
* dcim.Device
    * Removed the `display_name` attribute (use `display` instead)
* dcim.DeviceType
    * Removed the `display_name` attribute (use `display` instead)
* dcim.FrontPort
    * Added `color` field
* dcim.FrontPortTemplate
    * Added `color` field
* dcim.Rack
    * Removed the `display_name` attribute (use `display` instead)
* dcim.RearPort
    * Added `color` field
* dcim.RearPortTemplate
    * Added `color` field
* dcim.Site
    * `latitude` and `longitude` are now decimal fields rather than strings
* extras.ContentType
    * Removed the `display_name` attribute (use `display` instead)
* ipam.Prefix
    * Added the `mark_utilized` boolean field
* ipam.VLAN
    * Removed the `display_name` attribute (use `display` instead)
* ipam.VRF
    * Removed the `display_name` attribute (use `display` instead)
* virtualization.VirtualMachine
    * `vcpus` is now a decimal field rather than a string
