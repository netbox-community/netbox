from __future__ import unicode_literals

from django.db.models import QuerySet
from django.db.models.expressions import RawSQL

from .constants import IFACE_ORDERING_NAME, IFACE_ORDERING_POSITION, NONCONNECTABLE_IFACE_TYPES


class InterfaceQuerySet(QuerySet):

    def order_naturally(self, method=IFACE_ORDERING_POSITION):
        """
        Naturally order interfaces by their type and numeric position. The sort method must be one of the defined
        IFACE_ORDERING_CHOICES (typically indicated by a parent Device's DeviceType).

        To order interfaces naturally, the `name` field is split into six distinct components: leading text (type),
        slot, subslot, position, channel, and virtual circuit:

            {type}{slot}/{subslot}/{position}/{subposition}:{channel}.{vc}

        Components absent from the interface name are ignored. For example, an interface named GigabitEthernet1/2/3
        would be parsed as follows:

            name = 'GigabitEthernet'
            slot =  1
            subslot = 2
            position = 3
            subposition = 0
            channel = None
            vc = 0

        The original `name` field is taken as a whole to serve as a fallback in the event interfaces do not match any of
        the prescribed fields.
        """
        sql_col = '{}.name'.format(self.model._meta.db_table)
        ordering = {
            IFACE_ORDERING_POSITION: (
                '_slot', '_subslot', '_position', '_subposition', '_channel', '_type', '_vc', '_id', 'name',
            ),
            IFACE_ORDERING_NAME: (
                '_type', '_slot', '_subslot', '_position', '_subposition', '_channel', '_vc', '_id', 'name',
            ),
        }[method]

        TYPE_RE = r"SUBSTRING({} FROM '^([^0-9]+)')"
        ID_RE = r"CAST(SUBSTRING({} FROM '^(?:[^0-9]+)(\d{{1,9}})$') AS integer)"
        SLOT_RE = r"CAST(SUBSTRING({} FROM '^(?:[^0-9]+)?(\d{{1,9}})\/') AS integer)"
        SUBSLOT_RE = r"COALESCE(CAST(SUBSTRING({} FROM '^(?:[^0-9]+)?(?:\d{{1,9}}\/)(\d{{1,9}})') AS integer), 0)"
        POSITION_RE = r"COALESCE(CAST(SUBSTRING({} FROM '^(?:[^0-9]+)?(?:\d{{1,9}}\/){{2}}(\d{{1,9}})') AS integer), 0)"
        SUBPOSITION_RE = r"COALESCE(CAST(SUBSTRING({} FROM '^(?:[^0-9]+)?(?:\d{{1,9}}\/){{3}}(\d{{1,9}})') AS integer), 0)"
        CHANNEL_RE = r"COALESCE(CAST(SUBSTRING({} FROM ':(\d{{1,9}})(\.\d{{1,9}})?$') AS integer), 0)"
        VC_RE = r"COALESCE(CAST(SUBSTRING({} FROM '\.(\d{{1,9}})$') AS integer), 0)"

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

        return self.annotate(**fields).order_by(*ordering)

    def connectable(self):
        """
        Return only physical interfaces which are capable of being connected to other interfaces (i.e. not virtual or
        wireless).
        """
        return self.exclude(form_factor__in=NONCONNECTABLE_IFACE_TYPES)
