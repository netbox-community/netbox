from __future__ import unicode_literals

from django.db.models import Manager


class NaturalOrderByManager(Manager):
    """
    Order objects naturally by a designated field. Leading and/or trailing digits of values within this field will be
    cast as independent integers and sorted accordingly. For example, "Foo2" will be ordered before "Foo10", even though
    the digit 1 is normally ordered before the digit 2.
    """
    natural_order_field = None

    def get_queryset(self):

        queryset = super(NaturalOrderByManager, self).get_queryset()

        db_table = self.model._meta.db_table
        db_field = self.natural_order_field

        # Append the three subfields derived from the designated natural ordering field
        queryset = queryset.extra(select={
            '_nat1': r"CAST(SUBSTRING({}.{} FROM '^(\d{{1,9}})') AS integer)".format(db_table, db_field),
            '_nat2': r"SUBSTRING({}.{} FROM '^\d*(.*?)\d*$')".format(db_table, db_field),
            '_nat3': r"CAST(SUBSTRING({}.{} FROM '(\d{{1,9}})$') AS integer)".format(db_table, db_field),
        })

        # Replace any instance of the designated natural ordering field with its three subfields
        ordering = []
        for field in self.model._meta.ordering:
            if field == self.natural_order_field:
                ordering.append('_nat1')
                ordering.append('_nat2')
                ordering.append('_nat3')
            else:
                ordering.append(field)

        return queryset.order_by(*ordering)
