FROM vaporio/python:3.7 as builder

RUN apt-get update -qy \
 && apt-get install -y \
      libsasl2-dev \
      graphviz \
      libjpeg-dev \
      libffi-dev \
      libxml2-dev \
      libxslt1-dev \
      libldap2-dev \
      libpq-dev \
      ttf-ubuntu-font-family \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /install

RUN pip install --prefix="/install" --no-warn-script-location \
# gunicorn is used for launching netbox
      gunicorn \
      greenlet \
      eventlet \
# napalm is used for gathering information from network devices
      napalm \
# ruamel is used in startup_scripts
      'ruamel.yaml>=0.15,<0.16' \
# django-storages was introduced in 2.7 and is optional
      django-storages

ARG NETBOX_PATH=.
COPY ${NETBOX_PATH}/requirements.txt /
COPY ${NETBOX_PATH}/requirements.extras.txt /
RUN pip install --prefix="/install" --no-warn-script-location -r /requirements.txt -r /requirements.extras.txt

FROM vaporio/python:3.7-slim

RUN apt-get update -qy \
 && apt-get install -y \
      libsasl2-dev \
      graphviz \
      libjpeg-dev \
      libffi-dev \
      libxml2-dev \
      libxslt1-dev \
      libldap2-dev \
      libpq-dev \
      ttf-ubuntu-font-family \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt

COPY --from=builder /install /usr/local

ARG NETBOX_PATH=.
COPY ${NETBOX_PATH} /opt/netbox

COPY docker/configuration.docker.py /opt/netbox/netbox/netbox/configuration.py
COPY docker/configuration/gunicorn_config.py /etc/netbox/config/
COPY docker/nginx.conf /etc/netbox-nginx/nginx.conf
COPY docker/docker-entrypoint.sh /opt/netbox/docker-entrypoint.sh
COPY docker/startup_scripts/ /opt/netbox/startup_scripts/
COPY docker/initializers/ /opt/netbox/initializers/
COPY docker/configuration/configuration.py /etc/netbox/config/configuration.py

WORKDIR /opt/netbox/netbox

RUN mkdir -p static && chmod g+w static media

ENTRYPOINT [ "/opt/netbox/docker-entrypoint.sh" ]

CMD ["gunicorn", "-c /etc/netbox/config/gunicorn_config.py", "netbox.wsgi"]

ARG BUILD_VERSION
ARG BUILD_DATE
ARG VCS_REF

LABEL maintainer="Vapor IO" \
# See http://label-schema.org/rc1/#build-time-labels
# Also https://microbadger.com/labels
      org.label-schema.schema-version="1.0" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="vaporio/netbox" \
      org.label-schema.vcs-url="https://github.com/vapor-ware/netbox" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vendor="Vapor IO" \
      org.label-schema.version=$BUILD_VERSION \
      org.label-schema.description="A container based distribution of Vapor IO's Netbox, the free and open IPAM and DCIM solution." \
      org.label-schema.url="https://github.com/vapor-ware/netbox" \
      org.label-schema.usage="https://github.com/vapor-ware/netbox/wiki" \
      org.label-schema.vcs-url="https://github.com/vapor-ware/netbox.git" \
# See https://github.com/opencontainers/image-spec/blob/master/annotations.md#pre-defined-annotation-keys
      org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.title="vaporio/netbox" \
      org.opencontainers.image.description="A container based distribution of Vapor IO's Netbox, the free and open IPAM and DCIM solution." \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.authors="Vapor IO." \
      org.opencontainers.image.vendor="Vapor IO" \
      org.opencontainers.image.url="https://github.com/vapor-ware/netbox" \
      org.opencontainers.image.documentation="https://github.com/vapor-ware/netbox/wiki" \
      org.opencontainers.image.source="https://github.com/vapor-ware/netbox.git" \
      org.opencontainers.image.revision=$VCS_REF \
      org.opencontainers.image.version=$BUILD_VERSION
