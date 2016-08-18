FROM python:2.7-wheezy

WORKDIR /opt/netbox

ADD . /opt/netbox
#RUN git clone --depth 1 https://github.com/digitalocean/netbox.git -b master . \
RUN	pip install -r requirements.txt

ADD docker/docker-entrypoint.sh /docker-entrypoint.sh
ADD netbox/netbox/configuration.docker.py /opt/netbox/netbox/netbox/configuration.py

ENTRYPOINT [ "/docker-entrypoint.sh" ]

ADD docker/gunicorn_config.py /opt/netbox/
ADD docker/nginx.conf /etc/netbox-nginx/
VOLUME ["/etc/netbox-nginx/"]
