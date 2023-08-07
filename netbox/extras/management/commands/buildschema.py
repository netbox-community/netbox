import os
from json import dumps as json_dumps
from json import loads as json_loads

from django.conf import settings
from django.core.management.base import BaseCommand
from jinja2 import FileSystemLoader, Environment

from dcim.choices import (
    DeviceAirflowChoices, SubdeviceRoleChoices, ConsolePortTypeChoices, PowerPortTypeChoices,
    PowerOutletTypeChoices, PowerOutletFeedLegChoices, InterfaceTypeChoices, InterfacePoEModeChoices,
    InterfacePoETypeChoices, PortTypeChoices, WeightUnitChoices
)

TEMPLATE_FILENAME = 'generated_schema.json'
OUTPUT_FILENAME = 'contrib/generated_schema.json'


class Command(BaseCommand):
    help = "Generate the NetBox validation schemas."

    def add_arguments(self, parser):
        parser.add_argument(
            '--write',
            action='store_true',
            help="Write the generated schema to file"
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
        template = template_env.get_template(TEMPLATE_FILENAME)
        outputText = template.render(schemas=schemas)

        if kwargs['write']:
            # $root/contrib/generated_schema.json
            filename = os.path.join(os.path.split(settings.BASE_DIR)[0], OUTPUT_FILENAME)
            with open(filename, mode='w', encoding='UTF-8') as f:
                f.write(json_dumps(json_loads(outputText), indent=4))
                f.write('\n')
                f.close()
            self.stdout.write(self.style.SUCCESS(f"Schema written to {filename}."))
        else:
            self.stdout.write(outputText)
