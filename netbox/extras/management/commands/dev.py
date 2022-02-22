import typing as t
import threading
from django.core.management import call_command
from django.contrib.staticfiles.management.commands import runserver


class Command(runserver.Command):
    """Run the NetBox development server.

    Builds UI source files, runs `collectstatic`, starts the Django development web server, and
    watches UI source files for changes.
    """

    def handle(self, *args: t.Any, **options: t.Any) -> t.Optional[str]:
        # Run the UI development server in a separate thread so file watching doesn't block the
        # Django development server running in the main thread.
        ui_dev = threading.Thread(name="uidev", target=lambda: call_command("uidev"))
        ui_dev.start()
        # Run `collectstatic`.
        call_command("collectstatic", interactive=False)
        # Run the original `runserver` command.
        return super().handle(*args, **options)
