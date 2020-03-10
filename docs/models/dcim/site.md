# Sites

How you choose to use sites will depend on the nature of your organization, but typically a site will equate to a building or campus. For example, a chain of banks might create a site to represent each of its branches, a site for its corporate headquarters, and two additional sites for its presence in two colocation facilities.

Each site must be assigned one of the following operational statuses:

* Active
* Planned
* Retired

The site model provides a facility ID field which can be used to annotate a facility ID (such as a datacenter name) associated with the site. Each site may also have an autonomous system (AS) number and time zone associated with it. (Time zones are provided by the [pytz](https://pypi.org/project/pytz/) package.)

The site model also includes several fields for storing contact and address information.
