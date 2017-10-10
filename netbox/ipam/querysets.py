from __future__ import unicode_literals

from utilities.sql import NullsFirstQuerySet


class PrefixQuerySet(NullsFirstQuerySet):

    def annotate_depth(self, limit=None):
        """
        Iterate through a QuerySet of Prefixes and annotate the hierarchical level of each. While it would be preferable
        to do this using .extra() on the QuerySet to count the unique parents of each prefix, that approach introduces
        performance issues at scale.

        Because we're adding a non-field attribute to the model, annotation must be made *after* any QuerySet
        modifications.
        """
        queryset = self
        stack = []
        for p in queryset:
            try:
                prev_p = stack[-1]
            except IndexError:
                prev_p = None
            if prev_p is not None:
                while (p.prefix not in prev_p.prefix) or p.prefix == prev_p.prefix:
                    stack.pop()
                    try:
                        prev_p = stack[-1]
                    except IndexError:
                        prev_p = None
                        break
            if prev_p is not None:
                prev_p.has_children = True
            stack.append(p)
            p.depth = len(stack) - 1
        if limit is None:
            return queryset
        return list(filter(lambda p: p.depth <= limit, queryset))
