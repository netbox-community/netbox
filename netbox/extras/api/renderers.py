import json
from rest_framework import renderers


# IP address family designations
AF = {
    4: 'A',
    6: 'AAAA',
}


class FormlessBrowsableAPIRenderer(renderers.BrowsableAPIRenderer):
    """
    An instance of the browseable API with forms suppressed. Useful for POST endpoints that don't create objects.
    """
    def show_form_for_method(self, *args, **kwargs):
        return False


class BINDZoneRenderer(renderers.BaseRenderer):
    """
    Generate a BIND zone file from a list of DNS records.
        Required fields: `name`, `primary_ip`
    """
    media_type = 'text/plain'
    format = 'bind-zone'

    def render(self, data, media_type=None, renderer_context=None):
        records = []
        for record in data:
            if record.get('name') and record.get('primary_ip'):
                try:
                    records.append("{} IN {} {}".format(
                        record['name'],
                        AF[record['primary_ip']['family']],
                        record['primary_ip']['address'].split('/')[0],
                    ))
                except KeyError:
                    pass
        return '\n'.join(records)


class FlatJSONRenderer(renderers.BaseRenderer):
    """
    Flattens a nested JSON response.
    """
    format = 'json_flat'
    media_type = 'application/json'

    def render(self, data, media_type=None, renderer_context=None):

        def flatten(entry):
            for key, val in entry.items():
                if isinstance(val, dict):
                    for child_key, child_val in flatten(val):
                        yield "{}_{}".format(key, child_key), child_val
                else:
                    yield key, val

        return json.dumps([dict(flatten(i)) for i in data])


class FreeRADIUSClientsRenderer(renderers.BaseRenderer):
    """
    Generate a FreeRADIUS clients.conf file from a list of Secrets.
    """
    media_type = 'text/plain'
    format = 'freeradius'

    CLIENT_TEMPLATE = """client {name} {{
    ipaddr = {ip}
    secret = {secret}
}}"""

    def render(self, data, media_type=None, renderer_context=None):
        clients = []
        try:
            for secret in data:
                if secret['device']['primary_ip'] and secret['plaintext']:
                    client = self.CLIENT_TEMPLATE.format(
                        name=secret['device']['name'],
                        ip=secret['device']['primary_ip']['address'].split('/')[0],
                        secret=secret['plaintext']
                    )
                    clients.append(client)
        except:
            pass
        return '\n'.join(clients)
