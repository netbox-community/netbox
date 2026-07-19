from django.test import TestCase

from core.models import ObjectType
from dcim.models import Site
from users.forms import GroupForm, ObjectPermissionForm, OwnerForm, UserForm
from users.models import Group, ObjectPermission, Owner, User
from utilities.testing import simulate_restrict


class RestrictedUsersFormTest(TestCase):
    """Users-app M2M forms (not NetBoxModelForms) preserve hidden members via the mixin + clean() merge."""

    def test_userform_hidden_group_is_preserved(self):
        """Editing a user with a hidden group keeps it on save (Meta.fields save_m2m path)."""
        visible = Group.objects.create(name='Visible')
        hidden = Group.objects.create(name='Hidden')
        user = User.objects.create(username='user1')
        user.groups.set([visible, hidden])

        form = UserForm(data={'username': 'user1', 'groups': [visible.pk]}, instance=user)
        simulate_restrict(form, 'groups', Group.objects.filter(pk=visible.pk))
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(set(user.groups.all()), {visible, hidden})

    def test_groupform_hidden_user_is_preserved(self):
        """Editing a group with a hidden member keeps it on save (custom .set() path)."""
        visible = User.objects.create(username='visible')
        hidden = User.objects.create(username='hidden')
        group = Group.objects.create(name='Group 1')
        group.users.set([visible, hidden])

        form = GroupForm(data={'name': 'Group 1', 'users': [visible.pk]}, instance=group)
        simulate_restrict(form, 'users', User.objects.filter(pk=visible.pk))
        self.assertTrue(form.is_valid(), form.errors)
        group = form.save()
        self.assertEqual(set(group.users.all()), {visible, hidden})

    def test_objectpermissionform_hidden_user_is_preserved(self):
        """Editing an object permission with a hidden user keeps it on save (custom .set() path)."""
        visible = User.objects.create(username='visible')
        hidden = User.objects.create(username='hidden')
        perm = ObjectPermission.objects.create(name='Perm 1', actions=['view'])
        perm.users.set([visible, hidden])

        form = ObjectPermissionForm(
            data={
                'name': 'Perm 1',
                'object_types_1': [ObjectType.objects.get_for_model(Site).pk],
                'actions': 'view',
                'users': [visible.pk],
            },
            instance=perm,
        )
        simulate_restrict(form, 'users', User.objects.filter(pk=visible.pk))
        self.assertTrue(form.is_valid(), form.errors)
        perm = form.save()
        self.assertEqual(set(perm.users.all()), {visible, hidden})

    def test_ownerform_hidden_user_group_is_preserved(self):
        """Editing an owner with a hidden user group keeps it on save (Meta.fields save_m2m path)."""
        visible = Group.objects.create(name='Visible')
        hidden = Group.objects.create(name='Hidden')
        owner = Owner.objects.create(name='Owner 1')
        owner.user_groups.set([visible, hidden])

        form = OwnerForm(data={'name': 'Owner 1', 'user_groups': [visible.pk]}, instance=owner)
        simulate_restrict(form, 'user_groups', Group.objects.filter(pk=visible.pk))
        self.assertTrue(form.is_valid(), form.errors)
        owner = form.save()
        self.assertEqual(set(owner.user_groups.all()), {visible, hidden})
