from django.test import RequestFactory, TestCase, tag

from circuits.models import CircuitGroupAssignment, CircuitTermination
from circuits.tables import CircuitGroupAssignmentTable, CircuitTerminationTable


@tag('regression')
class CircuitTerminationTableTest(TestCase):
    def test_every_orderable_field_does_not_throw_exception(self):
        terminations = CircuitTermination.objects.all()
        disallowed = {
            'actions',
        }

        orderable_columns = [
            column.name
            for column in CircuitTerminationTable(terminations).columns
            if column.orderable and column.name not in disallowed
        ]
        fake_request = RequestFactory().get('/')

        for col in orderable_columns:
            for direction in ('-', ''):
                table = CircuitTerminationTable(terminations)
                table.order_by = f'{direction}{col}'
                table.as_html(fake_request)


@tag('regression')
class CircuitGroupAssignmentTableTest(TestCase):
    def test_every_orderable_field_does_not_throw_exception(self):
        assignment = CircuitGroupAssignment.objects.all()
        disallowed = {
            'actions',
        }

        orderable_columns = [
            column.name
            for column in CircuitGroupAssignmentTable(assignment).columns
            if column.orderable and column.name not in disallowed
        ]
        fake_request = RequestFactory().get('/')

        for col in orderable_columns:
            for direction in ('-', ''):
                table = CircuitGroupAssignmentTable(assignment)
                table.order_by = f'{direction}{col}'
                table.as_html(fake_request)
