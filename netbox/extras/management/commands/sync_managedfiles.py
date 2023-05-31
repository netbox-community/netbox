import os
import pkgutil
from importlib import import_module

from django.conf import settings
from django.core.management.base import BaseCommand

from extras.models import ScriptModule, ReportModule
from netbox.config import Config


def find_modules(root_path):
    modules = list(pkgutil.iter_modules([root_path]))
    filenames = []
    for importer, module_name, ispkg in modules:
        try:
            module = importer.find_module(module_name).load_module(module_name)
            rel_path = os.path.relpath(module.__file__, root_path)
            filenames.append(rel_path)
        except ImportError:
            pass
    return filenames

def create_files(cls, root_name, filenames):
    managed_files = [
        cls(file_root=root_name, file_path=filename)
        for filename in filenames
        if not cls.objects.filter(file_path=filename).exists()
    ]
    return cls.objects.bulk_create(managed_files)

def remove_files(cls, filenames):
    missing_files = cls.objects.exclude(file_path__in=filenames)
    removed = missing_files.count()
    missing_files.delete()
    return removed


class Command(BaseCommand):
    help = "Synchronize locally present managed files with database"

    def handle(self, *args, **options):

        # Sync ScriptModule files
        if options['verbosity']:
            self.stdout.write("[*] Sync ScriptModule files")
        filenames = find_modules(settings.SCRIPTS_ROOT)
        created = create_files(ScriptModule, 'scripts', filenames)
        if options['verbosity']:
            if created:
                self.stdout.write(f"[*] {len(created)} ScriptModule files created")
            else:
                self.stdout.write("[*] No ScriptModule files created")
        removed = remove_files(ScriptModule, filenames)
        if options['verbosity']:
            if removed:
                self.stdout.write(f"[*] {removed} ScriptModule files removed")
            else:
                self.stdout.write("[*] No ScriptModule files removed")

        # Sync ReportModule files
        if options['verbosity']:
            self.stdout.write("[*] Sync ReportModule files")
        #sync_files(ReportModule, 'reports', settings.REPORTS_ROOT)
        filenames = find_modules(settings.REPORTS_ROOT)
        created = create_files(ReportModule, 'reports', filenames)
        if options['verbosity']:
            if created:
                self.stdout.write(f"[*] {len(created)} ScriptModule files created")
            else:
                self.stdout.write("[*] No ScriptModule files created")
        removed = remove_files(ReportModule, filenames)
        if options['verbosity']:
            if removed:
                self.stdout.write(f"[*] {removed} ScriptModule files removed")
            else:
                self.stdout.write("[*] No ScriptModule files removed")

        if options['verbosity']:
            self.stdout.write("Finished.", self.style.SUCCESS)
