import tempfile
from pathlib import Path

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.choices import ManagedFileRootPathChoices
from core.events import OBJECT_CREATED
from core.models import DataSource, ObjectType
from dcim.forms import SiteForm
from dcim.models import Site
from extras.choices import CustomFieldTypeChoices, EventRuleActionChoices
from extras.forms import SavedFilterForm, TableConfigBulkEditForm, TableConfigForm
from extras.forms.bulk_import import EventRuleImportForm
from extras.forms.filtersets import EventRuleFilterForm
from extras.forms.model_forms import CustomFieldChoiceSetForm, EventRuleForm
from extras.forms.scripts import ScriptFileForm
from extras.models import CustomField, CustomFieldChoiceSet, EventRule, NotificationGroup, Script, ScriptModule, Webhook
from netbox.event_rules import EventRuleAction, register_event_rule_action
from netbox.registry import registry
from utilities.forms.widgets import HTMXSelect


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


class TableConfigFormTestCase(TestCase):

    def test_form_without_table_context(self):
        """The form must be constructible without an object type."""
        form = TableConfigForm()
        self.assertEqual(list(form.fields['available_columns'].widget.choices), [])
        self.assertEqual(list(form.fields['columns'].widget.choices), [])

    def test_form_with_invalid_object_type(self):
        """An unknown object type must yield empty column choices."""
        last_pk = ObjectType.objects.order_by('pk').last().pk
        form = TableConfigForm(initial={'object_type': last_pk + 1})
        self.assertEqual(list(form.fields['available_columns'].widget.choices), [])
        self.assertEqual(list(form.fields['columns'].widget.choices), [])

    def test_form_with_unknown_table(self):
        """An unresolvable table name must yield empty column choices."""
        object_type = ObjectType.objects.get_for_model(Site)
        form = TableConfigForm(initial={'object_type': object_type.pk, 'table': 'NoSuchTable'})
        self.assertEqual(list(form.fields['columns'].widget.choices), [])

    def test_form_with_table_context(self):
        """Column choices must be populated from the resolved table."""
        object_type = ObjectType.objects.get_for_model(Site)
        form = TableConfigForm(initial={
            'object_type': object_type.pk,
            'table': 'SiteTable',
            'columns': ['name', 'status'],
        })
        self.assertEqual(
            [name for name, _ in form.fields['columns'].widget.choices],
            ['name', 'status']
        )
        self.assertIn('region', dict(form.fields['available_columns'].widget.choices))

    def test_form_includes_changelog_message(self):
        """The model form must expose the changelog_message meta field."""
        object_type = ObjectType.objects.get_for_model(Site)
        form = TableConfigForm(initial={'object_type': object_type.pk, 'table': 'SiteTable'})
        self.assertIn('changelog_message', form.fields)
        self.assertIn('changelog_message', form.meta_fields)

    def test_bulk_edit_form_includes_changelog_message(self):
        """The bulk edit form must expose the changelog_message meta field."""
        form = TableConfigBulkEditForm()
        self.assertIn('changelog_message', form.fields)
        self.assertIn('changelog_message', form.meta_fields)


