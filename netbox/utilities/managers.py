from django.db.models import Manager

NAT1 = r"CAST(SUBSTRING({}.{} FROM '^(\d{{1,9}})') AS integer)"
NAT2 = r"SUBSTRING({}.{} FROM '^\d*(.*?)\d*$')"
NAT3 = r"CAST(SUBSTRING({}.{} FROM '(\d{{1,9}})$') AS integer)"


class NaturalOrderingManager(Manager):
    """
    Order objects naturally by a designated field (defaults to 'name'). Leading and/or trailing digits of values within
    this field will be cast as independent integers and sorted accordingly. For example, "Foo2" will be ordered before
    "Foo10", even though the digit 1 is normally ordered before the digit 2.
    """
    natural_order_field = 'name'

    def get_queryset(self):

        queryset = super().get_queryset()

        db_table = self.model._meta.db_table
        db_field = self.natural_order_field

        # Append the three subfields derived from the designated natural ordering field
        queryset = queryset.extra(select={
            '_nat1': NAT1.format(db_table, db_field),
            '_nat2': NAT2.format(db_table, db_field),
            '_nat3': NAT3.format(db_table, db_field),
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

        # Default to using the _nat indexes if Meta.ordering is empty
        if not ordering:
            ordering = ('_nat1', '_nat2', '_nat3')

        return queryset.order_by(*ordering)
