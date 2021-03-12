# NetBox v2.11

## v2.11-beta1 (FUTURE)

**WARNING:** This is a beta release and is not suitable for production use. It is intended for development and evaluation purposes only. No upgrade path to the final v2.11 release will be provided from this beta, and users should assume that all data entered into the application will be lost.

**Note:** NetBox v2.11 is the last major release that will support Python 3.6. Beginning with NetBox v2.12, Python 3.7 or
later will be required.

### New Features

#### Parent Interface Assignments ([#1519](https://github.com/netbox-community/netbox/issues/1519))

Virtual interfaces can now be assigned to a "parent" physical interface, by setting the `parent` field on the Interface model. This is helpful for associating subinterfaces with their physical counterpart. For example, you might assign virtual interfaces Gi0/0.100 and Gi0/0.200 to the physical interface Gi0/0.

#### Pre- and Post-Change Snapshots in Webhooks ([#3451](https://github.com/netbox-community/netbox/issues/3451))

In conjunction with the newly improved change logging functionality ([#5913](https://github.com/netbox-community/netbox/issues/5913)), outgoing webhooks now include a pre- and post-change representation of the modified object. These are available in the rendering context as a dictionary named `snapshots` with keys `prechange` and `postchange`. For example, here are the abridged snapshots resulting from renaming a site and changing its status:

```json
"snapshots": {
    "prechange": {
        "name": "Site 1",
        "slug": "site-1",
        "status": "active",
        ...
    },
    "postchange": {
        "name": "Site 2",
        "slug": "site-2",
        "status": "planned",
        ...
    }
}
```

Note: The pre-change snapshot for an object creation will always be null, as will the post-change snapshot for an object deletion.

#### Mark as Connected Without a Cable ([#3648](https://github.com/netbox-community/netbox/issues/3648))

Cable termination objects (circuit terminations, power feeds, and most device components) can now be marked as "connected" without actually attaching a cable. This helps simplify the process of modeling an infrastructure boundary where you don't necessarily know or care what is connected to the far end of a cable, but still need to designate the near end termination.

In addition to the new `mark_connected` boolean field, the REST API representation of these objects now also includes a read-only boolean field named `_occupied`. This conveniently returns true if either a cable is attached or `mark_connected` is true.

#### Allow Assigning Devices to Locations ([#4971](https://github.com/netbox-community/netbox/issues/4971))

Devices can now be assigned to locations (formerly known as rack groups) within a site without needing to be assigned to a particular rack. This is handy for assigning devices to rooms or floors within a building where racks are not used. The `location` foreign key field has been added to the Device model to support this.

#### Dynamic Object Exports ([#4999](https://github.com/netbox-community/netbox/issues/4999))

When exporting a list of objects in NetBox, users now have the option of selecting the "current view". This will render CSV output matching the configuration of the current table. For example, if you modify the sites list to display on the site name, tenant, and status, the rendered CSV will include only these columns.

The legacy static export behavior has been retained to ensure backward compatibility for dependent integrations. However, users are strongly encouraged to adapt custom export templates where needed as this functionality will be removed in v2.12.

#### New Site Group Model ([#5892](https://github.com/netbox-community/netbox/issues/5892))

This release introduces the new Site Group model, which can be used to organize sites similar to the existing Region model. Whereas regions are intended for geographically arranging sites into countries, states, and so on, the new site group model can be used to organize sites by role or other arbitrary classification. Using regions and site groups in conjunction provides two dimensions along which sites can be organized, offering greater flexibility to the user.

#### Improved Change Logging ([#5913](https://github.com/netbox-community/netbox/issues/5913))

The ObjectChange model (which is used to record the creation, modification, and deletion of NetBox objects) now explicitly records the pre-change and post-change state of each object, rather than only the post-change state. This was done to present a more clear depiction of each change being made, and to prevent the erroneous association of a previous unlogged change with its successor.

### Enhancements

* [#5370](https://github.com/netbox-community/netbox/issues/5370) - Extend custom field support to organizational models
* [#5375](https://github.com/netbox-community/netbox/issues/5375) - Add `speed` attribute to console port models
* [#5401](https://github.com/netbox-community/netbox/issues/5401) - Extend custom field support to device component models
* [#5451](https://github.com/netbox-community/netbox/issues/5451) - Add support for multiple-selection custom fields
* [#5608](https://github.com/netbox-community/netbox/issues/5608) - Add REST API endpoint for custom links
* [#5610](https://github.com/netbox-community/netbox/issues/5610) - Add REST API endpoint for webhooks
* [#5894](https://github.com/netbox-community/netbox/issues/5894) - Use primary keys when filtering object lists by related objects in the UI
* [#5895](https://github.com/netbox-community/netbox/issues/5895) - Rename RackGroup to Location
* [#5901](https://github.com/netbox-community/netbox/issues/5901) - Add `created` and `last_updated` fields to device component models
* [#5972](https://github.com/netbox-community/netbox/issues/5972) - Enable bulk editing for organizational models

### Other Changes

* [#1638](https://github.com/netbox-community/netbox/issues/1638) - Migrate all primary keys to 64-bit integers
* [#5873](https://github.com/netbox-community/netbox/issues/5873) - Use numeric IDs in all object URLs

### REST API Changes

* All primary keys are now 64-bit integers
* All device components
  * Added support for custom fields
  * Added `created` and `last_updated` fields to track object creation and modification
* All device component templates
  * Added `created` and `last_updated` fields to track object creation and modification
* All organizational models
  * Added support for custom fields
* All cable termination models (cabled device components, power feeds, and circuit terminations)
  * Added `mark_connected` boolean field to force connection status
  * Added `_occupied` read-only boolean field as common attribute for determining whether an object is occupied
* Renamed RackGroup to Location
  * The `/dcim/rack-groups/` endpoint is now `/dcim/locations/`
* dcim.Device
  * Added the `location` field
* dcim.Interface
  * Added the `parent` field
* dcim.PowerPanel
  * Renamed `rack_group` field to `location`
* dcim.Rack
  * Renamed `group` field to `location`
* dcim.Site
  * Added the `group` foreign key field to SiteGroup
* dcim.SiteGroup
  * Added the `/api/dcim/site-groups/` endpoint
* extras.ConfigContext
  * Added the `site_groups` many-to-many field to track the assignment of ConfigContexts to SiteGroups
* extras.CustomField
  * Added new custom field type: `multi-select`
* extras.CustomLink
  * Added the `/api/extras/custom-links/` endpoint
* extras.ObjectChange
  * Added the `prechange_data` field
  * Renamed `object_data` to `postchange_data`
* extras.Webhook
  * Added the `/api/extras/webhooks/` endpoint
