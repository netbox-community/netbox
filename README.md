**The [2017 NetBox User Survey](https://goo.gl/forms/75HnNS2iE0Y1hVFH3) is open!** Please consider taking a moment to respond. Your feedback helps shape the pace and focus of NetBox development. The survey will remain open until 2017-03-31. Results will be published on the mailing list.

---

![NetBox](docs/netbox_logo.png "NetBox logo")

NetBox is an IP address management (IPAM) and data center infrastructure management (DCIM) tool. Initially conceived by the network engineering team at [DigitalOcean](https://www.digitalocean.com/), NetBox was developed specifically to address the needs of network and infrastructure engineers.

NetBox runs as a web application atop the [Django](https://www.djangoproject.com/) Python framework with a [PostgreSQL](http://www.postgresql.org/) database. For a complete list of requirements, see `requirements.txt`. The code is available [on GitHub](https://github.com/digitalocean/netbox).

The complete documentation for NetBox can be found at [Read the Docs](http://netbox.readthedocs.io/en/stable/).

Questions? Comments? Please subscribe to [the netbox-discuss mailing list](https://groups.google.com/forum/#!forum/netbox-discuss), or join us on IRC in **#netbox** on **irc.freenode.net**!

### Build Status

|             | python 2.7 |
|-------------|------------|
| **master** | [![Build Status](https://travis-ci.org/digitalocean/netbox.svg?branch=master)](https://travis-ci.org/digitalocean/netbox) |
| **develop** | [![Build Status](https://travis-ci.org/digitalocean/netbox.svg?branch=develop)](https://travis-ci.org/digitalocean/netbox) |

## Screenshots

![Screenshot of main page](docs/media/screenshot1.png "Main page")

![Screenshot of rack elevation](docs/media/screenshot2.png "Rack elevation")

![Screenshot of prefix hierarchy](docs/media/screenshot3.png "Prefix hierarchy")

# Installation

Please see [the documentation](http://netbox.readthedocs.io/en/stable/) for instructions on installing NetBox. To upgrade NetBox, please download the [latest release](https://github.com/digitalocean/netbox/releases) and run `upgrade.sh`.

## Alternative Installations

* [Docker container](http://netbox.readthedocs.io/en/stable/installation/docker/)
* [Heroku deployment](https://heroku.com/deploy?template=https://github.com/BILDQUADRAT/netbox/tree/heroku) (via [@mraerino](https://github.com/BILDQUADRAT/netbox/tree/heroku))
