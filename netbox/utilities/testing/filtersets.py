__all__ = (
    'BaseFilterSetTests',
)


class BaseFilterSetTests:
    queryset = None
    filterset = None

    def test_id(self):
        """
        Test filtering for two PKs from a set of >2 objects.
        """
        params = {'id': self.queryset.values_list('pk', flat=True)[:2]}
        self.assertGreater(self.queryset.count(), 2)
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
