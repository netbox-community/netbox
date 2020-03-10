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