class EventRuleFormTestCase(TestCase):
    """
    EventRuleForm's action_choice field is built dynamically from the EventRuleAction registry,
    for both core actions and those registered by a plugin.
    """

    def tearDown(self):
        super().tearDown()
        registry['event_rule_actions'].pop('test.form_no_object_action', None)

    def test_action_type_widget_is_htmx_select(self):
        """
        action_choice refreshes via HTMX when action_type changes. The widget must be set on the
        field itself: Meta.widgets applies only to fields the ModelForm generates from the model,
        and action_type is declared explicitly.
        """
        form = EventRuleForm()
        widget = form.fields['action_type'].widget
        self.assertIsInstance(widget, HTMXSelect)
        self.assertEqual(widget.attrs.get('hx-target'), '#event-rule-action')

    def test_action_choice_field_for_webhook(self):
        webhook = Webhook.objects.create(name='Form Test Webhook', payload_url='http://localhost:9000/')
        form = EventRuleForm(data={'action_type': EventRuleActionChoices.WEBHOOK})
        self.assertIn('action_choice', form.fields)
        self.assertIn(webhook, form.fields['action_choice'].queryset)

    def test_action_choice_field_for_script(self):
        form = EventRuleForm(data={'action_type': EventRuleActionChoices.SCRIPT})
        self.assertIn('action_choice', form.fields)
        self.assertEqual(form.fields['action_choice'].queryset.model, Script)

    def test_action_choice_field_for_notification(self):
        form = EventRuleForm(data={'action_type': EventRuleActionChoices.NOTIFICATION})
        self.assertIn('action_choice', form.fields)
        self.assertEqual(form.fields['action_choice'].queryset.model, NotificationGroup)

    def test_action_choice_field_labels(self):
        """The object picker is labeled for the object being selected, not for the action itself."""
        for action_type, label in (
            (EventRuleActionChoices.WEBHOOK, 'Webhook'),
            (EventRuleActionChoices.SCRIPT, 'Script'),
            (EventRuleActionChoices.NOTIFICATION, 'Notification group'),
        ):
            form = EventRuleForm(data={'action_type': action_type})
            self.assertEqual(form.fields['action_choice'].label, label)

    def test_action_choice_field_honors_object_label(self):
        class LabeledObjectAction(EventRuleAction):
            slug = 'test.form_labeled_object_action'
            label = 'Form Labeled Object Action'
            object_model = Webhook
            object_label = 'Destination'

        register_event_rule_action(LabeledObjectAction)
        self.addCleanup(registry['event_rule_actions'].pop, LabeledObjectAction.slug, None)

        form = EventRuleForm(data={'action_type': LabeledObjectAction.slug})
        self.assertEqual(form.fields['action_choice'].label, 'Destination')

    def test_action_choice_field_omitted_for_registered_no_object_action(self):
        class NoObjectAction(EventRuleAction):
            slug = 'test.form_no_object_action'
            label = 'Form No-Object Action'
            object_required = False

        register_event_rule_action(NoObjectAction)

        form = EventRuleForm(data={'action_type': 'test.form_no_object_action'})
        self.assertNotIn('action_choice', form.fields)

    def test_action_choice_field_falls_back_to_initial_for_unregistered_action(self):
        """
        get_field_value() falls back to the field's own initial (webhook) for an unregistered
        action_type, so init_action_choice() still builds a usable picker.
        """
        form = EventRuleForm(data={'action_type': 'not.a.registered.action'})
        self.assertIn('action_choice', form.fields)
        self.assertEqual(form.fields['action_choice'].queryset.model, Webhook)

    def test_submit_and_save_with_registered_no_object_action(self):
        """A runtime-registered action can be submitted and saved end-to-end through the form."""
        class NoObjectAction(EventRuleAction):
            slug = 'test.form_no_object_action'
            label = 'Form No-Object Action'
            object_required = False

            def enqueue(self, **kwargs):
                pass

        register_event_rule_action(NoObjectAction)

        object_type = ObjectType.objects.get_for_model(Site)
        form = EventRuleForm(data={
            'name': 'Form No-Object Rule',
            'object_types': [object_type.pk],
            'event_types': [OBJECT_CREATED],
            'action_type': 'test.form_no_object_action',
        })
        self.assertTrue(form.is_valid(), form.errors)
        rule = form.save()
        self.assertIsNone(rule.action_object_type)
        self.assertIsNone(rule.action_object_id)

    def test_submit_and_save_webhook_action(self):
        """The generalized form still saves a core Webhook action correctly."""
        webhook = Webhook.objects.create(name='Form Submit Webhook', payload_url='http://localhost:9000/')
        object_type = ObjectType.objects.get_for_model(Site)
        form = EventRuleForm(data={
            'name': 'Form Webhook Rule',
            'object_types': [object_type.pk],
            'event_types': [OBJECT_CREATED],
            'action_type': EventRuleActionChoices.WEBHOOK,
            'action_choice': webhook.pk,
        })
        self.assertTrue(form.is_valid(), form.errors)
        rule = form.save()
        self.assertEqual(rule.action_object, webhook)

    def test_switching_to_optional_object_action_clears_stale_action_object(self):
        """
        Switching an existing rule to an action which declares object_model but not
        object_required, leaving the picker blank, must clear the old action_object.
        """
        class OptionalObjectAction(EventRuleAction):
            slug = 'test.optional_object_action'
            label = 'Optional Object Action'
            object_model = Webhook
            object_required = False

        register_event_rule_action(OptionalObjectAction)
        self.addCleanup(registry['event_rule_actions'].pop, 'test.optional_object_action', None)

        webhook = Webhook.objects.create(name='Stale Webhook', payload_url='http://localhost:9000/')
        webhook_type = ObjectType.objects.get_for_model(Webhook)
        object_type = ObjectType.objects.get_for_model(Site)
        rule = EventRule.objects.create(
            name='Stale Object Rule',
            event_types=[OBJECT_CREATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
        )
        rule.object_types.set([object_type])

        form = EventRuleForm(data={
            'name': rule.name,
            'object_types': [object_type.pk],
            'event_types': [OBJECT_CREATED],
            'action_type': 'test.optional_object_action',
            # action_choice omitted: the user left the picker blank
        }, instance=rule)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        self.assertIsNone(saved.action_object_type)
        self.assertIsNone(saved.action_object_id)


class EventRuleFilterFormTestCase(TestCase):

    def test_action_type_choices_reflect_the_live_registry(self):
        """
        The filter form's action_type choices must be read from the registry on access, not frozen
        when this module was first imported.
        """
        class FilterFormAction(EventRuleAction):
            slug = 'test.filter_form_action'
            label = 'Filter Form Action'

        register_event_rule_action(FilterFormAction)
        self.addCleanup(registry['event_rule_actions'].pop, FilterFormAction.slug, None)

        choices = dict(EventRuleFilterForm().fields['action_type'].choices)
        self.assertEqual(choices.get(FilterFormAction.slug), 'Filter Form Action')
        self.assertIn(None, choices)  # The blank choice is retained


class EventRuleImportFormTestCase(TestCase):
    """
    EventRuleImportForm resolves action_object via each registered action's resolve_import_object()
    hook, and treats it as optional (an action need not operate against a target object).
    """

    def tearDown(self):
        super().tearDown()
        registry['event_rule_actions'].pop('test.import_no_object_action', None)

    def test_resolves_webhook_by_name(self):
        webhook = Webhook.objects.create(name='Import Test Webhook', payload_url='http://localhost:9000/')
        form = EventRuleImportForm(data={
            'name': 'Import Webhook Rule',
            'object_types': 'dcim.site',
            'event_types': 'object_created',
            'action_type': EventRuleActionChoices.WEBHOOK,
            'action_object': webhook.name,
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.instance.action_object, webhook)

    def test_resolves_notification_group_by_name(self):
        """The import form resolves a notification group, not just webhooks and scripts."""
        group = NotificationGroup.objects.create(name='Import Test Group')
        form = EventRuleImportForm(data={
            'name': 'Import Notification Rule',
            'object_types': 'dcim.site',
            'event_types': 'object_created',
            'action_type': EventRuleActionChoices.NOTIFICATION,
            'action_object': group.name,
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.instance.action_object, group)

    def test_unresolvable_webhook_name_is_rejected(self):
        form = EventRuleImportForm(data={
            'name': 'Import Bad Webhook Rule',
            'object_types': 'dcim.site',
            'event_types': 'object_created',
            'action_type': EventRuleActionChoices.WEBHOOK,
            'action_object': 'Does Not Exist',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('action_object', form.errors)

    def test_unregistered_action_type_is_rejected(self):
        form = EventRuleImportForm(data={
            'name': 'Import Bad Type Rule',
            'object_types': 'dcim.site',
            'event_types': 'object_created',
            'action_type': 'not.a.registered.action',
            'action_object': 'whatever',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('action_type', form.errors)

    def test_submit_no_object_action_with_blank_action_object_succeeds(self):
        """A blank action_object must be accepted for bulk-importing a no-object action."""
        class NoObjectAction(EventRuleAction):
            slug = 'test.import_no_object_action'
            label = 'Import No-Object Action'
            object_required = False

        register_event_rule_action(NoObjectAction)

        form = EventRuleImportForm(data={
            'name': 'Import No-Object Rule',
            'object_types': 'dcim.site',
            'event_types': 'object_created',
            'action_type': 'test.import_no_object_action',
            'action_object': '',
        })
        self.assertTrue(form.is_valid(), form.errors)
        rule = form.save()
        self.assertIsNone(rule.action_object_type)
        self.assertIsNone(rule.action_object_id)

    def test_blank_action_object_rejected_for_object_required_action(self):
        """A blank action_object must be rejected cleanly (not raise) for an action which requires one."""
        form = EventRuleImportForm(data={
            'name': 'Import Webhook No Object',
            'object_types': 'dcim.site',
            'event_types': 'object_created',
            'action_type': EventRuleActionChoices.WEBHOOK,
            'action_object': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('action_object', form.errors)

    def test_action_object_rejected_for_action_without_object_model(self):
        """
        An action declaring no object_model rejects a supplied action_object as inapplicable,
        rather than reporting it as an unsupported bulk import.
        """
        class NoObjectAction(EventRuleAction):
            slug = 'test.import_no_object_action'
            label = 'Import No-Object Action'
            object_required = False

        register_event_rule_action(NoObjectAction)

        form = EventRuleImportForm(data={
            'name': 'Import No-Object Rule With Object',
            'object_types': 'dcim.site',
            'event_types': 'object_created',
            'action_type': 'test.import_no_object_action',
            'action_object': 'Some Object',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('does not operate against a target object', str(form.errors['action_object']))

    def test_csv_update_to_optional_object_action_clears_stale_action_object(self):
        """
        A CSV row updating an existing rule to an action_type which declares object_model but not
        object_required, with action_object left blank, must clear the previous action_object.
        """
        class OptionalObjectAction(EventRuleAction):
            slug = 'test.import_optional_object_action'
            label = 'Import Optional Object Action'
            object_model = Webhook
            object_required = False

        register_event_rule_action(OptionalObjectAction)
        self.addCleanup(registry['event_rule_actions'].pop, 'test.import_optional_object_action', None)

        webhook = Webhook.objects.create(name='CSV Stale Webhook', payload_url='http://localhost:9000/')
        webhook_type = ObjectType.objects.get_for_model(Webhook)
        rule = EventRule.objects.create(
            name='CSV Stale Object Rule',
            event_types=[OBJECT_CREATED],
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object_type=webhook_type,
            action_object_id=webhook.pk,
        )

        form = EventRuleImportForm(data={
            'name': rule.name,
            'object_types': 'dcim.site',
            'event_types': 'object_created',
            'action_type': 'test.import_optional_object_action',
            'action_object': '',
        }, instance=rule)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        self.assertIsNone(saved.action_object_type)
        self.assertIsNone(saved.action_object_id)

    def test_action_validate_error_on_unexposed_field_becomes_non_field_error(self):
        """A validate() error keyed by a field this form doesn't expose (e.g. action_data) must not raise."""
        class ActionDataValidatingAction(EventRuleAction):
            slug = 'test.import_action_data_validating'
            label = 'Import Action Data Validating'
            object_required = False

            def validate(self, *, action_object, action_data):
                raise ValidationError({'action_data': 'Bad action_data for test'})

        register_event_rule_action(ActionDataValidatingAction)
        self.addCleanup(registry['event_rule_actions'].pop, 'test.import_action_data_validating', None)

        form = EventRuleImportForm(data={
            'name': 'Import Bad Action Data Rule',
            'object_types': 'dcim.site',
            'event_types': 'object_created',
            'action_type': 'test.import_action_data_validating',
            'action_object': '',
        })
        self.assertFalse(form.is_valid())
        self.assertIn(NON_FIELD_ERRORS, form.errors)
        self.assertIn('Bad action_data for test', form.errors[NON_FIELD_ERRORS])
