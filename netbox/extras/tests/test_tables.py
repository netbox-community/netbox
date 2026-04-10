from django.test import RequestFactory, TestCase, tag

from extras.models import EventRule
from extras.tables import EventRuleTable


@tag('regression')
class EventRuleTableTest(TestCase):
    def test_every_orderable_field_does_not_throw_exception(self):
        rule = EventRule.objects.all()
        disallowed = {
            'actions',
        }

        orderable_columns = [
            column.name for column in EventRuleTable(rule).columns if column.orderable and column.name not in disallowed
        ]
        fake_request = RequestFactory().get('/')

        for col in orderable_columns:
            for direction in ('-', ''):
                table = EventRuleTable(rule)
                table.order_by = f'{direction}{col}'
                table.as_html(fake_request)
