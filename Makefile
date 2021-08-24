# This task clones the netbox configuration example, and populates for CI automated testing
# Note: the openssl command will be required in the runtime to populate the SECRETKEY.
# brew install openssl and/or apt-get install openssl
setup:
	rm -rfv netbox/netbox/configuration.py
	cp netbox/netbox/configuration.example.py netbox/netbox/configuration.py
	sed -i -e "s/ALLOWED_HOSTS = .*/ALLOWED_HOSTS = ['*']/g" netbox/netbox/configuration.py
	sed -i -e "s/SECRET_KEY = .*/SECRET_KEY = '$(shell openssl rand -hex 32)'/g" netbox/netbox/configuration.py
	sed -i -e "s/USER': .*/USER': 'postgres',/g" netbox/netbox/configuration.py
	sed -i -e "s/PASSWORD': .*/PASSWORD': '12345',/g" netbox/netbox/configuration.py
	sed -i -e "s/PLUGINS = .*/PLUGINS = ['netbox_virtual_circuit_plugin', 'netbox_bgp']/g" netbox/netbox/configuration.py

# spin up the required stack components to run the test suite
local-test-deps: reset-volumes
	docker-compose up -d postgres
	docker-compose up -d redis

local-test: setup local-test-deps
	tox -v

# Invoked by CI - so ensure the supporting env has been created if
# executing locally
unit-test:
	tox -v

# Reset will kill any running containers and remove them
reset:
	docker-compose kill
	docker-compose rm -f

# Remove all local volumes to ensure a restart from scratch
# docker-compose likes to "enable data caching" by not purging
# volumes between resets.
reset-volumes: reset
	docker volume rm -f netbox_netbox-media-files
	docker volume rm -f netbox_netbox-nginx-config
	docker volume rm -f netbox_netbox-postgres-data
	docker volume rm -f netbox_netbox-redis-data
	docker volume rm -f netbox_netbox-static-files
