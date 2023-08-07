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

CHOICES_MAP = {
    'airflow_choices': DeviceAirflowChoices,
    'weight_unit_choices': WeightUnitChoices,
    'subdevice_role_choices': SubdeviceRoleChoices,
    'console_port_type_choices': ConsolePortTypeChoices,
    'console_server_port_type_choices': ConsolePortTypeChoices,  # Reusing ConsolePortTypeChoices
    'power_port_type_choices': PowerPortTypeChoices,
    'power_outlet_type_choices': PowerOutletTypeChoices,
    'power_outlet_feedleg_choices': PowerOutletFeedLegChoices,
    'interface_type_choices': InterfaceTypeChoices,
    'interface_poe_mode_choices': InterfacePoEModeChoices,
    'interface_poe_type_choices': InterfacePoETypeChoices,
    'front_port_type_choices': PortTypeChoices,
    'rear_port_type_choices': PortTypeChoices,  # Reusing PortTypeChoices
}


class Command(BaseCommand):
    help = "Generate the NetBox validation schemas."

    def add_arguments(self, parser):
        parser.add_argument(
            '--write',
            action='store_true',
            help="Write the generated schema to file"
        )

    def handle(self, *args, **kwargs):
        template_loader = FileSystemLoader(searchpath=f'{settings.TEMPLATES_DIR}/extras/')
        template_env = Environment(loader=template_loader)
        template = template_env.get_template(TEMPLATE_FILENAME)
        context = {
            key: json_dumps(choices.values())
            for key, choices in CHOICES_MAP.items()
        }
        rendered = template.render(**context)

        if kwargs['write']:
            # $root/contrib/generated_schema.json
            filename = os.path.join(os.path.split(settings.BASE_DIR)[0], OUTPUT_FILENAME)
            with open(filename, mode='w', encoding='UTF-8') as f:
                f.write(json_dumps(json_loads(rendered), indent=4))
                f.write('\n')
                f.close()
            self.stdout.write(self.style.SUCCESS(f"Schema written to {filename}."))
        else:
            self.stdout.write(rendered)
