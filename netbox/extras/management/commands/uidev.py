import shutil
import subprocess
import typing as t
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Provide access to the underlying UI development server."""

    def handle(self, *args: t.Any, **options: t.Any) -> t.Optional[str]:
        """Run the `npm run dev` command via a separate process and write the output."""

        project_root = Path(__file__).parent.parent.parent.parent
        project_static = project_root / "project-static"

        npm = shutil.which("npm")
        npm_args = tuple(str(i) for i in (npm, "--prefix", project_static, "run", "--silent", "dev"))

        try:
            self.stdout.write(self.style.SUCCESS("Watching UI files..."))
            proc = subprocess.Popen(
                args=npm_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=project_static,
            )
            while True:
                out = proc.stdout.readline().decode()
                if out == '' and proc.poll() is not None:
                    break
                if out:
                    self.stdout.write(out.strip())

        except BaseException as exc:
            proc.kill()
            raise CommandError("Error while running command '{}'".format(" ".join(npm_args))) from exc
