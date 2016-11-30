This guide demonstrates how to build and run NetBox as a Docker container. It assumes that the latest versions of [Docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/) are already installed in your host.

# Quickstart

To get NetBox up and running:

```no-highlight
# git clone -b master https://github.com/digitalocean/netbox.git
# cd netbox
# docker-compose up -d
```

The application will be available on http://localhost/ after a few minutes.

Default credentials:

* Username: **admin**
* Password: **admin**

# Configuration

You can configure the app at runtime using variables (see `docker-compose.yml`). Possible environment variables include:

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
