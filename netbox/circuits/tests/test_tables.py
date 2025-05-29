from django.test import RequestFactory, tag, TestCase

from circuits.models import CircuitTermination
from circuits.tables import CircuitTerminationTable


@tag('regression')
class CircuitTerminationTableTest(TestCase):
    def test_every_orderable_field_does_not_throw_exception(self):
        terminations = CircuitTermination.objects.all()
        disallowed = {'actions', }

        orderable_columns = [
            column.name for column in CircuitTerminationTable(terminations).columns
            if column.orderable and column.name not in disallowed
        ]
        fake_request = RequestFactory().get("/")

        for col in orderable_columns:
            for dir in ('-', ''):
                table = CircuitTerminationTable(terminations)
                table.order_by = f'{dir}{col}'
                table.as_html(fake_request)
