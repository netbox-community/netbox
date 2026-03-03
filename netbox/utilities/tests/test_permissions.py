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
        self.original_actions = dict(registry['model_actions'])

    def tearDown(self):
        registry['model_actions'].clear()
        registry['model_actions'].update(self.original_actions)

    def test_register_model_action_objects(self):
        register_model_actions(Site, [
            ModelAction('test_action', help_text='Test help'),
        ])
        actions = registry['model_actions']['dcim.site']
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0].name, 'test_action')
        self.assertEqual(actions[0].help_text, 'Test help')

    def test_register_string_actions(self):
        register_model_actions(Site, ['action1', 'action2'])
        actions = registry['model_actions']['dcim.site']
        self.assertEqual(len(actions), 2)
        self.assertIsInstance(actions[0], ModelAction)
        self.assertEqual(actions[0].name, 'action1')
        self.assertEqual(actions[1].name, 'action2')

    def test_register_mixed_actions(self):
        register_model_actions(Site, [
            ModelAction('with_help', help_text='Has help'),
            'without_help',
        ])
        actions = registry['model_actions']['dcim.site']
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0].help_text, 'Has help')
        self.assertEqual(actions[1].help_text, '')

    def test_multiple_registrations_append(self):
        register_model_actions(Site, [ModelAction('first')])
        register_model_actions(Site, [ModelAction('second')])
        actions = registry['model_actions']['dcim.site']
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0].name, 'first')
        self.assertEqual(actions[1].name, 'second')


class ObjectPermissionFormTest(TestCase):

    def setUp(self):
        self.original_actions = dict(registry['model_actions'])

    def tearDown(self):
        registry['model_actions'].clear()
        registry['model_actions'].update(self.original_actions)

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

        initial = form.fields['registered_actions'].initial
        self.assertIn('dcim.device.render_config', initial)
        self.assertIn('virtualization.virtualmachine.render_config', initial)

        # Should not leak into the additional actions field
        self.assertEqual(form.initial['actions'], [])

        permission.delete()
