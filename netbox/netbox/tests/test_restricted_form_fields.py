from django.test import TestCase as DjangoTestCase
from django.urls import reverse

from circuits.forms import CircuitGroupAssignmentForm, CircuitTerminationForm
from circuits.models import (
    Circuit,
    CircuitGroup,
    CircuitGroupAssignment,
    CircuitTermination,
    CircuitType,
    Provider,
    ProviderNetwork,
    VirtualCircuit,
)
from core.models import ObjectType
from dcim.forms import MACAddressForm
from dcim.models import Device, DeviceRole, DeviceType, Interface, MACAddress, Manufacturer, Site
from extras.choices import CustomFieldTypeChoices, CustomFieldUIEditableChoices, EventRuleActionChoices
from extras.forms import EventRuleForm
from extras.models import CustomField, EventRule, NotificationGroup, Tag, Webhook
from ipam.forms import IPAddressForm, ServiceForm, VLANGroupForm
from ipam.models import IPAddress, Service, VLANGroup
from netbox.forms import NetBoxModelForm
from netbox.forms.model_forms import RestrictedChoiceLabel
from tenancy.models import Tenant
from users.models import ObjectPermission, User
from utilities.forms.utils import restrict_form_fields
from utilities.testing import TestCase, create_test_device, create_test_virtualmachine
from virtualization.models import VirtualMachine, VMInterface
from vpn.choices import TunnelTerminationTypeChoices
from vpn.forms import L2VPNTerminationForm, TunnelTerminationForm
from vpn.models import L2VPN, L2VPNTermination, Tunnel, TunnelTermination


def simulate_restrict(form, field_name, restricted_queryset, original_queryset=None):
    """
    Stand in for restrict_form_fields(): record the original queryset, swap in the restricted one, then prepare the
    read-only display. `original_queryset` defaults to the field's current (pre-restriction) queryset.
    """
    if original_queryset is None:
        original_queryset = form.fields[field_name].queryset
    form.fields[field_name].queryset = restricted_queryset
    form.prepare_restricted_queryset_fields({field_name: original_queryset})


class SiteTagsForm(NetBoxModelForm):
    class Meta:
        model = Site
        fields = ('name', 'slug', 'status', 'tags')


class SiteTenantForm(NetBoxModelForm):
    class Meta:
        model = Site
        fields = ('name', 'slug', 'status', 'tenant')


class SiteBaseForm(NetBoxModelForm):
    class Meta:
        model = Site
        fields = ('name', 'slug', 'status')


