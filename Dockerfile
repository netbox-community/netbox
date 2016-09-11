FROM python:2.7.12-wheezy

WORKDIR /opt/netbox
ENTRYPOINT [ "/docker-entrypoint.sh" ]
VOLUME ["/etc/netbox-nginx/"]

COPY requirements.txt /opt/netbox/requirements.txt
RUN apt-get update -qq && apt-get install -y libldap2-dev libsasl2-dev libssl-dev && \
    pip install gunicorn==17.5 && \
    pip install django-auth-ldap && \
    pip install -r requirements.txt

COPY docker/docker-entrypoint.sh /docker-entrypoint.sh
COPY docker/nginx.conf /etc/netbox-nginx/

COPY . /opt/netbox
COPY netbox/netbox/configuration.docker.py /opt/netbox/netbox/netbox/configuration.py
COPY docker/gunicorn_config.py /opt/netbox/
