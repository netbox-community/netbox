# Sites

How you choose to use sites will depend on the nature of your organization, but typically a site will equate to a building or campus. For example, a chain of banks might create a site to represent each of its branches, a site for its corporate headquarters, and two additional sites for its presence in two colocation facilities.

Each site must be assigned one of the following operational statuses:

* Active
* Planned
* Retired

The site model provides a facility ID field which can be used to annotate a facility ID (such as a datacenter name) associated with the site. Each site may also have an autonomous system (AS) number and time zone associated with it. (Time zones are provided by the [pytz](https://pypi.org/project/pytz/) package.)

The site model also includes several fields for storing contact and address information.

## Regions

Sites can be arranged geographically using regions. A region might represent a continent, country, city, campus, or other area depending on your use case. Regions can be nested recursively to construct a hierarchy. For example, you might define several country regions, and within each of those several state or city regions to which sites are assigned.

---

# Racks

The rack model represents a physical two- or four-post equipment rack in which equipment is mounted. Each rack must be assigned to a site. Rack height is measured in *rack units* (U); racks are commonly between 42U and 48U tall, but NetBox allows you to define racks of arbitrary height. A toggle is provided to indicate whether rack units are in ascending or descending order.

Each rack is assigned a name and (optionally) a separate facility ID. This is helpful when leasing space in a data center your organization does not own: The facility will often assign a seemingly arbitrary ID to a rack (for example, "M204.313") whereas internally you refer to is simply as "R113." A unique serial number may also be associated with each rack.

A rack must be designated as one of the following types:

* 2-post frame
* 4-post frame
* 4-post cabinet
* Wall-mounted frame
* Wall-mounted cabinet

Each rack has two faces (front and rear) on which devices can be mounted. Rail-to-rail width may be 19 or 23 inches.

## Rack Groups

Racks can be arranged into groups. As with sites, how you choose to designate rack groups will depend on the nature of your organization. For example, if each site represents a campus, each group might represent a building within a campus. If each site represents a building, each rack group might equate to a floor or room.

Each rack group must be assigned to a parent site. Hierarchical recursion of rack groups is not currently supported.

## Rack Roles

Each rack can optionally be assigned a functional role. For example, you might designate a rack for compute or storage resources, or to house colocated customer devices. Rack roles are fully customizable.

## Rack Space Reservations

Users can reserve units within a rack for future use. Multiple non-contiguous rack units can be associated with a single reservation (but reservations cannot span multiple racks). A rack reservation may optionally designate a specific tenant.