class RestrictedScalarFieldTest(DjangoTestCase):

    def setUp(self):
        self.visible_tenant = Tenant.objects.create(name='Visible Tenant', slug='visible-tenant')
        self.hidden_tenant = Tenant.objects.create(name='Hidden Tenant', slug='hidden-tenant')

    def test_restricted_value_is_shown_disabled_and_preserved(self):
        """A scalar value removed by permissions is shown read-only and preserved on save."""
        site = Site.objects.create(name='Site 1', slug='site-1', tenant=self.hidden_tenant)

        form = SiteTenantForm(
            data={'name': site.name, 'slug': site.slug, 'status': 'active'},
            instance=site
        )
        simulate_restrict(form, 'tenant', Tenant.objects.filter(pk=self.visible_tenant.pk))

        self.assertTrue(form.fields['tenant'].disabled)
        self.assertEqual(form['tenant'].value(), self.hidden_tenant.pk)
        self.assertIn(self.hidden_tenant.pk, set(form.fields['tenant'].queryset.values_list('pk', flat=True)))

        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(site.tenant, self.hidden_tenant)

    def test_replacement_is_ignored(self):
        """A submitted replacement for a disabled scalar field is ignored."""
        site = Site.objects.create(name='Site 1', slug='site-1', tenant=self.hidden_tenant)

        form = SiteTenantForm(
            data={'name': site.name, 'slug': site.slug, 'status': 'active', 'tenant': self.visible_tenant.pk},
            instance=site
        )
        simulate_restrict(form, 'tenant', Tenant.objects.filter(pk=self.visible_tenant.pk))

        self.assertTrue(form.fields['tenant'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(site.tenant, self.hidden_tenant)

    def test_visible_value_is_not_locked(self):
        """A visible scalar value remains editable (the field is not disabled)."""
        site = Site.objects.create(name='Site 1', slug='site-1', tenant=self.visible_tenant)

        form = SiteTenantForm(
            data={'name': site.name, 'slug': site.slug, 'status': 'active', 'tenant': self.visible_tenant.pk},
            instance=site
        )
        simulate_restrict(form, 'tenant', Tenant.objects.filter(pk=self.visible_tenant.pk))

        self.assertFalse(form.fields['tenant'].disabled)
        self.assertTrue(form.is_valid(), form.errors)

    def test_business_excluded_value_is_not_locked(self):
        """A value absent from the original queryset for non-permission reasons is not locked."""
        site = Site.objects.create(name='Site 1', slug='site-1', tenant=self.hidden_tenant)

        form = SiteTenantForm(
            data={'name': site.name, 'slug': site.slug, 'status': 'active', 'tenant': self.visible_tenant.pk},
            instance=site
        )
        # The original queryset already excludes the current tenant (business filter); nothing further is removed.
        business_queryset = Tenant.objects.filter(pk=self.visible_tenant.pk)
        simulate_restrict(form, 'tenant', business_queryset, original_queryset=business_queryset)

        self.assertFalse(form.fields['tenant'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(site.tenant, self.visible_tenant)

    def test_locked_field_keeps_existing_help_text(self):
        """Locking a field appends to, rather than replaces, any existing help text."""
        site = Site.objects.create(name='Site 1', slug='site-1', tenant=self.hidden_tenant)

        form = SiteTenantForm(
            data={'name': site.name, 'slug': site.slug, 'status': 'active'},
            instance=site
        )
        form.fields['tenant'].help_text = 'Existing help.'
        simulate_restrict(form, 'tenant', Tenant.objects.filter(pk=self.visible_tenant.pk))

        help_text = str(form.fields['tenant'].help_text)
        self.assertIn('Existing help.', help_text)
        self.assertIn('restricted value', help_text)

    def test_unrestricted_user_does_not_lock_fields(self):
        """When restrict() leaves every field unchanged (e.g. a superuser), preparation is skipped entirely."""
        user = User.objects.create_user(username='superuser', is_superuser=True)
        site = Site.objects.create(name='Site 1', slug='site-1', tenant=self.hidden_tenant)

        form = SiteTenantForm(instance=site)
        restrict_form_fields(form, user)

        self.assertFalse(form.fields['tenant'].disabled)
        self.assertFalse(getattr(form, '_restricted_queryset_fields_prepared', False))

    def test_preparation_is_idempotent(self):
        """Running the preparation twice does not duplicate help text or re-wrap labels."""
        site = Site.objects.create(name='Site 1', slug='site-1', tenant=self.hidden_tenant)

        form = SiteTenantForm(
            data={'name': site.name, 'slug': site.slug, 'status': 'active'},
            instance=site
        )
        simulate_restrict(form, 'tenant', Tenant.objects.filter(pk=self.visible_tenant.pk))
        help_text = str(form.fields['tenant'].help_text)

        form.prepare_restricted_queryset_fields({'tenant': Tenant.objects.all()})
        self.assertEqual(str(form.fields['tenant'].help_text), help_text)


class RestrictedMultiValueFieldTest(DjangoTestCase):

    def setUp(self):
        self.visible_tag = Tag.objects.create(name='Visible Tag', slug='visible-tag')
        self.hidden_tag = Tag.objects.create(name='Hidden Tag', slug='hidden-tag')
        self.other_hidden_tag = Tag.objects.create(name='Other Hidden Tag', slug='other-hidden-tag')

    def test_restricted_member_is_read_only_but_field_stays_editable(self):
        """A restricted current tag is preserved while the field stays editable; removing the visible tag works."""
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set([self.visible_tag, self.hidden_tag])

        form = SiteTagsForm(
            # The user removes the visible tag. The restricted tag's option is disabled and not submitted.
            data={'name': site.name, 'slug': site.slug, 'status': 'active', 'tags': []},
            instance=site
        )
        simulate_restrict(form, 'tags', Tag.objects.filter(pk=self.visible_tag.pk))

        self.assertFalse(form.fields['tags'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(set(site.tags.values_list('pk', flat=True)), {self.hidden_tag.pk})

    def test_visible_tag_can_be_added_while_restricted_member_preserved(self):
        """A visible tag can be added while the restricted current tag is preserved."""
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set([self.hidden_tag])

        form = SiteTagsForm(
            data={'name': site.name, 'slug': site.slug, 'status': 'active', 'tags': [self.visible_tag.pk]},
            instance=site
        )
        simulate_restrict(form, 'tags', Tag.objects.filter(pk=self.visible_tag.pk))

        self.assertFalse(form.fields['tags'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(
            set(site.tags.values_list('pk', flat=True)),
            {self.hidden_tag.pk, self.visible_tag.pk}
        )

    def test_restricted_member_preserved_on_prefixed_form(self):
        """Preservation works for a prefixed form: hidden members are merged in clean(), not into submitted data."""
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set([self.visible_tag, self.hidden_tag])

        form = SiteTagsForm(
            data={
                'quickadd-name': site.name,
                'quickadd-slug': site.slug,
                'quickadd-status': 'active',
                'quickadd-tags': [],
            },
            instance=site,
            prefix='quickadd'
        )
        simulate_restrict(form, 'tags', Tag.objects.filter(pk=self.visible_tag.pk))

        self.assertFalse(form.fields['tags'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(set(site.tags.values_list('pk', flat=True)), {self.hidden_tag.pk})

    def test_forged_non_current_restricted_value_is_rejected(self):
        """A restricted tag not already assigned cannot be added."""
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set([self.hidden_tag])

        form = SiteTagsForm(
            data={'name': site.name, 'slug': site.slug, 'status': 'active', 'tags': [self.other_hidden_tag.pk]},
            instance=site
        )
        simulate_restrict(form, 'tags', Tag.objects.filter(pk=self.visible_tag.pk))

        self.assertFalse(form.fields['tags'].disabled)
        self.assertFalse(form.is_valid())

    def test_restricted_choice_label(self):
        """RestrictedChoiceLabel is disabled and stringifies to its wrapped label."""
        label = RestrictedChoiceLabel('Tag 1')
        self.assertTrue(label.disabled)
        self.assertEqual(str(label), 'Tag 1')

    def test_restricted_member_renders_as_disabled_option(self):
        """The restricted member renders as a disabled <option> while the field itself is not disabled."""
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set([self.visible_tag, self.hidden_tag])

        form = SiteTagsForm(instance=site)
        simulate_restrict(form, 'tags', Tag.objects.filter(pk=self.visible_tag.pk))

        rendered = str(form['tags'])
        # The <select> itself is not disabled; only the restricted option carries disabled="disabled".
        self.assertFalse(form.fields['tags'].disabled)
        self.assertIn(f'value="{self.hidden_tag.pk}"', rendered)
        self.assertIn('disabled="disabled"', rendered)

    def test_visible_field_remains_editable(self):
        """A fully visible tags field stays editable and can be cleared."""
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set([self.visible_tag])

        form = SiteTagsForm(
            data={'name': site.name, 'slug': site.slug, 'status': 'active', 'tags': []},
            instance=site
        )
        simulate_restrict(form, 'tags', Tag.objects.filter(pk=self.visible_tag.pk))

        self.assertFalse(form.fields['tags'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(site.tags.count(), 0)

    def test_editable_field_rejects_forged_value(self):
        """An editable field (no hidden current value) still validates submitted values against the restricted qs."""
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set([self.visible_tag])

        form = SiteTagsForm(
            data={
                'name': site.name,
                'slug': site.slug,
                'status': 'active',
                'tags': [self.visible_tag.pk, self.other_hidden_tag.pk],
            },
            instance=site
        )
        simulate_restrict(form, 'tags', Tag.objects.filter(pk=self.visible_tag.pk))

        self.assertFalse(form.fields['tags'].disabled)
        self.assertFalse(form.is_valid())


class RestrictedCustomFieldTest(DjangoTestCase):

    def setUp(self):
        site_type = ObjectType.objects.get_for_model(Site)
        tenant_type = ObjectType.objects.get_for_model(Tenant)

        self.cf_object = CustomField.objects.create(
            name='primary_vendor',
            type=CustomFieldTypeChoices.TYPE_OBJECT,
            related_object_type=tenant_type
        )
        self.cf_object.object_types.set([site_type])

        self.cf_multiobject = CustomField.objects.create(
            name='vendors',
            type=CustomFieldTypeChoices.TYPE_MULTIOBJECT,
            related_object_type=tenant_type
        )
        self.cf_multiobject.object_types.set([site_type])

        self.visible_tenant = Tenant.objects.create(name='Visible Tenant', slug='visible-tenant')
        self.hidden_tenant = Tenant.objects.create(name='Hidden Tenant', slug='hidden-tenant')

    def test_editable_multiobject_restricted_member_is_preserved(self):
        """An editable multi-object custom field stays editable; the restricted member is preserved."""
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.custom_field_data['vendors'] = [self.hidden_tenant.pk, self.visible_tenant.pk]
        site.save()

        form = SiteBaseForm(
            # The user removes the visible tenant; the restricted tenant's option is disabled and not submitted.
            data={'name': site.name, 'slug': site.slug, 'status': 'active', 'cf_vendors': []},
            instance=site
        )
        simulate_restrict(form, 'cf_vendors', Tenant.objects.filter(pk=self.visible_tenant.pk))

        self.assertFalse(form.fields['cf_vendors'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(set(site.custom_field_data['vendors']), {self.hidden_tenant.pk})

    def test_two_restricted_multi_value_fields_are_both_preserved(self):
        """Two restricted multi-value fields on one bound form both preserve their restricted members."""
        visible_tag = Tag.objects.create(name='Visible Tag', slug='visible-tag-multi')
        hidden_tag = Tag.objects.create(name='Hidden Tag', slug='hidden-tag-multi')
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.tags.set([visible_tag, hidden_tag])
        site.custom_field_data['vendors'] = [self.hidden_tenant.pk, self.visible_tenant.pk]
        site.save()

        form = SiteBaseForm(
            data={'name': site.name, 'slug': site.slug, 'status': 'active', 'tags': [], 'cf_vendors': []},
            instance=site
        )
        form.fields['tags'].queryset = Tag.objects.filter(pk=visible_tag.pk)
        form.fields['cf_vendors'].queryset = Tenant.objects.filter(pk=self.visible_tenant.pk)
        form.prepare_restricted_queryset_fields({
            'tags': Tag.objects.all(),
            'cf_vendors': Tenant.objects.all(),
        })

        self.assertFalse(form.fields['tags'].disabled)
        self.assertFalse(form.fields['cf_vendors'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(set(site.tags.values_list('pk', flat=True)), {hidden_tag.pk})
        self.assertEqual(set(site.custom_field_data['vendors']), {self.hidden_tenant.pk})

    def test_hidden_object_value_is_shown_disabled_and_preserved(self):
        """An object custom field with a hidden value is disabled and preserved."""
        site = Site.objects.create(name='Site 1', slug='site-1')
        site.custom_field_data['primary_vendor'] = self.hidden_tenant.pk
        site.save()

        form = SiteBaseForm(
            data={'name': site.name, 'slug': site.slug, 'status': 'active'},
            instance=site
        )
        simulate_restrict(form, 'cf_primary_vendor', Tenant.objects.filter(pk=self.visible_tenant.pk))

        self.assertTrue(form.fields['cf_primary_vendor'].disabled)
        self.assertEqual(form['cf_primary_vendor'].value(), self.hidden_tenant.pk)
        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(site.custom_field_data['primary_vendor'], self.hidden_tenant.pk)

    def test_readonly_multiobject_hidden_value_is_preserved(self):
        """A read-only (ui_editable='no') multi-object custom field with a hidden member is preserved."""
        cf = CustomField.objects.create(
            name='readonly_vendors',
            type=CustomFieldTypeChoices.TYPE_MULTIOBJECT,
            related_object_type=ObjectType.objects.get_for_model(Tenant),
            ui_editable=CustomFieldUIEditableChoices.NO
        )
        cf.object_types.set([ObjectType.objects.get_for_model(Site)])

        site = Site.objects.create(name='Site 1', slug='site-1')
        site.custom_field_data['readonly_vendors'] = [self.hidden_tenant.pk, self.visible_tenant.pk]
        site.save()

        form = SiteBaseForm(
            data={'name': site.name, 'slug': site.slug, 'status': 'active'},
            instance=site
        )
        self.assertTrue(form.fields['cf_readonly_vendors'].disabled)
        simulate_restrict(form, 'cf_readonly_vendors', Tenant.objects.filter(pk=self.visible_tenant.pk))

        self.assertTrue(form.is_valid(), form.errors)
        site = form.save()
        self.assertEqual(
            set(site.custom_field_data['readonly_vendors']),
            {self.hidden_tenant.pk, self.visible_tenant.pk}
        )


class RestrictedSyntheticSelectorTest(DjangoTestCase):

    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model='Model 1', slug='model-1')
        role = DeviceRole.objects.create(name='Role 1', slug='role-1')
        site = Site.objects.create(name='Site 1', slug='site-1')
        cls.device = Device.objects.create(name='Device 1', device_type=device_type, role=role, site=site)
        cls.interface = Interface.objects.create(device=cls.device, name='eth0', type='1000base-t')

    def test_ipaddress_selector_resolves_current_assignment(self):
        """The declared selectors resolve the assigned interface only for the matching field."""
        ip = IPAddress(address='192.0.2.1/24')
        ip.assigned_object = self.interface
        ip.save()
        ip = IPAddress.objects.get(pk=ip.pk)

        form = IPAddressForm(instance=ip)
        original = Interface.objects.all()
        self.assertEqual(form._get_restricted_queryset_field_current_objects('interface', original), [self.interface])
        self.assertEqual(form._get_restricted_queryset_field_current_objects('vminterface', original), [])
        self.assertEqual(form._get_restricted_queryset_field_current_objects('fhrpgroup', original), [])

    def test_macaddress_selector_resolves_current_assignment(self):
        """The declared selectors resolve the assigned interface only for the matching field."""
        mac = MACAddress(mac_address='00:11:22:33:44:55')
        mac.assigned_object = self.interface
        mac.save()

        form = MACAddressForm(instance=mac)
        original = Interface.objects.all()
        self.assertEqual(form._get_restricted_queryset_field_current_objects('interface', original), [self.interface])
        self.assertEqual(form._get_restricted_queryset_field_current_objects('vminterface', original), [])

        # An unassigned object resolves no current value for any selector.
        unassigned = MACAddress.objects.create(mac_address='00:11:22:33:44:66')
        form = MACAddressForm(instance=unassigned)
        self.assertEqual(form._get_restricted_queryset_field_current_objects('interface', original), [])

    def test_l2vpntermination_selector_resolves_current_assignment(self):
        """The declared selectors resolve the assigned interface only for the matching field."""
        l2vpn = L2VPN.objects.create(name='L2VPN 1', slug='l2vpn-1', type='vxlan')
        termination = L2VPNTermination(l2vpn=l2vpn)
        termination.assigned_object = self.interface
        termination.save()

        form = L2VPNTerminationForm(instance=termination)
        original = Interface.objects.all()
        self.assertEqual(form._get_restricted_queryset_field_current_objects('interface', original), [self.interface])
        self.assertEqual(form._get_restricted_queryset_field_current_objects('vminterface', original), [])
        self.assertEqual(form._get_restricted_queryset_field_current_objects('vlan', original), [])

    def test_ipaddress_cross_selector_submission_cannot_replace_hidden_assignment(self):
        """A value submitted for a sibling selector cannot silently replace a hidden assignment."""
        ip = IPAddress(address='192.0.2.1/24')
        ip.assigned_object = self.interface
        ip.save()
        ip = IPAddress.objects.get(pk=ip.pk)
        vm = create_test_virtualmachine('VM 1')
        vminterface = VMInterface.objects.create(virtual_machine=vm, name='eth0')

        form = IPAddressForm(
            data={'address': '192.0.2.1/24', 'status': 'active', 'vminterface': vminterface.pk},
            instance=ip,
        )
        simulate_restrict(form, 'interface', Interface.objects.none())

        # The locked hidden interface plus the submitted sibling trip the single-assignment validation.
        self.assertFalse(form.is_valid())
        self.assertIn('vminterface', form.errors)
        self.assertEqual(IPAddress.objects.get(pk=ip.pk).assigned_object, self.interface)

    def test_tunneltermination_parent_resolves_through_termination(self):
        """The auxiliary parent selector resolves the termination's owner via its dotted path."""
        tunnel = Tunnel.objects.create(name='Tunnel 1', encapsulation='gre', status='active')
        termination = TunnelTermination.objects.create(tunnel=tunnel, role='peer', termination=self.interface)

        form = TunnelTerminationForm(instance=termination)
        self.assertEqual(
            form._get_restricted_queryset_field_current_objects('parent', Device.objects.all()),
            [self.device],
        )

    def test_hidden_assigned_object_is_shown_disabled_and_preserved(self):
        """Editing a MAC address whose assigned interface is hidden shows it disabled and preserves it."""
        mac = MACAddress(mac_address='00:11:22:33:44:55')
        mac.assigned_object = self.interface
        mac.save()

        form = MACAddressForm(data={'mac_address': '00:11:22:33:44:55'}, instance=mac)
        simulate_restrict(form, 'interface', Interface.objects.none())

        self.assertTrue(form.fields['interface'].disabled)
        self.assertEqual(form['interface'].value(), self.interface.pk)
        self.assertTrue(form.is_valid(), form.errors)
        mac = form.save()
        self.assertEqual(mac.assigned_object, self.interface)


class RestrictedEditViewTest(TestCase):

    def setUp(self):
        super().setUp()
        self.visible_tag = Tag.objects.create(name='VisibleTagAlpha', slug='visible-tag-alpha')
        self.hidden_tag = Tag.objects.create(name='HiddenTagBravo', slug='hidden-tag-bravo')
        self.site = Site.objects.create(name='Site 1', slug='site-1', status='active')
        self.site.tags.set([self.visible_tag, self.hidden_tag])

    def _grant(self):
        # Allow editing the site, but only viewing the single visible tag (all tenants remain hidden).
        self.add_permissions('dcim.view_site', 'dcim.change_site')
        obj_perm = ObjectPermission(
            name='View visible tag only',
            constraints={'pk': self.visible_tag.pk},
            actions=['view'],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(Tag))

    def _edit_url(self):
        return reverse('dcim:site_edit', kwargs={'pk': self.site.pk})

    def test_edit_preserves_restricted_tag(self):
        """Keeping the visible tag preserves the restricted tag too."""
        self._grant()
        data = {'name': self.site.name, 'slug': self.site.slug, 'status': 'active', 'tags': [self.visible_tag.pk]}
        response = self.client.post(self._edit_url(), data)

        self.assertEqual(response.status_code, 302)
        self.site.refresh_from_db()
        self.assertEqual(
            set(self.site.tags.values_list('pk', flat=True)),
            {self.visible_tag.pk, self.hidden_tag.pk}
        )

    def test_edit_can_remove_visible_tag_while_restricted_preserved(self):
        """Removing the visible tag drops only it; the restricted tag is preserved."""
        self._grant()
        data = {'name': self.site.name, 'slug': self.site.slug, 'status': 'active', 'tags': []}
        response = self.client.post(self._edit_url(), data)

        self.assertEqual(response.status_code, 302)
        self.site.refresh_from_db()
        self.assertEqual(set(self.site.tags.values_list('pk', flat=True)), {self.hidden_tag.pk})

    def test_edit_preserves_hidden_tenant(self):
        """A scalar value the user cannot view is preserved across an edit."""
        tenant = Tenant.objects.create(name='SecretTenantDelta', slug='secret-tenant-delta')
        self.site.tenant = tenant
        self.site.save()
        self._grant()

        data = {'name': self.site.name, 'slug': self.site.slug, 'status': 'active', 'tags': [self.visible_tag.pk]}
        response = self.client.post(self._edit_url(), data)

        self.assertEqual(response.status_code, 302)
        self.site.refresh_from_db()
        self.assertEqual(self.site.tenant, tenant)

    def test_get_shows_restricted_values_disabled(self):
        """The edit form renders the restricted current values read-only with explanatory help text."""
        tenant = Tenant.objects.create(name='SecretTenantDelta', slug='secret-tenant-delta')
        self.site.tenant = tenant
        self.site.save()
        self._grant()

        response = self.client.get(self._edit_url())
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # The current restricted values are now shown read-only.
        self.assertIn('HiddenTagBravo', content)
        self.assertIn('SecretTenantDelta', content)
        self.assertIn('disabled="disabled"', content)
        self.assertIn('restricted values that cannot be changed', content)


class RestrictedTypeDrivenSelectorTest(TestCase):
    """Forms whose selector model is chosen by a paired content-type field preserve hidden current values."""

    def setUp(self):
        super().setUp()
        # The user may edit, but has no view permission on the related models, so their values are hidden.
        self.add_permissions(
            'ipam.add_service', 'ipam.change_service',
            'ipam.add_vlangroup', 'ipam.change_vlangroup',
            'vpn.add_tunneltermination', 'vpn.change_tunneltermination',
            'circuits.add_circuittermination', 'circuits.change_circuittermination',
            'circuits.add_circuitgroupassignment', 'circuits.change_circuitgroupassignment',
            'extras.add_eventrule', 'extras.change_eventrule',
        )
        self.device = create_test_device('Device 1')
        self.interface = Interface.objects.create(device=self.device, name='eth0', type='1000base-t')

    def test_service_parent_hidden_is_preserved(self):
        """A Service whose parent device is hidden keeps that parent on save."""
        service = Service.objects.create(name='svc', protocol='tcp', ports=[80], parent=self.device)
        device_ct = ObjectType.objects.get_for_model(Device)

        form = ServiceForm(
            data={'name': 'svc', 'protocol': 'tcp', 'ports': '80', 'parent_object_type': device_ct.pk},
            instance=service,
        )
        restrict_form_fields(form, self.user)

        self.assertTrue(form.fields['parent'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        service = form.save()
        self.assertEqual(service.parent, self.device)

    def test_service_parent_type_tamper_is_blocked(self):
        """Switching parent_object_type while the current parent is hidden cannot drop or remap the parent."""
        service = Service.objects.create(name='svc', protocol='tcp', ports=[80], parent=self.device)
        vm_ct = ObjectType.objects.get_for_model(VirtualMachine)

        form = ServiceForm(
            # Tampered: claim the parent is now a VirtualMachine, with no parent selected.
            data={'name': 'svc', 'protocol': 'tcp', 'ports': '80', 'parent_object_type': vm_ct.pk, 'parent': ''},
            instance=service,
        )
        restrict_form_fields(form, self.user)

        self.assertTrue(form.fields['parent'].disabled)
        self.assertTrue(form.fields['parent_object_type'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        service = form.save()
        self.assertEqual(service.parent, self.device)
        self.assertEqual(service.parent_object_type.model_class(), Device)

    def test_vlangroup_scope_hidden_is_preserved(self):
        """A VLANGroup whose scope site is hidden keeps that scope on save."""
        site = Site.objects.create(name='Scope Site', slug='scope-site')
        group = VLANGroup.objects.create(name='Group 1', slug='group-1', scope=site)
        site_ct = ObjectType.objects.get_for_model(Site)

        form = VLANGroupForm(
            data={'name': 'Group 1', 'slug': 'group-1', 'vid_ranges': '1-100', 'scope_type': site_ct.pk},
            instance=group,
        )
        restrict_form_fields(form, self.user)

        self.assertTrue(form.fields['scope'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        group = form.save()
        self.assertEqual(group.scope, site)

    def test_tunneltermination_hidden_is_preserved(self):
        """A TunnelTermination whose interface is hidden keeps that termination on save."""
        tunnel = Tunnel.objects.create(name='Tunnel 1', encapsulation='gre', status='active')
        termination = TunnelTermination.objects.create(tunnel=tunnel, role='peer', termination=self.interface)

        form = TunnelTerminationForm(
            data={'tunnel': tunnel.pk, 'role': 'peer', 'type': TunnelTerminationTypeChoices.TYPE_DEVICE},
            instance=termination,
        )
        restrict_form_fields(form, self.user)

        self.assertTrue(form.fields['termination'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        termination = form.save()
        self.assertEqual(termination.termination, self.interface)

    def test_tunneltermination_type_tamper_is_blocked(self):
        """Switching the termination type while the interface is hidden cannot drop or remap it."""
        tunnel = Tunnel.objects.create(name='Tunnel 1', encapsulation='gre', status='active')
        termination = TunnelTermination.objects.create(tunnel=tunnel, role='peer', termination=self.interface)

        form = TunnelTerminationForm(
            # Tampered: claim a virtual-machine termination, with nothing selected.
            data={
                'tunnel': tunnel.pk, 'role': 'peer',
                'type': TunnelTerminationTypeChoices.TYPE_VIRTUALMACHINE, 'parent': '', 'termination': '',
            },
            instance=termination,
        )
        restrict_form_fields(form, self.user)

        self.assertTrue(form.fields['termination'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        termination = form.save()
        self.assertEqual(termination.termination, self.interface)

    def test_circuittermination_hidden_is_preserved(self):
        """A CircuitTermination whose terminating site is hidden keeps that termination on save."""
        self.add_permissions('circuits.view_circuit')
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Type 1', slug='type-1')
        circuit = Circuit.objects.create(provider=provider, type=circuit_type, cid='Circuit 1')
        site = Site.objects.create(name='Term Site', slug='term-site')
        termination = CircuitTermination.objects.create(circuit=circuit, term_side='A', termination=site)
        site_ct = ObjectType.objects.get_for_model(Site)

        form = CircuitTerminationForm(
            data={'circuit': circuit.pk, 'term_side': 'A', 'termination_type': site_ct.pk},
            instance=termination,
        )
        restrict_form_fields(form, self.user)

        self.assertTrue(form.fields['termination'].disabled)
        self.assertTrue(form.fields['termination_type'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        termination = form.save()
        self.assertEqual(termination.termination, site)

    def test_circuittermination_type_tamper_is_blocked(self):
        """Switching termination_type while the current termination is hidden cannot drop or remap it."""
        self.add_permissions('circuits.view_circuit')
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Type 1', slug='type-1')
        circuit = Circuit.objects.create(provider=provider, type=circuit_type, cid='Circuit 1')
        site = Site.objects.create(name='Term Site', slug='term-site')
        termination = CircuitTermination.objects.create(circuit=circuit, term_side='A', termination=site)
        providernetwork_ct = ObjectType.objects.get_for_model(ProviderNetwork)

        form = CircuitTerminationForm(
            # Tampered: claim a provider-network termination, with nothing selected.
            data={
                'circuit': circuit.pk, 'term_side': 'A',
                'termination_type': providernetwork_ct.pk, 'termination': '',
            },
            instance=termination,
        )
        restrict_form_fields(form, self.user)

        self.assertTrue(form.fields['termination'].disabled)
        self.assertTrue(form.fields['termination_type'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        termination = form.save()
        self.assertEqual(termination.termination, site)
        self.assertEqual(termination.termination_type.model_class(), Site)

    def test_circuitgroupassignment_hidden_is_preserved(self):
        """A group assignment whose member circuit is hidden keeps that member on save."""
        self.add_permissions('circuits.view_circuitgroup')
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Type 1', slug='type-1')
        circuit = Circuit.objects.create(provider=provider, type=circuit_type, cid='Circuit 1')
        group = CircuitGroup.objects.create(name='Group 1', slug='group-1')
        assignment = CircuitGroupAssignment.objects.create(group=group, member=circuit)
        circuit_ct = ObjectType.objects.get_for_model(Circuit)

        form = CircuitGroupAssignmentForm(
            data={'group': group.pk, 'member_type': circuit_ct.pk},
            instance=assignment,
        )
        restrict_form_fields(form, self.user)

        self.assertTrue(form.fields['member'].disabled)
        self.assertTrue(form.fields['member_type'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        assignment = form.save()
        self.assertEqual(assignment.member, circuit)

    def test_circuitgroupassignment_type_tamper_is_blocked(self):
        """Switching member_type while the current member is hidden cannot drop or remap it."""
        self.add_permissions('circuits.view_circuitgroup')
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Type 1', slug='type-1')
        circuit = Circuit.objects.create(provider=provider, type=circuit_type, cid='Circuit 1')
        group = CircuitGroup.objects.create(name='Group 1', slug='group-1')
        assignment = CircuitGroupAssignment.objects.create(group=group, member=circuit)
        virtualcircuit_ct = ObjectType.objects.get_for_model(VirtualCircuit)

        form = CircuitGroupAssignmentForm(
            # Tampered: claim a virtual-circuit member, with nothing selected.
            data={'group': group.pk, 'member_type': virtualcircuit_ct.pk, 'member': ''},
            instance=assignment,
        )
        restrict_form_fields(form, self.user)

        self.assertTrue(form.fields['member'].disabled)
        self.assertTrue(form.fields['member_type'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        assignment = form.save()
        self.assertEqual(assignment.member, circuit)
        self.assertEqual(assignment.member_type.model_class(), Circuit)

    def test_eventrule_hidden_webhook_is_preserved(self):
        """An EventRule whose webhook is hidden keeps its action object on save."""
        webhook = Webhook.objects.create(name='Webhook 1', payload_url='http://example.com/')
        rule = EventRule.objects.create(
            name='Rule 1',
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object=webhook,
            event_types=['object_created'],
        )
        site_ot = ObjectType.objects.get_for_model(Site)
        rule.object_types.set([site_ot])

        form = EventRuleForm(
            data={
                'name': 'Rule 1',
                'object_types': [site_ot.pk],
                'event_types': ['object_created'],
                'action_type': EventRuleActionChoices.WEBHOOK,
            },
            instance=rule,
        )
        restrict_form_fields(form, self.user)

        self.assertTrue(form.fields['action_choice'].disabled)
        self.assertTrue(form.fields['action_type'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        rule = EventRule.objects.get(pk=rule.pk)
        self.assertEqual(rule.action_object, webhook)

    def test_eventrule_action_type_tamper_is_blocked(self):
        """Switching action_type while the action object is hidden cannot remap the action."""
        webhook = Webhook.objects.create(name='Webhook 1', payload_url='http://example.com/')
        rule = EventRule.objects.create(
            name='Rule 1',
            action_type=EventRuleActionChoices.WEBHOOK,
            action_object=webhook,
            event_types=['object_created'],
        )
        site_ot = ObjectType.objects.get_for_model(Site)
        rule.object_types.set([site_ot])
        group = NotificationGroup.objects.create(name='Group 1')

        form = EventRuleForm(
            # Tampered: claim a notification action targeting another object.
            data={
                'name': 'Rule 1',
                'object_types': [site_ot.pk],
                'event_types': ['object_created'],
                'action_type': EventRuleActionChoices.NOTIFICATION,
                'action_choice': group.pk,
            },
            instance=rule,
        )
        restrict_form_fields(form, self.user)

        self.assertTrue(form.fields['action_choice'].disabled)
        self.assertTrue(form.fields['action_type'].disabled)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        rule = EventRule.objects.get(pk=rule.pk)
        self.assertEqual(rule.action_object, webhook)
        self.assertEqual(rule.action_object_type.model_class(), Webhook)
        self.assertEqual(rule.action_object_id, webhook.pk)
