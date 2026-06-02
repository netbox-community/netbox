import tempfile
from pathlib import Path

from django.core.exceptions import NON_FIELD_ERRORS
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.choices import ManagedFileRootPathChoices
from core.models import DataSource, ObjectType
from dcim.forms import SiteForm
from dcim.models import Site
from extras.choices import CustomFieldTypeChoices
from extras.forms import SavedFilterForm
from extras.forms.model_forms import CustomFieldChoiceSetForm
from extras.forms.scripts import ScriptFileForm
from extras.models import CustomField, CustomFieldChoiceSet, ScriptModule


class CustomFieldModelFormTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        object_type = ObjectType.objects.get_for_model(Site)
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Choice Set 1',
            extra_choices=(('a', 'A'), ('b', 'B'), ('c', 'C'))
        )

        cf_text = CustomField.objects.create(name='text', type=CustomFieldTypeChoices.TYPE_TEXT)
        cf_text.object_types.set([object_type])

        cf_longtext = CustomField.objects.create(name='longtext', type=CustomFieldTypeChoices.TYPE_LONGTEXT)
        cf_longtext.object_types.set([object_type])

        cf_integer = CustomField.objects.create(name='integer', type=CustomFieldTypeChoices.TYPE_INTEGER)
        cf_integer.object_types.set([object_type])

        cf_integer = CustomField.objects.create(name='decimal', type=CustomFieldTypeChoices.TYPE_DECIMAL)
        cf_integer.object_types.set([object_type])

        cf_boolean = CustomField.objects.create(name='boolean', type=CustomFieldTypeChoices.TYPE_BOOLEAN)
        cf_boolean.object_types.set([object_type])

        cf_date = CustomField.objects.create(name='date', type=CustomFieldTypeChoices.TYPE_DATE)
        cf_date.object_types.set([object_type])

        cf_datetime = CustomField.objects.create(name='datetime', type=CustomFieldTypeChoices.TYPE_DATETIME)
        cf_datetime.object_types.set([object_type])

        cf_url = CustomField.objects.create(name='url', type=CustomFieldTypeChoices.TYPE_URL)
        cf_url.object_types.set([object_type])

        cf_json = CustomField.objects.create(name='json', type=CustomFieldTypeChoices.TYPE_JSON)
        cf_json.object_types.set([object_type])

        cf_select = CustomField.objects.create(
            name='select',
            type=CustomFieldTypeChoices.TYPE_SELECT,
            choice_set=choice_set
        )
        cf_select.object_types.set([object_type])

        cf_multiselect = CustomField.objects.create(
            name='multiselect',
            type=CustomFieldTypeChoices.TYPE_MULTISELECT,
            choice_set=choice_set
        )
        cf_multiselect.object_types.set([object_type])

        cf_object = CustomField.objects.create(
            name='object',
            type=CustomFieldTypeChoices.TYPE_OBJECT,
            related_object_type=ObjectType.objects.get_for_model(Site)
        )
        cf_object.object_types.set([object_type])

        cf_multiobject = CustomField.objects.create(
            name='multiobject',
            type=CustomFieldTypeChoices.TYPE_MULTIOBJECT,
            related_object_type=ObjectType.objects.get_for_model(Site)
        )
        cf_multiobject.object_types.set([object_type])

    def test_empty_values(self):
        """
        Test that empty custom field values are stored as null
        """
        form = SiteForm({
            'name': 'Site 1',
            'slug': 'site-1',
            'status': 'active',
        })
        self.assertTrue(form.is_valid())
        instance = form.save()

        for field_type, _ in CustomFieldTypeChoices.CHOICES:
            self.assertIn(field_type, instance.custom_field_data)
            self.assertIsNone(instance.custom_field_data[field_type])


class CustomFieldChoiceSetFormTestCase(TestCase):

    def test_escaped_colons_preserved_on_edit(self):
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Test Choice Set',
            extra_choices=[['foo:bar', 'label'], ['value', 'label:with:colons']]
        )

        form = CustomFieldChoiceSetForm(instance=choice_set)
        initial_choices = form.initial['extra_choices']

        # colons are re-escaped
        self.assertEqual(initial_choices, 'foo\\:bar:label\nvalue:label\\:with\\:colons')

        form = CustomFieldChoiceSetForm(
            {'name': choice_set.name, 'extra_choices': initial_choices},
            instance=choice_set
        )
        self.assertTrue(form.is_valid())
        updated = form.save()

        # cleaned extra choices are correct, which does actually mean a list of tuples
        self.assertEqual(updated.extra_choices, [('foo:bar', 'label'), ('value', 'label:with:colons')])

    def test_choice_colors_round_trip_on_edit(self):
        choice_set = CustomFieldChoiceSet.objects.create(
            name='Test Choice Set',
            extra_choices=[['foo:bar', 'label'], ['choice2', 'Choice 2']],
            choice_colors={'foo:bar': 'red', 'choice2': 'green'},
        )

        form = CustomFieldChoiceSetForm(instance=choice_set)
        initial_choices = form.initial['extra_choices']
        initial_choice_colors = form.initial['choice_colors']

        self.assertEqual(initial_choice_colors, 'choice2:green\nfoo\\:bar:red')

        form = CustomFieldChoiceSetForm(
            {
                'name': choice_set.name,
                'extra_choices': initial_choices,
                'choice_colors': initial_choice_colors,
            },
            instance=choice_set,
        )
        self.assertTrue(form.is_valid())
        updated = form.save()

        self.assertEqual(updated.choice_colors, {'choice2': 'green', 'foo:bar': 'red'})


