from os import path as os_path
from jinja2 import FileSystemLoader, Environment
from json import dumps as json_dumps

from django.core.management.base import BaseCommand

from dcim.choices import DeviceAirflowChoices
from dcim.choices import SubdeviceRoleChoices
from dcim.choices import ConsolePortTypeChoices
from dcim.choices import PowerPortTypeChoices
from dcim.choices import PowerOutletTypeChoices, PowerOutletFeedLegChoices
from dcim.choices import InterfaceTypeChoices, InterfacePoEModeChoices, InterfacePoETypeChoices
from dcim.choices import PortTypeChoices
from dcim.choices import WeightUnitChoices


class Command(BaseCommand):
    help = "Generate the NetBox validation schemas."

    def handle(self, *args, **options):
        schemas = {}
        schemas["airflow_choices"] = json_dumps(DeviceAirflowChoices.values())
        schemas["weight_unit_choices"] = json_dumps(WeightUnitChoices.values())
        schemas["subdevice_role_choices"] = json_dumps(SubdeviceRoleChoices.values())
        schemas["console_port_type_choices"] = json_dumps(ConsolePortTypeChoices.values())  # console-ports and console-server-ports
        schemas["power_port_type_choices"] = json_dumps(PowerPortTypeChoices.values())
        schemas["power_outlet_type_choices"] = json_dumps(PowerOutletTypeChoices.values())
        schemas["power_outlet_feedleg_choices"] = json_dumps(PowerOutletFeedLegChoices.values())
        schemas["interface_type_choices"] = json_dumps(InterfaceTypeChoices.values())
        schemas["interface_poe_mode_choices"] = json_dumps(InterfacePoEModeChoices.values())
        schemas["interface_poe_type_choices"] = json_dumps(InterfacePoETypeChoices.values())
        schemas["port_type_choices"] = json_dumps(PortTypeChoices.values())  # front-ports and rear-ports

        template_loader = FileSystemLoader(searchpath=f'{os_path.dirname(__file__)}/../templates')
        template_env = Environment(loader=template_loader)
        TEMPLATE_FILE = 'generated_schema.j2'
        template = template_env.get_template(TEMPLATE_FILE)
        outputText = template.render(schemas=schemas)

        print(outputText)
