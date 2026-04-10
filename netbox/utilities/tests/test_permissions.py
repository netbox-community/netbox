from django.test import TestCase

from core.models import ObjectType
from dcim.models import Device, Site
from netbox.registry import registry
from users.forms.model_forms import ObjectPermissionForm
from users.models import ObjectPermission
from utilities.permissions import ModelAction, register_model_actions
from virtualization.models import VirtualMachine


class ModelActionTest(TestCase):

    def test_hash(self):
        action1 = ModelAction(name='sync')
        action2 = ModelAction(name='sync', help_text='Different help')
        self.assertEqual(hash(action1), hash(action2))

    def test_equality_with_model_action(self):
        action1 = ModelAction(name='sync')
        action2 = ModelAction(name='sync', help_text='Different help')
        action3 = ModelAction(name='merge')
        self.assertEqual(action1, action2)
        self.assertNotEqual(action1, action3)

    def test_equality_with_string(self):
        action = ModelAction(name='sync')
        self.assertEqual(action, 'sync')
        self.assertNotEqual(action, 'merge')

    def test_usable_in_set(self):
        action1 = ModelAction(name='sync')
        action2 = ModelAction(name='sync', help_text='Different')
        action3 = ModelAction(name='merge')
        actions = {action1, action2, action3}
        self.assertEqual(len(actions), 2)


class RegisterModelActionsTest(TestCase):

    def setUp(self):
        self._original_actions = dict(registry['model_actions'])
        registry['model_actions'].clear()

    def tearDown(self):
        registry['model_actions'].clear()
        registry['model_actions'].update(self._original_actions)

    def test_register_model_action_objects(self):
        register_model_actions(Site, [
            ModelAction('test_action', help_text='Test help'),
        ])
        actions = registry['model_actions']['dcim.site']
        self.assertEqual(len(actions), 1)
        action = next(iter(actions))
        self.assertEqual(action.name, 'test_action')
        self.assertEqual(action.help_text, 'Test help')

    def test_register_string_actions(self):
        register_model_actions(Site, ['action1', 'action2'])
        actions = registry['model_actions']['dcim.site']
        self.assertEqual(len(actions), 2)
        action_names = {a.name for a in actions}
        self.assertEqual(action_names, {'action1', 'action2'})
        self.assertTrue(all(isinstance(a, ModelAction) for a in actions))

    def test_register_mixed_actions(self):
        register_model_actions(Site, [
            ModelAction('with_help', help_text='Has help'),
            'without_help',
        ])
        actions = registry['model_actions']['dcim.site']
        self.assertEqual(len(actions), 2)
        actions_by_name = {a.name: a for a in actions}
        self.assertEqual(actions_by_name['with_help'].help_text, 'Has help')
        self.assertEqual(actions_by_name['without_help'].help_text, '')

    def test_multiple_registrations_append(self):
        register_model_actions(Site, [ModelAction('first')])
        register_model_actions(Site, [ModelAction('second')])
        actions = registry['model_actions']['dcim.site']
        self.assertEqual(len(actions), 2)
        action_names = {a.name for a in actions}
        self.assertEqual(action_names, {'first', 'second'})

    def test_duplicate_registration_ignored(self):
        register_model_actions(Site, [ModelAction('sync')])
        register_model_actions(Site, [ModelAction('sync', help_text='Different help')])
        actions = registry['model_actions']['dcim.site']
        self.assertEqual(len(actions), 1)

    def test_reserved_action_rejected(self):
        for action_name in ('view', 'add', 'change', 'delete'):
            with self.assertRaises(ValueError):
                register_model_actions(Site, [ModelAction(action_name)])

    def test_empty_action_name_rejected(self):
        with self.assertRaises(ValueError):
            register_model_actions(Site, [ModelAction('')])

    def test_no_duplicate_action_fields(self):
        register_model_actions(Device, [ModelAction('render_config')])
        register_model_actions(VirtualMachine, [ModelAction('render_config')])

        form = ObjectPermissionForm()
        action_fields = [k for k in form.fields if k.startswith('action_')]
        self.assertEqual(action_fields.count('action_render_config'), 1)


class ObjectPermissionFormTest(TestCase):

    def setUp(self):
        self._original_actions = dict(registry['model_actions'])
        registry['model_actions'].clear()

    def tearDown(self):
        registry['model_actions'].clear()
        registry['model_actions'].update(self._original_actions)

    def test_shared_action_preselection(self):
        register_model_actions(Device, [ModelAction('render_config')])
        register_model_actions(VirtualMachine, [ModelAction('render_config')])

        device_ct = ObjectType.objects.get_for_model(Device)
        vm_ct = ObjectType.objects.get_for_model(VirtualMachine)

        permission = ObjectPermission.objects.create(
            name='Test Permission',
            actions=['view', 'render_config'],
        )
        permission.object_types.set([device_ct, vm_ct])

        form = ObjectPermissionForm(instance=permission)

        self.assertTrue(form.fields['action_render_config'].initial)

        self.assertEqual(form.initial['actions'], [])

        permission.delete()

    def test_clean_accepts_valid_registered_action(self):
        register_model_actions(Device, [ModelAction('render_config')])

        device_ct = ObjectType.objects.get_for_model(Device)
        form = ObjectPermissionForm(data={
            'name': 'test perm',
            'object_types_0': [],
            'object_types_1': [device_ct.pk],
            'action_render_config': True,
            'can_view': True,
            'actions': '',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIn('render_config', form.cleaned_data['actions'])

    def test_get_registered_actions(self):
        register_model_actions(Device, [ModelAction('render_config')])
        register_model_actions(VirtualMachine, [ModelAction('render_config')])

        device_ct = ObjectType.objects.get_for_model(Device)

        permission = ObjectPermission.objects.create(
            name='Test Registered Actions',
            actions=['view', 'render_config'],
        )
        permission.object_types.set([device_ct])

        registered = permission.get_registered_actions()
        self.assertEqual(len(registered), 1)
        action = registered[0]
        self.assertEqual(action['name'], 'render_config')
        self.assertEqual(action['help_text'], '')
        self.assertTrue(action['enabled'])
        self.assertEqual(action['models'], ['device', 'virtual machine'])

        permission.delete()

    def test_form_with_no_registered_actions(self):
        device_ct = ObjectType.objects.get_for_model(Device)
        form = ObjectPermissionForm(data={
            'name': 'test perm',
            'object_types_0': [],
            'object_types_1': [device_ct.pk],
            'can_view': True,
            'actions': '',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIn('view', form.cleaned_data['actions'])
        action_fields = [k for k in form.fields if k.startswith('action_')]
        self.assertEqual(action_fields, [])

    def test_clone_preselects_registered_actions(self):
        register_model_actions(Device, [ModelAction('render_config')])

        form = ObjectPermissionForm(initial={
            'actions': ['view', 'render_config'],
        })
        self.assertTrue(form.fields['action_render_config'].initial)
        self.assertNotIn('render_config', form.initial['actions'])
