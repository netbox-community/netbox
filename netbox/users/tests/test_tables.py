from django.test import RequestFactory, TestCase, tag

from users.models import Token
from users.tables import TokenTable


class TokenTableTest(TestCase):
    @tag('regression')
    def test_every_orderable_field_does_not_throw_exception(self):
        tokens = Token.objects.all()
        disallowed = {'actions'}

        orderable_columns = [
            column.name for column in TokenTable(tokens).columns
            if column.orderable and column.name not in disallowed
        ]
        fake_request = RequestFactory().get("/")

        for col in orderable_columns:
            for direction in ('-', ''):
                with self.subTest(col=col, direction=direction):
                    table = TokenTable(tokens)
                    table.order_by = f'{direction}{col}'
                    table.as_html(fake_request)
