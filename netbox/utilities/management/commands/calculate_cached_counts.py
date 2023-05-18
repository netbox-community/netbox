from django.core.management.base import BaseCommand
from django.core.management.color import no_style

from dcim.models import Device
from virtualization.models import VirtualMachine


def recalculate_device_counts():
    for device in Device.objects.all():
        device._console_port_count = device.consoleports.count()
        device._console_server_port_count = device.consoleserverports.count()
        device._interface_count = device.interfaces.count()
        device._front_port_count = device.frontports.count()
        device._rear_port_count = device.rearports.count()
        device._device_bay_count = device.devicebays.count()
        device._inventory_item_count = device.inventoryitems.count()
        device._power_port_count = device.powerports.count()
        device._power_outlet_count = device.poweroutlets.count()
        device.save()


def recalculate_virtual_machine_counts():
    for vm in VirtualMachine.objects.all():
        vm._interface_count = vm.interfaces.count()
        vm.save()


class Command(BaseCommand):
    help = "Recalculate cached counts"

    def handle(self, *model_names, **options):
        self.stdout.write('Recalculating device counts...')
        recalculate_device_counts()
        self.stdout.write('Recalculating virtual machine counts...')
        recalculate_virtual_machine_counts()
        self.stdout.write(self.style.SUCCESS('Finished.'))
