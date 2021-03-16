# Sites

How you choose to employ sites when modeling your network may vary depending on the nature of your organization, but generally a site will equate to a building or campus. For example, a chain of banks might create a site to represent each of its branches, a site for its corporate headquarters, and two additional sites for its presence in two colocation facilities.

Each site must be assigned a unique name and may optionally be assigned to a region and/or tenant. The following operational statuses are available:

* Planned
* Staging
* Active
* Decommissioning
* Retired

The site model also provides a facility ID field which can be used to annotate a facility ID (such as a datacenter name) associated with the site. Each site may also have an autonomous system (AS) number and time zone associated with it. (Time zones are provided by the [pytz](https://pypi.org/project/pytz/) package.)

The site model also includes several fields for storing contact and address information as well as geolocation data (GPS coordinates).
