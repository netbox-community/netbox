from django.db.models import Manager, QuerySet
from django.db.models.expressions import RawSQL

from .constants import NONCONNECTABLE_IFACE_TYPES

# Regular expressions for parsing Interface names
TYPE_RE = r"SUBSTRING({} FROM '^([^0-9\.:]+)')"
SLOT_RE = r"COALESCE(CAST(SUBSTRING({} FROM '^(?:[^0-9]+)?(\d{{1,9}})/') AS integer), NULL)"
SUBSLOT_RE = r"COALESCE(CAST(SUBSTRING({} FROM '^(?:[^0-9\.:]+)?\d{{1,9}}/(\d{{1,9}})') AS integer), NULL)"
POSITION_RE = r"COALESCE(CAST(SUBSTRING({} FROM '^(?:[^0-9]+)?(?:\d{{1,9}}/){{2}}(\d{{1,9}})') AS integer), NULL)"
SUBPOSITION_RE = r"COALESCE(CAST(SUBSTRING({} FROM '^(?:[^0-9]+)?(?:\d{{1,9}}/){{3}}(\d{{1,9}})') AS integer), NULL)"
ID_RE = r"CAST(SUBSTRING({} FROM '^(?:[^0-9\.:]+)?(\d{{1,9}})([^/]|$)') AS integer)"
CHANNEL_RE = r"COALESCE(CAST(SUBSTRING({} FROM '^.*:(\d{{1,9}})(\.\d{{1,9}})?$') AS integer), 0)"
VC_RE = r"COALESCE(CAST(SUBSTRING({} FROM '^.*\.(\d{{1,9}})$') AS integer), 0)"


class InterfaceQuerySet(QuerySet):

    def connectable(self):
        """
        Return only physical interfaces which are capable of being connected to other interfaces (i.e. not virtual or
        wireless).
        """
        return self.exclude(type__in=NONCONNECTABLE_IFACE_TYPES)


class InterfaceManager(Manager):

    def get_queryset(self):
        """
        Naturally order interfaces by their type and numeric position. To order interfaces naturally, the `name` field
        is split into eight distinct components: leading text (type), slot, subslot, position, subposition, ID, channel,
        and virtual circuit:

            {type}{slot or ID}/{subslot}/{position}/{subposition}:{channel}.{vc}

        Components absent from the interface name are coalesced to zero or null. For example, an interface named
        GigabitEthernet1/2/3 would be parsed as follows:

            type = 'GigabitEthernet'
            slot =  1
            subslot = 2
            position = 3
            subposition = None
            id = None
            channel = 0
            vc = 0

        The original `name` field is considered in its entirety to serve as a fallback in the event interfaces do not
        match any of the prescribed fields.

        The `id` field is included to enforce deterministic ordering of interfaces in similar vein of other device
        components.
        """

        sql_col = '{}.name'.format(self.model._meta.db_table)
        ordering = [
            '_slot', '_subslot', '_position', '_subposition', '_type', '_id', '_channel', '_vc', 'name', 'pk'

        ]

        fields = {
            '_type': RawSQL(TYPE_RE.format(sql_col), []),
            '_id': RawSQL(ID_RE.format(sql_col), []),
            '_slot': RawSQL(SLOT_RE.format(sql_col), []),
            '_subslot': RawSQL(SUBSLOT_RE.format(sql_col), []),
            '_position': RawSQL(POSITION_RE.format(sql_col), []),
            '_subposition': RawSQL(SUBPOSITION_RE.format(sql_col), []),
            '_channel': RawSQL(CHANNEL_RE.format(sql_col), []),
            '_vc': RawSQL(VC_RE.format(sql_col), []),
        }

        return InterfaceQuerySet(self.model, using=self._db).annotate(**fields).order_by(*ordering)
