from django.test import RequestFactory, tag, TestCase

from vpn.models import TunnelTermination
from vpn.tables import TunnelTerminationTable


@tag('regression')
class TunnelTerminationTableTest(TestCase):
    def test_every_orderable_field_does_not_throw_exception(self):
        terminations = TunnelTermination.objects.all()
        fake_request = RequestFactory().get("/")
        disallowed = {'actions'}

        orderable_columns = [
            column.name for column in TunnelTerminationTable(terminations).columns
            if column.orderable and column.name not in disallowed
        ]

        for col in orderable_columns:
            for dir in ('-', ''):
                table = TunnelTerminationTable(terminations)
                table.order_by = f'{dir}{col}'
                table.as_html(fake_request)
