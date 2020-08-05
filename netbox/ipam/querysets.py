from utilities.querysets import RestrictedQuerySet


class PrefixQuerySet(RestrictedQuerySet):

    def annotate_tree(self):
        """
        Annotate the number of parent and child prefixes for each Prefix. Raw SQL is needed for these subqueries
        because we need to cast NULL VRF values to integers for comparison. (NULL != NULL).
        """
        return self.extra(
            select={
                'parents': 'SELECT COUNT(U0."prefix") AS "c" '
                           'FROM "ipam_prefix" U0 '
                           'WHERE (U0."prefix" >> "ipam_prefix"."prefix" '
                           'AND COALESCE(U0."vrf_id", 0) = COALESCE("ipam_prefix"."vrf_id", 0))',
                'children': 'SELECT COUNT(U1."prefix") AS "c" '
                            'FROM "ipam_prefix" U1 '
                            'WHERE (U1."prefix" << "ipam_prefix"."prefix" '
                            'AND COALESCE(U1."vrf_id", 0) = COALESCE("ipam_prefix"."vrf_id", 0))',
            }
        )
