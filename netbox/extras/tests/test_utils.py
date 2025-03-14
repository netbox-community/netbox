from django.test import TestCase

from extras.models import ExportTemplate
from extras.utils import filename_from_model
from tenancy.models import ContactGroup, TenantGroup
from wireless.models import WirelessLANGroup


class FilenameFromModelTests(TestCase):
    def test_expected_output(self):
        cases = (
            (ExportTemplate, 'netbox_export_templates'),
            (ContactGroup, 'netbox_contact_groups'),
            (TenantGroup, 'netbox_tenant_groups'),
            (WirelessLANGroup, 'netbox_wireless_lan_groups'),
        )

        for model, expected in cases:
            self.assertEqual(filename_from_model(model), expected)
