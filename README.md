# NetBox

NetBox is an IP address management (IPAM) and data center infrastructure management (DCIM) tool. Initially conceived by the network engineering team at [DigitalOcean](https://www.digitalocean.com/), NetBox was developed specifically to address the needs of network and infrastructure engineers.

NetBox runs as a web application atop the [Django](https://www.djangoproject.com/) Python framework with a [PostgreSQL](http://www.postgresql.org/) database. For a complete list of requirements, see `requirements.txt`. The code is available [on GitHub](https://github.com/digitalocean/netbox).

The complete documentation for Netbox can be found at [Read the Docs](http://netbox.readthedocs.io/en/latest/).

Questions? Comments? Please join us on IRC in **#netbox** on **irc.freenode.net**!

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

Please see docs/getting-started.md for instructions on installing NetBox.

To upgrade NetBox, please download the [latest release](https://github.com/digitalocean/netbox/releases) and run `upgrade.sh`.
