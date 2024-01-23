import django_tables2 as tables

from dcim.tables import SiteTable
from utilities.tables import register_table_column

mycol = tables.Column(
    verbose_name='My column',
    accessor=tables.A('description')
)

register_table_column(mycol, 'foo', SiteTable)
