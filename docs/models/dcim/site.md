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

GPS coordinates of the site for geolocation. These are assumed to use the WGS84 datum (as reported by GPS).

### Web Mercator X & Y

!!! info "This field was introduced in NetBox v4.8."

The site's coordinates in the [Web Mercator](https://epsg.io/3857) (EPSG:3857) projection, in meters. These read-only values are calculated from the latitude and longitude (they are not stored in the database), and are useful for integrating with mapping tools that expect projected X/Y coordinates rather than latitude and longitude. They are calculated as:

```
X = longitude × (π / 180) × 6378137
Y = ln(tan(π / 4 + latitude × π / 360)) × 6378137
```

where `ln` is the natural logarithm. Because Web Mercator is undefined at the poles, latitudes beyond ±85.05113° are clamped to that bound.

!!! note
    Web Mercator (EPSG:3857) differs from the ellipsoidal World Mercator projection (EPSG:3395). Ensure the target system expects EPSG:3857 coordinates.
