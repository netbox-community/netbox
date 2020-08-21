# Racks

The rack model represents a physical two- or four-post equipment rack in which devices can be installed. Each rack must be assigned to a site, and may optionally be assigned to a rack group and/or tenant. Racks can also be organized by user-defined functional roles.

Rack height is measured in *rack units* (U); racks are commonly between 42U and 48U tall, but NetBox allows you to define racks of arbitrary height. A toggle is provided to indicate whether rack units are in ascending (from the ground up) or descending order.

Each rack is assigned a name and (optionally) a separate facility ID. This is helpful when leasing space in a data center your organization does not own: The facility will often assign a seemingly arbitrary ID to a rack (for example, "M204.313") whereas internally you refer to is simply as "R113." A unique serial number and asset tag may also be associated with each rack.

A rack must be designated as one of the following types:

* 2-post frame
* 4-post frame
* 4-post cabinet
* Wall-mounted frame
* Wall-mounted cabinet

Similarly, each rack must be assigned an operational status, which is one of the following:

* Reserved
* Available
* Planned
* Active
* Deprecated

Each rack has two faces (front and rear) on which devices can be mounted. Rail-to-rail width may be 10, 19, 21, or 23 inches. The outer width and depth of a rack or cabinet can also be annotated in millimeters or inches.
