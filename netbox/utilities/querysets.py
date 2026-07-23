from django.conf import settings
from django.db import router, transaction
from django.db.models import Max, Prefetch, QuerySet

from users.constants import CONSTRAINT_TOKEN_USER
from utilities.permissions import get_permission_for_model, permission_is_exempt, qs_filter_from_constraints

__all__ = (
    'RestrictedPrefetch',
    'RestrictedQuerySet',
    'chunked_update',
)


def chunked_update(queryset, chunk_size=None, **kwargs):
    """
    Perform a bulk UPDATE on the given queryset, optionally splitting it into batches of at most
    `chunk_size` rows. Bounding the number of rows touched by each statement avoids exceeding the
    database's statement timeout when updating very large tables. Batches are selected via keyset
    pagination on the primary key and wrapped in a transaction so that the operation remains atomic,
    as it would be when performed by a single UPDATE. Returns the total number of rows updated
    (matching the return value of QuerySet.update()).

    If `chunk_size` is None, it falls back to the BULK_UPDATE_CHUNK_SIZE configuration parameter
    (5000 by default). If that is also None, a single unbounded UPDATE is issued, identical to
    calling queryset.update(**kwargs) directly.

    :param queryset: The QuerySet identifying the rows to update
    :param chunk_size: The maximum number of rows to update per statement (defaults to
        settings.BULK_UPDATE_CHUNK_SIZE)
    """
    if chunk_size is None:
        chunk_size = settings.BULK_UPDATE_CHUNK_SIZE
    if chunk_size is not None and (type(chunk_size) is not int or chunk_size < 1):
        raise ValueError(f"chunk_size must be a positive integer or None (found {chunk_size!r})")
    if chunk_size is None:
        return queryset.update(**kwargs)

    model = queryset.model

    # Pin the entire operation to a single write database so that the PK lookups, the UPDATE
    # statements, and the enclosing transaction all use the same connection. This preserves an
    # explicit .using() on the queryset and otherwise honors the router's write destination.
    using = queryset._db or router.db_for_write(model)

    count = 0
    last_pk = 0
    # Upper bound on the PKs to process. Established lazily (see below) only once a second batch is
    # known to be needed, so the common single-batch case incurs no extra aggregate query.
    max_pk = None
    with transaction.atomic(using=using):
        while True:
            batch = queryset.using(using).filter(pk__gt=last_pk).order_by('pk')
            if max_pk is not None:
                batch = batch.filter(pk__lte=max_pk)
            pks = list(batch.values_list('pk', flat=True)[:chunk_size])
            if not pks:
                break
            # Re-filter the original queryset by pk__in (rather than the model's default manager) so
            # that its own filters are preserved and rows no longer matching them are left untouched.
            count += queryset.using(using).filter(pk__in=pks).update(**kwargs)
            last_pk = pks[-1]
            # A batch shorter than chunk_size means the rows are exhausted; stop without issuing a
            # trailing (empty) lookup. This keeps a single-batch update to one SELECT and one UPDATE.
            if len(pks) < chunk_size:
                break
            # A full batch means more rows may remain. Capture the current maximum PK as an upper
            # bound (once) so that rows inserted while the operation runs cannot keep extending it.
            if max_pk is None:
                max_pk = queryset.using(using).aggregate(_max=Max('pk'))['_max']

    return count


class RestrictedPrefetch(Prefetch):
    """
    Extend Django's Prefetch to accept a user and action to be passed to the
    `restrict()` method of the related object's queryset.
    """
    def __init__(self, lookup, user, action='view', queryset=None, to_attr=None):
        self.restrict_user = user
        self.restrict_action = action

        super().__init__(lookup, queryset=queryset, to_attr=to_attr)

    def get_current_querysets(self, level):
        params = {
            'user': self.restrict_user,
            'action': self.restrict_action,
        }

        if querysets := super().get_current_querysets(level):
            return [qs.restrict(**params) for qs in querysets]

        # Bit of a hack. If no queryset is defined, pass through the dict of restrict()
        # kwargs to be handled by the field. This is necessary e.g. for GenericForeignKey
        # fields, which do not permit setting a queryset on a Prefetch object.
        return params


class RestrictedQuerySet(QuerySet):

    def restrict(self, user, action='view'):
        """
        Filter the QuerySet to return only objects on which the specified user has been granted the specified
        permission.

        :param user: User instance
        :param action: The action which must be permitted (e.g. "view" for "dcim.view_site"); default is 'view'
        """
        # Resolve the full name of the required permission
        permission_required = get_permission_for_model(self.model, action)

        # Bypass restriction for superusers and exempt views
        if (user and user.is_active and user.is_superuser) or permission_is_exempt(permission_required):
            return self

        # User is anonymous or has not been granted the requisite permission
        if user is None or not user.is_authenticated or permission_required not in user.get_all_permissions():
            return self.none()

        # Filter the queryset to include only objects with allowed attributes
        constraints = user._object_perm_cache[permission_required]
        tokens = {
            CONSTRAINT_TOKEN_USER: user,
        }
        if attrs := qs_filter_from_constraints(constraints, tokens):
            # #8715: Avoid duplicates when JOIN on many-to-many fields without using DISTINCT.
            # DISTINCT acts globally on the entire request, which may not be desirable.
            allowed_objects = self.model.objects.filter(attrs)
            return self.filter(pk__in=allowed_objects)

        return self
