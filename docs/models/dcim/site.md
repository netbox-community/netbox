# Sites

How you choose to employ sites when modeling your network may vary depending on the nature of your organization, but generally a site will equate to a building or campus. For example, a chain of banks might create a site to represent each of its branches, a site for its corporate headquarters, and two additional sites for its presence in two colocation facilities.

## Fields

### Name

The site's unique name.

### Slug

A unique URL-friendly identifier. (This value can be used for filtering.)

### Status

The site's operational status.

!!! tip
    Additional statuses may be defined by setting `Site.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Region

The parent [region](./region.md) to which the site belongs, if any.

### Facility

Data center or facility designation for identifying the site.

### ASNs

Each site can have multiple [AS numbers](../ipam/asn.md) assigned to it.

### Time Zone

The site's local time zone. (Time zones are provided by the [zoneinfo](https://docs.python.org/3/library/zoneinfo.html) library.)

### Physical Address

The site's physical address, used for mapping.

### Shipping Address

The address to use for deliveries destined for the site.

!!! tip
    You can also designate [points of contact](../../features/contacts.md) for each site to provide additional contact details.

### Latitude & Longitude

GPS coordinates of the site for geolocation.
