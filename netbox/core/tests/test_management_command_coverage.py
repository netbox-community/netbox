import ast
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.test import SimpleTestCase

EXCLUDED_CUSTOM_COMMANDS = {
    # Deprecated; excluded from management command test coverage by #22124.
    'housekeeping',
}


class ManagementCommandCoverageTestCase(SimpleTestCase):
    def test_all_custom_management_commands_have_tests(self):
        custom_commands = self._get_custom_management_commands()
        tested_commands = self._get_tested_management_commands()

        self.assertTrue(
            custom_commands,
            'No custom management commands were discovered; check command discovery logic.',
        )

        missing_commands = sorted(custom_commands - tested_commands - EXCLUDED_CUSTOM_COMMANDS)

        self.assertEqual(
            missing_commands,
            [],
            msg=(f'Tests are missing for custom management commands: {", ".join(missing_commands)}'),
        )

    @staticmethod
    def _get_custom_management_commands():
        base_dir = Path(settings.BASE_DIR).resolve()
        commands = set()

        for app_config in apps.get_app_configs():
            app_path = Path(app_config.path).resolve()
            if not app_path.is_relative_to(base_dir):
                continue

            commands_path = app_path / 'management' / 'commands'
            if not commands_path.exists():
                continue

            commands.update(path.stem for path in commands_path.glob('*.py') if not path.name.startswith('_'))

        return commands

    @staticmethod
    def _get_tested_management_commands():
        base_dir = Path(settings.BASE_DIR).resolve()
        commands = set()

        for test_file in base_dir.glob('*/tests/test_management_commands.py'):
            tree = ast.parse(test_file.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not _is_call_command(node.func):
                    continue
                if not node.args:
                    continue

                command_name = node.args[0]
                if isinstance(command_name, ast.Constant) and isinstance(command_name.value, str):
                    commands.add(command_name.value)

        return commands


def _is_call_command(func):
    if isinstance(func, ast.Name):
        return func.id == 'call_command'

    if isinstance(func, ast.Attribute):
        return func.attr == 'call_command'

    return False
