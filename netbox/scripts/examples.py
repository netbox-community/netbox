from django.utils.text import slugify

from dcim.constants import *
from dcim.models import Device, DeviceRole, DeviceType, Site
from extras.scripts import *


class NewBranchScript(Script):
    script_name = "New Branch"
    script_description = "Provision a new branch site"
    script_fields = ['site_name', 'switch_count', 'switch_model']

    site_name = StringVar(
        description="Name of the new site"
    )
    switch_count = IntegerVar(
        description="Number of access switches to create"
    )
    switch_model = ObjectVar(
        description="Access switch model",
        queryset=DeviceType.objects.filter(
            manufacturer__name='Cisco',
            model__in=['Catalyst 3560X-48T', 'Catalyst 3750X-48T']
        )
    )
    x = BooleanVar(
        description="Check me out"
    )

    def run(self, data):

        # Create the new site
        site = Site(
            name=data['site_name'],
            slug=slugify(data['site_name']),
            status=SITE_STATUS_PLANNED
        )
        site.save()
        self.log_success("Created new site: {}".format(site))

        # Create access switches
        switch_role = DeviceRole.objects.get(name='Access Switch')
        for i in range(1, data['switch_count'] + 1):
            switch = Device(
                device_type=data['switch_model'],
                name='{}-switch{}'.format(site.slug, i),
                site=site,
                status=DEVICE_STATUS_PLANNED,
                device_role=switch_role
            )
            switch.save()
            self.log_success("Created new switch: {}".format(switch))

        # Generate a CSV table of new devices
        output = [
            'name,make,model'
        ]
        for switch in Device.objects.filter(site=site):
            attrs = [
                switch.name,
                switch.device_type.manufacturer.name,
                switch.device_type.model
            ]
            output.append(','.join(attrs))

        return '\n'.join(output)
