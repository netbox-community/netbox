from __future__ import unicode_literals

import re
import time

import paramiko
import xmltodict
from ncclient import manager

CONNECT_TIMEOUT = 5  # seconds


class RPCClient(object):

    def __init__(self, device, username='', password=''):
        self.username = username
        self.password = password
        try:
            self.host = str(device.primary_ip.address.ip)
        except AttributeError:
            raise Exception("Specified device ({}) does not have a primary IP defined.".format(device))

    def get_inventory(self):
        """
        Returns a dictionary representing the device chassis and installed inventory items.

        {
            'chassis': {
                'serial': <str>,
                'description': <str>,
            }
            'items': [
                {
                    'name': <str>,
                    'part_id': <str>,
                    'serial': <str>,
                },
                ...
            ]
        }
        """
        raise NotImplementedError("Feature not implemented for this platform.")


class SSHClient(RPCClient):
    def __enter__(self):

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(
                self.host,
                username=self.username,
                password=self.password,
                timeout=CONNECT_TIMEOUT,
                allow_agent=False,
                look_for_keys=False,
            )
        except paramiko.AuthenticationException:
            # Try default credentials if the configured creds don't work
            try:
                default_creds = self.default_credentials
                if default_creds.get('username') and default_creds.get('password'):
                    self.ssh.connect(
                        self.host,
                        username=default_creds['username'],
                        password=default_creds['password'],
                        timeout=CONNECT_TIMEOUT,
                        allow_agent=False,
                        look_for_keys=False,
                    )
                else:
                    raise ValueError('default_credentials are incomplete.')
            except AttributeError:
                raise paramiko.AuthenticationException

        self.session = self.ssh.invoke_shell()
        self.session.recv(1000)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ssh.close()

    def _send(self, cmd, pause=1):
        self.session.send('{}\n'.format(cmd))
        data = ''
        time.sleep(pause)
        while self.session.recv_ready():
            data += self.session.recv(4096).decode()
            if not data:
                break
        return data


class JunosNC(RPCClient):
    """
    NETCONF client for Juniper Junos devices
    """

    def __enter__(self):

        # Initiate a connection to the device
        self.manager = manager.connect(host=self.host, username=self.username, password=self.password,
                                       hostkey_verify=False, timeout=CONNECT_TIMEOUT)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        # Close the connection to the device
        self.manager.close_session()

    def get_inventory(self):

        def glean_items(node, depth=0):
            items = []
            items_list = node.get('chassis{}-module'.format('-sub' * depth), [])
            # Junos like to return single children directly instead of as a single-item list
            if hasattr(items_list, 'items'):
                items_list = [items_list]
            for item in items_list:
                m = {
                    'name': item['name'],
                    'part_id': item.get('model-number') or item.get('part-number', ''),
                    'serial': item.get('serial-number', ''),
                }
                child_items = glean_items(item, depth + 1)
                if child_items:
                    m['items'] = child_items
                items.append(m)
            return items

        rpc_reply = self.manager.dispatch('get-chassis-inventory')
        inventory_raw = xmltodict.parse(rpc_reply.xml)['rpc-reply']['chassis-inventory']['chassis']

        result = dict()

        # Gather chassis data
        result['chassis'] = {
            'serial': inventory_raw['serial-number'],
            'description': inventory_raw['description'],
        }

        # Gather inventory items
        result['items'] = glean_items(inventory_raw)

        return result


class IOSSSH(SSHClient):
    """
    SSH client for Cisco IOS devices
    """

    def get_inventory(self):
        def version():

            def parse(cmd_out, rex):
                for i in cmd_out:
                    match = re.search(rex, i)
                    if match:
                        return match.groups()[0]

            sh_ver = self._send('show version').split('\r\n')
            return {
                'serial': parse(sh_ver, r'Processor board ID ([^\s]+)'),
                'description': parse(sh_ver, r'cisco ([^\s]+)')
            }

        def items(chassis_serial=None):
            cmd = self._send('show inventory').split('\r\n\r\n')
            for i in cmd:
                i_fmt = i.replace('\r\n', ' ')
                try:
                    m_name = re.search(r'NAME: "([^"]+)"', i_fmt).group(1)
                    m_pid = re.search(r'PID: ([^\s]+)', i_fmt).group(1)
                    m_serial = re.search(r'SN: ([^\s]+)', i_fmt).group(1)
                    # Omit built-in items and those with no PID
                    if m_serial != chassis_serial and m_pid.lower() != 'unspecified':
                        yield {
                            'name': m_name,
                            'part_id': m_pid,
                            'serial': m_serial,
                        }
                except AttributeError:
                    continue

        self._send('term length 0')
        sh_version = version()

        return {
            'chassis': sh_version,
            'items': list(items(chassis_serial=sh_version.get('serial')))
        }


class OpengearSSH(SSHClient):
    """
    SSH client for Opengear devices
    """
    default_credentials = {
        'username': 'root',
        'password': 'default',
    }

    def get_inventory(self):

        try:
            stdin, stdout, stderr = self.ssh.exec_command("showserial")
            serial = stdout.readlines()[0].strip()
        except Exception:
            raise RuntimeError("Failed to glean chassis serial from device.")
        # Older models don't provide serial info
        if serial == "No serial number information available":
            serial = ''

        try:
            stdin, stdout, stderr = self.ssh.exec_command("config -g config.system.model")
            description = stdout.readlines()[0].split(' ', 1)[1].strip()
        except Exception:
            raise RuntimeError("Failed to glean chassis description from device.")

        return {
            'chassis': {
                'serial': serial,
                'description': description,
            },
            'items': [],
        }


# For mapping platform -> NC client
RPC_CLIENTS = {
    'juniper-junos': JunosNC,
    'cisco-ios': IOSSSH,
    'opengear': OpengearSSH,
}
