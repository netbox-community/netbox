# NetBox v4.0

## v4.0.9 (2024-08-14)

### Enhancements

* [#16692](https://github.com/netbox-community/netbox/issues/16692) - Enable modifying VLAN assignment while bulk editing prefixes
* [#17006](https://github.com/netbox-community/netbox/issues/17006) - Add IEEE 802.11be interface type

### Bug Fixes

* [#13459](https://github.com/netbox-community/netbox/issues/13459) - Correct OpenAPI schema type for `TreeNodeMultipleChoiceFilter`
* [#16073](https://github.com/netbox-community/netbox/issues/16073) - Respect default values for custom fields during bulk import of objects
* [#16176](https://github.com/netbox-community/netbox/issues/16176) - Restore ability to select multiple terminating devices when connecting a cable
* [#16871](https://github.com/netbox-community/netbox/issues/16871) - Sanitize device ID query parameter when bulk editing components to prevent exception
* [#17038](https://github.com/netbox-community/netbox/issues/17038) - Fix AttributeError exception when attempting to export system status data
* [#17064](https://github.com/netbox-community/netbox/issues/17064) - Fix misaligned text within rendered Markdown code blocks
* [#17124](https://github.com/netbox-community/netbox/issues/17124) - `BaseTable` should follow reverse one-to-one relationships when prefetching related objects
* [#17131](https://github.com/netbox-community/netbox/issues/17131) - Fix exception when creating object-type custom field without selecting related object type
* [#17144](https://github.com/netbox-community/netbox/issues/17144) - Avoid showing duplicated pop-up messages

---

## v4.0.8 (2024-07-26)

### Enhancements

* [#14640](https://github.com/netbox-community/netbox/issues/14640) - Add Dutch language support
* [#14792](https://github.com/netbox-community/netbox/issues/14792) - Add Polish language support
* [#15375](https://github.com/netbox-community/netbox/issues/15375) - Enable customization of SSO backend name & icon
* [#15660](https://github.com/netbox-community/netbox/issues/15660) - Add Czech language support
* [#15696](https://github.com/netbox-community/netbox/issues/15696) - Add Danish language support
* [#16793](https://github.com/netbox-community/netbox/issues/16793) - Add Italian language support
* [#16933](https://github.com/netbox-community/netbox/issues/16933) - Enable toggling true/false marks on BooleanColumn
* [#16943](https://github.com/netbox-community/netbox/issues/16943) - Expand navigation breadcrumbs on job view to include the parent object

### Bug Fixes

* [#16357](https://github.com/netbox-community/netbox/issues/16357) - Replicate assigned type & tenant for cable when clicking "create an add another"
* [#16402](https://github.com/netbox-community/netbox/issues/16402) - Remove inoperative links from report result view
* [#16536](https://github.com/netbox-community/netbox/issues/16536) - Revert `role` & `role_id` filters for device components to `device_role` & `device_role_id` to avoid conflict with inventory item `role` field
* [#16624](https://github.com/netbox-community/netbox/issues/16624) - Correct OpenAPI schema definitions for several fields
* [#16760](https://github.com/netbox-community/netbox/issues/16760) - Fix data source syncing using git via a local path
* [#16819](https://github.com/netbox-community/netbox/issues/16819) - Highlight parent device in rack when viewing child device
* [#16838](https://github.com/netbox-community/netbox/issues/16838) - ActionsColumn should render extra buttons even when no stock actions are enabled
* [#16867](https://github.com/netbox-community/netbox/issues/16867) - Fix exception when a dashboard list widget references a model which has been removed
* [#16963](https://github.com/netbox-community/netbox/issues/16963) - Fix filtering of "accounts" link under providers list
* [#16964](https://github.com/netbox-community/netbox/issues/16964) - Ensure configured password validators are enforced

---

## v4.0.7 (2024-07-09)

### Enhancements

* [#14554](https://github.com/netbox-community/netbox/issues/14554) - Add support for [django-storage-swift](https://github.com/dennisv/django-storage-swift) storage backend
* [#16424](https://github.com/netbox-community/netbox/issues/16424) - Enable filtering of devices by cluster and cluster group
* [#16716](https://github.com/netbox-community/netbox/issues/16716) - Display NAT address (if any) for OOB IP address under device view
* [#16725](https://github.com/netbox-community/netbox/issues/16725) - Always position the admin section last in the navigation menu
* [#16791](https://github.com/netbox-community/netbox/issues/16791) - Add 200 & 400 Gbps selections for circuit termination port speed
* [#16802](https://github.com/netbox-community/netbox/issues/16802) - Introduce `SENTRY_SEND_DEFAULT_PII` configuration parameter and disable PII export by default
* [#16817](https://github.com/netbox-community/netbox/issues/16817) - Add 200 & 400 Gbps selections for circuit commit rate

### Bug Fixes

* [#16523](https://github.com/netbox-community/netbox/issues/16523) - Restore highlighting of current device in virtual chassis members panel
* [#16654](https://github.com/netbox-community/netbox/issues/16654) - Fix parent item assignment for inventory item bulk import
* [#16657](https://github.com/netbox-community/netbox/issues/16657) - Fix translation of object types in global search
* [#16679](https://github.com/netbox-community/netbox/issues/16679) - Avoid overwriting custom JSON fields during bulk edit
* [#16689](https://github.com/netbox-community/netbox/issues/16689) - System configuration view should reflect static parameters when no config revisions exist
* [#16714](https://github.com/netbox-community/netbox/issues/16714) - Fix cloning of device types with 0U height
* [#16721](https://github.com/netbox-community/netbox/issues/16721) - Fix errant API request after deselecting a rack in device edit form
* [#16723](https://github.com/netbox-community/netbox/issues/16723) - Fix escaping of path to virtual environment in `upgrade.sh`
* [#16735](https://github.com/netbox-community/netbox/issues/16735) - Object list "results" tab should show a count of zero when empty
* [#16747](https://github.com/netbox-community/netbox/issues/16747) - Avoid clearing entire search cache when manually reindexing specific apps/models
* [#16758](https://github.com/netbox-community/netbox/issues/16758) - Ensure manually selected lagnuage persists across browser sessions
* [#16779](https://github.com/netbox-community/netbox/issues/16779) - Fix saved filter selection for child object lists
* [#16780](https://github.com/netbox-community/netbox/issues/16780) - IKE proposal created via REST API should not require authentication_algorithm
* [#16796](https://github.com/netbox-community/netbox/issues/16796) - Allow assignment of VM with no site to a cluster with a site
* [#16806](https://github.com/netbox-community/netbox/issues/16806) - Fix redirect URL when creating contact assignments with "add another" button
* [#16807](https://github.com/netbox-community/netbox/issues/16807) - Fix layout of VLAN edit form when custom fields are present
* [#16808](https://github.com/netbox-community/netbox/issues/16808) - Fix event rule triggering in scenario where objects are updated immediately prior to deletion
* [#16813](https://github.com/netbox-community/netbox/issues/16813) - Fix AttributeError exception when filtering bookmarks in dashboard widget by object type
* [#16843](https://github.com/netbox-community/netbox/issues/16843) - Permit creation of IKE policies via REST API without specifying an IKE mode

---

## v4.0.6 (2024-06-24)

### Enhancements

* [#15348](https://github.com/netbox-community/netbox/issues/15348) - Show saved filters alongside quick search on object list views
* [#15794](https://github.com/netbox-community/netbox/issues/15794) - Dynamically populate related objects in UI views
* [#16256](https://github.com/netbox-community/netbox/issues/16256) - Enable alphabetical ordering of bookmarks on dashboard
* [#16307](https://github.com/netbox-community/netbox/issues/16307) - Enable calling `log_*()` methods on Script without passing a message

### Bug Fixes

* [#13925](https://github.com/netbox-community/netbox/issues/13925) - Fix support for "zulu" (UTC) timestamps for custom fields
* [#14829](https://github.com/netbox-community/netbox/issues/14829) - Fix support for simple conditions (without AND/OR) in event rules
* [#15717](https://github.com/netbox-community/netbox/issues/15717) - Allow assigning a device/VM in a site to a cluster with no site assigned
* [#16143](https://github.com/netbox-community/netbox/issues/16143) - Display timestamps in tables in the configured timezone
* [#16149](https://github.com/netbox-community/netbox/issues/16149) - Fix object linking in custom script logs
* [#16252](https://github.com/netbox-community/netbox/issues/16252) - Fix total count in tab at top of rack elevations view
* [#16273](https://github.com/netbox-community/netbox/issues/16273) - Restore global search bar on mobile
* [#16416](https://github.com/netbox-community/netbox/issues/16416) - Retain dark/light mode toggle on mobile view
* [#16444](https://github.com/netbox-community/netbox/issues/16444) - Disable ordering circuits list by A/Z termination
* [#16450](https://github.com/netbox-community/netbox/issues/16450) - Searching for rack unit in form dropdown should be case-insensitive
* [#16452](https://github.com/netbox-community/netbox/issues/16452) - Fix sizing of buttons within object attribute panels
* [#16454](https://github.com/netbox-community/netbox/issues/16454) - Address DNS lookup bug in `django-debug-toolbar
* [#16460](https://github.com/netbox-community/netbox/issues/16460) - Omit spaces from telephone number URLs
* [#16512](https://github.com/netbox-community/netbox/issues/16512) - Restore a user's preferred language (if any) on login
* [#16542](https://github.com/netbox-community/netbox/issues/16542) - Fix bulk form operations when HTMX is enabled
* [#16702](https://github.com/netbox-community/netbox/issues/16702) - Fix validation of `return_url` query parameter

---

## v4.0.5 (2024-06-06)

### Enhancements

* [#14810](https://github.com/netbox-community/netbox/issues/14810) - Enable contact assignment for services
* [#15489](https://github.com/netbox-community/netbox/issues/15489) - Add 1000Base-TX interface type
* [#15873](https://github.com/netbox-community/netbox/issues/15873) - Improve readability of allocates resource numbers for clusters
* [#16290](https://github.com/netbox-community/netbox/issues/16290) - Capture entire object in changelog data (but continue to display only non-internal attributes)
* [#16353](https://github.com/netbox-community/netbox/issues/16353) - Enable plugins to extend object change view with custom content

### Bug Fixes

* [#13422](https://github.com/netbox-community/netbox/issues/13422) - Rebuild MPTT trees for applicable models after merging staged changes
* [#14567](https://github.com/netbox-community/netbox/issues/14567) - Apply active quicksearch value when exporting "current view" from object list
* [#15194](https://github.com/netbox-community/netbox/issues/15194) - Avoid enqueuing duplicate event triggers for a modified object
* [#16039](https://github.com/netbox-community/netbox/issues/16039) - Fix row highlighting for front & rear port connections under device view
* [#16050](https://github.com/netbox-community/netbox/issues/16050) - Fix display of names & descriptions defined for custom scripts
* [#16083](https://github.com/netbox-community/netbox/issues/16083) - Disable font ligatures to avoid peculiarities in rendered text
* [#16202](https://github.com/netbox-community/netbox/issues/16202) - Fix site map button URL for certain localizations
* [#16261](https://github.com/netbox-community/netbox/issues/16261) - Fix GraphQL filtering for certain multi-value filters
* [#16286](https://github.com/netbox-community/netbox/issues/16286) - Fix global search support for provider accounts
* [#16312](https://github.com/netbox-community/netbox/issues/16312) - Fix object list navigation for dashboard widgets
* [#16315](https://github.com/netbox-community/netbox/issues/16315) - Fix filtering change log & journal entries by object type in UI
* [#16376](https://github.com/netbox-community/netbox/issues/16376) - Update change log for the terminating object (e.g. interface) when attaching a cable
* [#16400](https://github.com/netbox-community/netbox/issues/16400) - Fix AttributeError when attempting to restore a previous configuration revision after deleting the current one

---

## v4.0.3 (2024-05-22)

### Enhancements

* [#12984](https://github.com/netbox-community/netbox/issues/12984) - Add Molex Micro-Fit power port & outlet types
* [#13764](https://github.com/netbox-community/netbox/issues/13764) - Enable contact assignments for aggregates, prefixes, IP ranges, and IP addresses
* [#14639](https://github.com/netbox-community/netbox/issues/14639) - Add Ukrainian translation support
* [#14653](https://github.com/netbox-community/netbox/issues/14653) - Add an inventory items table column for all device components
* [#14686](https://github.com/netbox-community/netbox/issues/14686) - Add German translation support
* [#14855](https://github.com/netbox-community/netbox/issues/14855) - Add Chinese translation support
* [#14948](https://github.com/netbox-community/netbox/issues/14948) - Introduce the `has_virtual_device_context` filter for devices
* [#15353](https://github.com/netbox-community/netbox/issues/15353) - Improve error reporting when custom scripts fail to load
* [#15496](https://github.com/netbox-community/netbox/issues/15496) - Implement dedicated views for management of circuit terminations
* [#15603](https://github.com/netbox-community/netbox/issues/15603) - Add 4G & 5G cellular interface types
* [#15962](https://github.com/netbox-community/netbox/issues/15962) - Enable UNIX socket connections for Redis

### Bug Fixes

* [#13293](https://github.com/netbox-community/netbox/issues/13293) - Limit interface selector for IP address to current device/VM
* [#14953](https://github.com/netbox-community/netbox/issues/14953) - Ensure annotated count fields are present in REST API response data when creating new objects
* [#14982](https://github.com/netbox-community/netbox/issues/14982) - Fix OpenAPI schema definition for SerializedPKRelatedFields
* [#15082](https://github.com/netbox-community/netbox/issues/15082) - Strip whitespace from choice values & labels when creating a custom field choice set
* [#16138](https://github.com/netbox-community/netbox/issues/16138) - Fix support for referencing users & groups in object permissions
* [#16145](https://github.com/netbox-community/netbox/issues/16145) - Restore ability to reference custom scripts via module & name in REST API
* [#16164](https://github.com/netbox-community/netbox/issues/16164) - Correct display of selected values in UI when filtering object list by a null value
* [#16173](https://github.com/netbox-community/netbox/issues/16173) - Fix TypeError exception when viewing object list with no pagination preference defined
* [#16228](https://github.com/netbox-community/netbox/issues/16228) - Fix permissions enforcement for GraphQL queries of users & groups
* [#16232](https://github.com/netbox-community/netbox/issues/16232) - Preserve bulk action checkboxes on dynamic tables when using pagination
* [#16240](https://github.com/netbox-community/netbox/issues/16240) - Fixed NoReverseMatch exception when adding circuit terminations to an object counts dashboard widget

---

## v4.0.2 (2024-05-14)

!!! warning "Important"
    This release includes an important security fix, and is a strongly recommended update for all users. More details will follow.

### Enhancements

* [#15119](https://github.com/netbox-community/netbox/issues/15119) - Add cluster & cluster group UI filter fields for VLAN groups
* [#16090](https://github.com/netbox-community/netbox/issues/16090) - Include current NetBox version when an unsupported plugin is detected
* [#16096](https://github.com/netbox-community/netbox/issues/16096) - Introduce the `ENABLE_TRANSLATION` configuration parameter
* [#16107](https://github.com/netbox-community/netbox/issues/16107) - Change the default value for `LOGIN_REQUIRED` to True
* [#16127](https://github.com/netbox-community/netbox/issues/16127) - Add integration point for unsupported settings

### Bug Fixes

* [#16077](https://github.com/netbox-community/netbox/issues/16077) - Fix display of parameter values when viewing configuration revisions
* [#16078](https://github.com/netbox-community/netbox/issues/16078) - Fix integer filters mistakenly marked as required for GraphQL API
* [#16101](https://github.com/netbox-community/netbox/issues/16101) - Fix initial loading of pagination widget for dynamic object tables
* [#16123](https://github.com/netbox-community/netbox/issues/16123) - Fix custom script execution via REST API
* [#16124](https://github.com/netbox-community/netbox/issues/16124) - Fix GraphQL API support for querying virtual machine interfaces

---

## v4.0.1 (2024-05-09)

### Enhancements

* [#15148](https://github.com/netbox-community/netbox/issues/15148) - Add copy-to-clipboard button for config context data
* [#15328](https://github.com/netbox-community/netbox/issues/15328) - Add a virtual machines UI tab for host devices
* [#15451](https://github.com/netbox-community/netbox/issues/15451) - Add 2.5 and 5 Gbps backplane Ethernet interface types
* [#16010](https://github.com/netbox-community/netbox/issues/16010) - Enable Prometheus middleware only if metrics are enabled

### Bug Fixes

* [#15968](https://github.com/netbox-community/netbox/issues/15968) - Avoid resizing quick search field to display clear button
* [#15973](https://github.com/netbox-community/netbox/issues/15973) - Fix AttributeError exception when modifying cable termination type
* [#15977](https://github.com/netbox-community/netbox/issues/15977) - Hide all admin menu items for non-authenticated users
* [#15982](https://github.com/netbox-community/netbox/issues/15982) - Restore the "assign IP" tab for assigning existing IP addresses to interfaces
* [#15992](https://github.com/netbox-community/netbox/issues/15992) - Fix AttributeError exception when Sentry integration is enabled
* [#15995](https://github.com/netbox-community/netbox/issues/15995) - Permit nullable fields referenced by unique constraints to be omitted from REST API requests
* [#15999](https://github.com/netbox-community/netbox/issues/15999) - Fix layout of login form labels for certain languages
* [#16003](https://github.com/netbox-community/netbox/issues/16003) - Enable cache busting for `setmode.js` asset to avoid breaking dark mode support on upgrade
* [#16011](https://github.com/netbox-community/netbox/issues/16011) - Fix site tenant assignment by PK via REST API
* [#16020](https://github.com/netbox-community/netbox/issues/16020) - Include Python version in system UI view
* [#16022](https://github.com/netbox-community/netbox/issues/16022) - Fix database migration failure when encountering a script module which no longer exists on disk
* [#16025](https://github.com/netbox-community/netbox/issues/16025) - Fix execution of scripts via the `runscript` management command
* [#16031](https://github.com/netbox-community/netbox/issues/16031) - Render Markdown content in script log messages
* [#16051](https://github.com/netbox-community/netbox/issues/16051) - Translate "empty" text for object tables
* [#16061](https://github.com/netbox-community/netbox/issues/16061) - Omit hidden fields from display within event rule edit form

---

## v4.0.0 (2024-05-06)

!!! tip "Plugin Maintainers"
    Please see the dedicated [plugin migration guide](../plugins/development/migration-v4.md) for a checklist of changes that may be needed to ensure compatibility with NetBox v4.0.

### Breaking Changes

* Support for Python 3.8 and 3.9 has been removed.
* The format for GraphQL query filters has changed. Please see the GraphQL documentation for details and examples.
* The deprecated `device_role` & `device_role_id` filters for devices have been removed. (Use `role` and `role_id` instead.)
* The obsolete `device_role` field has been removed from the REST API serializer for devices. (Use `role` instead.)
* The legacy reports functionality has been dropped. Reports will be automatically converted to custom scripts on upgrade.
* The `parent` and `parent_id` filters for locations now return only immediate children of the specified location. (Use `ancestor` and `ancestor_id` to return _all_ descendants.)
* The `object_type` field on the CustomField model has been renamed to `related_object_type`.
* The `utilities.utils` module has been removed and its resources reorganized into separate modules organized by function.
* The obsolete `NullableCharField` class has been removed. (Use Django's stock `CharField` class with `null=True` instead.)
* The `annotated_date` template filter and `annotated_now` template tag have been removed.

### New Features

#### Complete UI Refresh ([#12128](https://github.com/netbox-community/netbox/issues/12128))

The NetBox user interface has been completely refreshed and updated. This massive effort entailed:

* Refactoring the base HTML templates
* Moving from Boostrap 5.0 to Bootstrap 5.3
* Adopting the [Tabler](https://tabler.io/) UI theme
* Replacing slim-select with [Tom-Select](https://tom-select.js.org/)
* Displaying additional object attributes in dropdown form fields
* Enabling opt-in HTMX-powered navigation (see [#14736](https://github.com/netbox-community/netbox/issues/14736))
* Widespread cleanup & standardization of UI components

#### Dynamic REST API Fields ([#15087](https://github.com/netbox-community/netbox/issues/15087))

The REST API now supports specifying which fields to include in the response data. For example, the response to a request for

```
GET /api/dcim/sites/?fields=name,status,region,tenant
```

will include only the four specified fields in the representation of each site. Additionally, the underlying database queries effected by such requests have been optimized to omit fields which are not included in the response, resulting in a substantial performance improvement.

#### Strawberry GraphQL Engine ([#9856](https://github.com/netbox-community/netbox/issues/9856))

The GraphQL engine has been changed from using Graphene-Django to Strawberry-Django. Changes include:

* Queryset Optimizer - reduces the number of database queries when querying related tables
* Updated GraphiQL Browser
* The format for GraphQL query filters and lookups has changed. Please see the GraphQL documentation for details and examples.

#### Advanced Form Rendering Functionality ([#14739](https://github.com/netbox-community/netbox/issues/14739))

New resources have been introduced to enable advanced form rendering without a need for custom HTML templates. These include:

* FieldSet - Represents a grouping of form fields (replaces the use of lists/tuples)
* InlineFields - Multiple fields rendered on a single row
* TabbedGroups - Fieldsets rendered under navigable tabs within a form
* ObjectAttribute - Renders a read-only representation of a particular object attribute (for reference)

#### Legacy Admin UI Disabled ([#12325](https://github.com/netbox-community/netbox/issues/12325))

The legacy admin user interface is now disabled by default, and the few remaining views it provided have been relocated to the primary UI. NetBox deployments which still depend on the legacy admin functionality for plugins can enable it by setting the `DJANGO_ADMIN_ENABLED` configuration parameter to true.

### Enhancements

* [#12776](https://github.com/netbox-community/netbox/issues/12776) - Introduce the `htmx_table` template tag to simplify the rendering of embedded tables
* [#12851](https://github.com/netbox-community/netbox/issues/12851) - Replace the deprecated Bleach HTML sanitization library with nh3
* [#13283](https://github.com/netbox-community/netbox/issues/13283) - Display additional context on API-backed dropdown form fields (e.g. object descriptions)
* [#13918](https://github.com/netbox-community/netbox/issues/13918) - Add `facility` field to Location model
* [#14237](https://github.com/netbox-community/netbox/issues/14237) - Automatically clear dependent selection form fields when modifying a parent selection
* [#14279](https://github.com/netbox-community/netbox/issues/14279) - Make the current request available as context when running custom validators
* [#14454](https://github.com/netbox-community/netbox/issues/14454) - Include member devices in the REST API representation of virtual chassis
* [#14637](https://github.com/netbox-community/netbox/issues/14637) - Upgrade to Django 5.0
* [#14672](https://github.com/netbox-community/netbox/issues/14672) - Add support for Python 3.12
* [#14728](https://github.com/netbox-community/netbox/issues/14728) - The plugins list view has been moved from the legacy admin UI to the main NetBox UI
* [#14729](https://github.com/netbox-community/netbox/issues/14729) - All background task views have been moved from the legacy admin UI to the main NetBox UI
* [#14736](https://github.com/netbox-community/netbox/issues/14736) - Introduce a user preference to enable HTMX-powered navigation
* [#14438](https://github.com/netbox-community/netbox/issues/14438) - Track individual custom scripts as database objects
* [#15131](https://github.com/netbox-community/netbox/issues/15131) - Automatically annotate related object counts on REST API querysets
* [#15237](https://github.com/netbox-community/netbox/issues/15237) - Ensure consistent filtering ability for all model fields by testing for missing/incorrect filters
* [#15238](https://github.com/netbox-community/netbox/issues/15238) - Include the `description` field in "brief" REST API serializations
* [#15278](https://github.com/netbox-community/netbox/issues/15278) - BaseModelSerializer now takes a `nested` keyword argument allowing it to represent a related object
* [#15383](https://github.com/netbox-community/netbox/issues/15383) - Standardize filtering logic for the parents of recursively-nested models (parent & ancestor filters)
* [#15413](https://github.com/netbox-community/netbox/issues/15413) - The global search engine now supports caching of non-field object attributes
* [#15490](https://github.com/netbox-community/netbox/issues/15490) - Custom validators can now reference related object attributes via dotted paths
* [#15547](https://github.com/netbox-community/netbox/issues/15547) - Add comments field to CustomField model
* [#15712](https://github.com/netbox-community/netbox/issues/15712) - Enable image attachments for virtual machines
* [#15735](https://github.com/netbox-community/netbox/issues/15735) - Display all dates & times in ISO 8601 format consistently
* [#15754](https://github.com/netbox-community/netbox/issues/15754) - Remove `is_staff` restriction on admin menu items
* [#15764](https://github.com/netbox-community/netbox/issues/15764) - Increase maximum value of Device `vc_position` field
* [#15915](https://github.com/netbox-community/netbox/issues/15915) - Provide a comprehensive system status view with export functionality

### Bug Fixes (from Beta2)

* [#15630](https://github.com/netbox-community/netbox/issues/15630) - Ensure consistent toggling between light & dark UI modes
* [#15802](https://github.com/netbox-community/netbox/issues/15802) - Improve hyperlink color contrast in dark mode
* [#15809](https://github.com/netbox-community/netbox/issues/15809) - Fix GraphQL union support for nullable fields
* [#15815](https://github.com/netbox-community/netbox/issues/15815) - Convert dashboard widgets referencing old user/group models
* [#15826](https://github.com/netbox-community/netbox/issues/15826) - Update `EXEMPT_EXCLUDE_MODELS` to reference new user & group models
* [#15831](https://github.com/netbox-community/netbox/issues/15831) - Fix LDAP group mirroring
* [#15838](https://github.com/netbox-community/netbox/issues/15838) - Fix AttributeError exception when rendering custom date fields
* [#15852](https://github.com/netbox-community/netbox/issues/15852) - Update total results count when filtering object lists
* [#15853](https://github.com/netbox-community/netbox/issues/15853) - Correct background color for cable trace SVG images in dark mode
* [#15855](https://github.com/netbox-community/netbox/issues/15855) - Fix AttributeError exception when creating an event rule tied to a custom script
* [#15944](https://github.com/netbox-community/netbox/issues/15944) - Fix styling of paginator when displayed above an object list

### Other Changes

* [#10587](https://github.com/netbox-community/netbox/issues/10587) - Enable pagination and filtering for custom script logs
* [#12325](https://github.com/netbox-community/netbox/issues/12325) - The Django admin UI is now disabled by default (set `DJANGO_ADMIN_ENABLED` to True to enable it)
* [#12510](https://github.com/netbox-community/netbox/issues/12510) - Dropped support for legacy reports
* [#12795](https://github.com/netbox-community/netbox/issues/12795) - NetBox now uses custom User and Group models rather than the stock models provided by Django
* [#13647](https://github.com/netbox-community/netbox/issues/13647) - Squash all database migrations prior to v3.7
* [#14092](https://github.com/netbox-community/netbox/issues/14092) - Remove backward compatibility for importing plugin resources from `extras.plugins` (now `netbox.plugins`)
* [#14638](https://github.com/netbox-community/netbox/issues/14638) - Drop support for Python 3.8 and 3.9
* [#14657](https://github.com/netbox-community/netbox/issues/14657) - Remove backward compatibility for old permissions mapping under `ActionsMixin`
* [#14658](https://github.com/netbox-community/netbox/issues/14658) - Remove backward compatibility for importing `process_webhook()` from `extras.webhooks_worker` (now `extras.webhooks.send_webhook()`)
* [#14740](https://github.com/netbox-community/netbox/issues/14740) - Remove the obsolete `BootstrapMixin` form mixin class
* [#15042](https://github.com/netbox-community/netbox/issues/15042) - The logic for registering models & model features now executes under the `ready()` method of individual app configs, rather than relying on the `class_prepared` signal
* [#15099](https://github.com/netbox-community/netbox/issues/15099) - Remove obsolete `device_role` and `device_role_id` filters for devices
* [#15100](https://github.com/netbox-community/netbox/issues/15100) - Remove obsolete `NullableCharField` class
* [#15154](https://github.com/netbox-community/netbox/issues/15154) - The installation documentation been extended to include instructions and an example configuration file for uWSGI as an alternative to gunicorn
* [#15193](https://github.com/netbox-community/netbox/issues/15193) - Switch to compiled distribution of the `psycopg` library
* [#15277](https://github.com/netbox-community/netbox/issues/15277) - Replace references to ContentType without ObjectType proxy model & standardize field names
* [#15292](https://github.com/netbox-community/netbox/issues/15292) - Remove obsolete `device_role` attribute from Device model (this field was renamed to `role` in v3.6)
* [#15357](https://github.com/netbox-community/netbox/issues/15357) - The `object_type` field on the CustomField model has been renamed to `related_object_type` to avoid confusion with its `object_types` field
* [#15401](https://github.com/netbox-community/netbox/issues/15401) - PostgreSQL indexes and sequence tables for the relocated L2VPN models (see [#14311](https://github.com/netbox-community/netbox/issues/14311)) have been renamed 
* [#15462](https://github.com/netbox-community/netbox/issues/15462) - Relocate resources from the `utilities.utils` module
* [#15464](https://github.com/netbox-community/netbox/issues/15464) - The many-to-many relationships for ObjectPermission are now defined on the custom User and Group models
* [#15736](https://github.com/netbox-community/netbox/issues/15736) - Remove obsolete `annotated_date` template filter & `annotated_now` template tag
* [#15738](https://github.com/netbox-community/netbox/issues/15738) - Remove obsolete configuration parameters for date & time formatting
* [#15752](https://github.com/netbox-community/netbox/issues/15752) - Remove the obsolete `ENABLE_LOCALIZATION` configuration parameter
* [#15942](https://github.com/netbox-community/netbox/issues/15942) - Refactor `settings_and_registry()` context processor

### REST API Changes

* The `/api/extras/content-types/` endpoint has moved to `/api/extras/object-types/`
* The `/api/extras/reports/` endpoint has been removed
* The `description` field is now included by default when using "brief mode" for all relevant models
* dcim.Device
    * The obsolete read-only attribute `device_role` has been removed (replaced by `role` in v3.6)
* dcim.Location
    * Added the optional `location` field
* dcim.VirtualChassis
    * Added `members` field to list the member devices
* extras.CustomField
    * `content_types` has been renamed to `object_types`
    * `object_type` has been renamed to `related_object_type`
    * The `content_types` filter is now `object_type`
    * The `content_type_id` filter is now `object_type_id`
* extras.CustomLink
    * `content_types` has been renamed to `object_types`
    * The `content_types` filter is now `object_type`
    * The `content_type_id` filter is now `object_type_id`
* extras.EventRule
    * `content_types` has been renamed to `object_types`
    * The `content_types` filter is now `object_type`
    * The `content_type_id` filter is now `object_type_id`
* extras.ExportTemplate
    * `content_types` has been renamed to `object_types`
    * The `content_types` filter is now `object_type`
    * The `content_type_id` filter is now `object_type_id`
* extras.ImageAttachment
    * `content_type` has been renamed to `object_type`
    * The `content_type` filter is now `object_type`
* extras.SavedFilter
    * `content_types` has been renamed to `object_types`
    * The `content_types` filter is now `object_type`
    * The `content_type_id` filter is now `object_type_id`
* tenancy.ContactAssignment
    * `content_type` has been renamed to `object_type`
    * The `content_type_id` filter is now `object_type_id`
* users.Group
    * Added the `permissions` field
* users.User
    * Added the `permissions` field
