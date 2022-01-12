FROM alpine:3.13 as builder

RUN apk add --no-cache \
      bash \
      build-base \
      cargo \
      ca-certificates \
      cyrus-sasl-dev \
      graphviz \
      jpeg-dev \
      libevent-dev \
      libffi-dev \
      libressl-dev \
      libxslt-dev \
      musl-dev \
      openldap-dev \
      postgresql-dev \
      py3-pip \
      python3-dev \
  && python3 -m venv /opt/netbox/venv \
  && /opt/netbox/venv/bin/python3 -m pip install --upgrade \
      pip \
      setuptools \
      wheel

ARG NETBOX_PATH=.
COPY ${NETBOX_PATH}/requirements.txt requirements.extras.txt /
RUN /opt/netbox/venv/bin/pip install \
      -r /requirements.txt \
      -r /requirements.extras.txt

###
# Main stage
###

FROM alpine:3.13 as main


RUN apk add --no-cache \
      bash \
      ca-certificates \
      curl \
      graphviz \
      libevent \
      libffi \
      libjpeg-turbo \
      libressl \
      libxslt \
      postgresql-libs \
      python3 \
      py3-pip \
      ttf-ubuntu-font-family \
      unit \
      unit-python3

WORKDIR /opt

COPY --from=builder /opt/netbox/venv /opt/netbox/venv

ARG NETBOX_PATH=.
COPY ${NETBOX_PATH} /opt/netbox

COPY docker/configuration.docker.py /opt/netbox/netbox/netbox/configuration.py
COPY docker/docker-entrypoint.sh /opt/netbox/docker-entrypoint.sh
COPY docker/launch-netbox.sh /opt/netbox/launch-netbox.sh
COPY docker/startup_scripts/ /opt/netbox/startup_scripts/
COPY docker/initializers/ /opt/netbox/initializers/
COPY docker/configuration/ /etc/netbox/config/
COPY docker/nginx-unit.json /etc/unit/

WORKDIR /opt/netbox/netbox

# Must set permissions for '/opt/netbox/netbox/media' directory
# to g+w so that pictures can be uploaded to netbox.
RUN mkdir -p static /opt/unit/state/ /opt/unit/tmp/ \
      && chmod -R g+w media /opt/unit/ \
      && SECRET_KEY="dummy" /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py collectstatic --no-input

ENTRYPOINT [ "/opt/netbox/docker-entrypoint.sh" ]

CMD [ "/opt/netbox/launch-netbox.sh" ]

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


FROM main as ldap

RUN apk add --no-cache \
      libsasl \
      libldap \
      util-linux

COPY docker/ldap_config.docker.py /opt/netbox/netbox/netbox/ldap_config.py