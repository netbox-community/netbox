FROM ubuntu:14.04

RUN apt-get update && apt-get install -y \
	python2.7 \
	python-dev \
	git \
	python-pip \
	libxml2-dev \
	libxslt1-dev \
	libffi-dev \
	graphviz \
	libpq-dev \
	build-essential \
	gunicorn \
	--no-install-recommends \
	&& rm -rf /var/lib/apt/lists/* \
	&& mkdir -p /opt/netbox \
	&& cd /opt/netbox \
	&& git clone --depth 1 https://github.com/digitalocean/netbox.git -b master . \
	&& pip install -r requirements.txt \
	&& apt-get purge -y --auto-remove git build-essential

ADD docker/docker-entrypoint.sh /docker-entrypoint.sh
ADD netbox/netbox/configuration.docker.py /opt/netbox/netbox/netbox/configuration.py

ENTRYPOINT [ "/docker-entrypoint.sh" ]

ADD docker/gunicorn_config.py /opt/netbox/
ADD docker/nginx.conf /etc/netbox-nginx/
VOLUME ["/etc/netbox-nginx/"]
