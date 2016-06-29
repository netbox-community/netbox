<h1>Getting Started with NetBox and Docker</h1>

This guide assumes that the latest versions of [Docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/) are already installed in your host.

# Quickstart

To get NetBox up and running:

```
git clone https://github.com/digitalocean/netbox.git
cd netbox
docker-compose up -d
```

The application will be available on http://localhost/ after a few minutes.

Default credentials:
* user: admin
* password: admin

# Configuration
You can configure the app at runtime using variables (see docker-compose.yml).

Possible environment variables:

* SUPERUSER_NAME
* SUPERUSER_EMAIL
* SUPERUSER_PASSWORD
* ALLOWED_HOSTS
* DB_NAME
* DB_USER
* DB_PASSWORD
* DB_HOST
* DB_PORT
* SECRET_KEY
* EMAIL_SERVER
* EMAIL_PORT
* EMAIL_USERNAME
* EMAIL_PASSWORD
* EMAIL_TIMEOUT
* EMAIL_FROM
* LOGIN_REQUIRED
* MAINTENANCE_MODE
* NETBOX_USERNAME
* NETBOX_PASSWORD
* PAGINATE_COUNT
* TIME_ZONE
* DATE_FORMAT
* SHORT_DATE_FORMAT
* TIME_FORMAT
* SHORT_TIME_FORMAT
* DATETIME_FORMAT
* SHORT_DATETIME_FORMAT

