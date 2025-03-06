import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from jinja2 import FileSystemLoader, Environment

from dcim.choices import *
from netbox.choices import WeightUnitChoices

TEMPLATE_FILENAME = 'devicetype_schema.jinja2'
OUTPUT_FILENAME = 'contrib/generated_schema.json'

CHOICES_MAP = {
    'airflow_choices': DeviceAirflowChoices,
    'weight_unit_choices': WeightUnitChoices,
    'subdevice_role_choices': SubdeviceRoleChoices,
    'console_port_type_choices': ConsolePortTypeChoices,
    'console_server_port_type_choices': ConsolePortTypeChoices,
    'power_port_type_choices': PowerPortTypeChoices,
    'power_outlet_type_choices': PowerOutletTypeChoices,
    'power_outlet_feedleg_choices': PowerOutletFeedLegChoices,
    'interface_type_choices': InterfaceTypeChoices,
    'interface_poe_mode_choices': InterfacePoEModeChoices,
    'interface_poe_type_choices': InterfacePoETypeChoices,
    'front_port_type_choices': PortTypeChoices,
    'rear_port_type_choices': PortTypeChoices,
}


class Command(BaseCommand):
    help = "Generate JSON schema for validating NetBox device type definitions"

    def add_arguments(self, parser):
        parser.add_argument(
            '--write',
            action='store_true',
            help="Write the generated schema to file"
        )

    def handle(self, *args, **kwargs):
        # Initialize template
        template_loader = FileSystemLoader(searchpath=f'{settings.TEMPLATES_DIR}/extras/schema/')
        template_env = Environment(loader=template_loader)
        template = template_env.get_template(TEMPLATE_FILENAME)

        # Render template
        context = {
            key: json.dumps(choices.values())
            for key, choices in CHOICES_MAP.items()
        }
        rendered = template.render(**context)

        if kwargs['write']:
            # $root/contrib/generated_schema.json
            filename = os.path.join(os.path.split(settings.BASE_DIR)[0], OUTPUT_FILENAME)
            with open(filename, mode='w', encoding='UTF-8') as f:
                f.write(json.dumps(json.loads(rendered), indent=4))
                f.write('\n')
                f.close()
            self.stdout.write(self.style.SUCCESS(f"Schema written to {filename}."))
        else:
            self.stdout.write(rendered)
