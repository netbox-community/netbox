from os import path as os_path
from json import dumps as json_dumps
from json import loads as json_loads
from jinja2 import FileSystemLoader, Environment

from django.core.management.base import BaseCommand
from django.conf import settings

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

    def add_arguments(self, parser):
        parser.add_argument(
            '--console',
            action='store_true',
            help="Print the generated schema to stdout"
        )
        parser.add_argument(
            '--file',
            action='store_true',
            help="Print the generated schema to the generated file"
        )

    def handle(self, *args, **kwargs):
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

        template_loader = FileSystemLoader(searchpath=f'{settings.TEMPLATES_DIR}/extras/')
        template_env = Environment(loader=template_loader)
        TEMPLATE_FILE = 'generated_schema.json'
        template = template_env.get_template(TEMPLATE_FILE)
        outputText = template.render(schemas=schemas)

        if kwargs['console']:
            print(json_dumps(json_loads(outputText), indent=4))

        if kwargs['file']:
            print()
            with open(f'{settings.BASE_DIR}/../contrib/generated_schema.json', 'w') as generated_json_file:
                generated_json_file.write(json_dumps(json_loads(outputText), indent=4))
                generated_json_file.close()