class SavedFilterFormTestCase(TestCase):

    def test_basic_submit(self):
        """
        Test form submission and validation
        """
        form = SavedFilterForm({
            'name': 'test-sf',
            'slug': 'test-sf',
            'object_types': [ObjectType.objects.get_for_model(Site).pk],
            'weight': 100,
            'parameters': {
                "status": [
                    "active"
                ]
            }
        })
        self.assertTrue(form.is_valid())
        form.save()


class ScriptFileFormTestCase(TestCase):
    """
    Scripts added via a Data Source must be validated the same way uploaded scripts are (see #22180).
    """
    BROKEN_SCRIPT = (
        "from extras.scripts import Script\n"
        "import imnotarealmoduleicreateerrors\n\n\n"
        "class BrokenScript(Script):\n"
        "    def run(self, data, commit):\n"
        "        pass\n"
    )
    VALID_SCRIPT = (
        "from extras.scripts import Script\n\n\n"
        "class FirstScript(Script):\n"
        "    def run(self, data, commit):\n"
        "        pass\n\n\n"
        "class SecondScript(Script):\n"
        "    def run(self, data, commit):\n"
        "        pass\n"
    )

    @staticmethod
    def _write(scripts_dir, filename, content):
        with open(scripts_dir / filename, 'w') as f:
            f.write(content)

    @staticmethod
    def _new_module():
        # Mirror ScriptModuleCreateView.alter_object(), which sets file_root before validation.
        return ScriptModule(file_root=ManagedFileRootPathChoices.SCRIPTS)

    def _sync_source(self, name, **files):
        """
        Create a local DataSource over a temp dir populated with the given {filename: content} files,
        sync it, and return the DataSource.
        """
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        scripts_dir = Path(temp_dir.name) / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        for filename, content in files.items():
            self._write(scripts_dir, filename, content)

        data_source = DataSource(name=name, type="local", source_url=str(scripts_dir))
        data_source.save()
        data_source.sync()
        return data_source

    def test_broken_script_via_data_file_is_rejected(self):
        """A script that fails to import via a data_file must be rejected, and no ScriptModule created."""
        data_source = self._sync_source("Broken", **{'broken.py': self.BROKEN_SCRIPT})
        data_file = data_source.datafiles.get(path__endswith='broken.py')

        form = ScriptFileForm(data={'data_file': data_file.pk}, instance=self._new_module())

        self.assertFalse(form.is_valid())
        self.assertIn(NON_FIELD_ERRORS, form.errors)
        self.assertEqual(ScriptModule.objects.count(), 0)

    def test_valid_script_via_data_file_is_accepted(self):
        """A valid script via a data_file passes validation and its Script classes are discovered on save."""
        data_source = self._sync_source("Valid", **{'valid.py': self.VALID_SCRIPT})
        data_file = data_source.datafiles.get(path__endswith='valid.py')

        form = ScriptFileForm(data={'data_file': data_file.pk}, instance=self._new_module())
        self.assertTrue(form.is_valid())
        module = form.save()

        self.assertEqual(ScriptModule.objects.count(), 1)
        self.assertEqual(
            {script.name for script in module.scripts.all()},
            {'FirstScript', 'SecondScript'},
        )

    def test_corrected_script_recovers(self):
        """After a broken script is rejected, syncing a corrected version succeeds without a uniqueness deadlock."""
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        scripts_dir = Path(temp_dir.name) / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)

        data_source = DataSource(name="Recovery", type="local", source_url=str(scripts_dir))
        data_source.save()

        # First sync: broken script is rejected, nothing created
        self._write(scripts_dir, 'myscript.py', self.BROKEN_SCRIPT)
        data_source.sync()
        data_file = data_source.datafiles.get(path__endswith='myscript.py')
        form = ScriptFileForm(data={'data_file': data_file.pk}, instance=self._new_module())
        self.assertFalse(form.is_valid())
        self.assertEqual(ScriptModule.objects.count(), 0)

        # Correct the script and re-sync: now it should be accepted
        self._write(scripts_dir, 'myscript.py', self.VALID_SCRIPT)
        data_source.sync()
        data_file = data_source.datafiles.get(path__endswith='myscript.py')
        form = ScriptFileForm(data={'data_file': data_file.pk}, instance=self._new_module())
        self.assertTrue(form.is_valid())
        module = form.save()
        self.assertEqual(
            {script.name for script in module.scripts.all()},
            {'FirstScript', 'SecondScript'},
        )

    def test_broken_script_via_upload_is_rejected(self):
        """Regression guard: the upload_file path still validates content."""
        upload_file = SimpleUploadedFile(name='broken.py', content=self.BROKEN_SCRIPT.encode())
        form = ScriptFileForm(files={'upload_file': upload_file}, instance=self._new_module())

        self.assertFalse(form.is_valid())
        self.assertIn(NON_FIELD_ERRORS, form.errors)

    def test_valid_script_via_upload_is_accepted(self):
        """Regression guard: a valid uploaded script still validates."""
        upload_file = SimpleUploadedFile(name='valid.py', content=self.VALID_SCRIPT.encode())
        form = ScriptFileForm(files={'upload_file': upload_file}, instance=self._new_module())

        self.assertTrue(form.is_valid())
