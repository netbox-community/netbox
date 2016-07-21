from django.db.models import Manager


class NaturalOrderByManager(Manager):

    def natural_order_by(self, *fields):
        """
        Attempt to order records naturally by segmenting a field into three parts:

        1. Leading integer (if any)
        2. Middle portion
        3. Trailing integer (if any)

        :param fields: The fields on which to order the queryset. The last field in the list will be ordered naturally.
        """
        db_table = self.model._meta.db_table
        primary_field = fields[-1]

        id1 = '_{}_{}1'.format(db_table, primary_field)
        id2 = '_{}_{}2'.format(db_table, primary_field)
        id3 = '_{}_{}3'.format(db_table, primary_field)

        queryset = super(NaturalOrderByManager, self).get_queryset().extra(select={
            id1: "CAST(SUBSTRING({}.{} FROM '^(\d+)') AS integer)".format(db_table, primary_field),
            id2: "SUBSTRING({}.{} FROM '^\d*(.*?)\d*$')".format(db_table, primary_field),
            id3: "CAST(SUBSTRING({}.{} FROM '(\d+)$') AS integer)".format(db_table, primary_field),
        })
        ordering = fields[0:-1] + (id1, id2, id3)

        return queryset.order_by(*ordering)
