from collections.abc import Sequence

from django.utils.translation import gettext_lazy as _

from .client import error_of
from .constants import CATALOG_MAX_PAGE_SIZE

__all__ = (
    'COVERAGE_CATEGORIES',
    'CatalogResults',
    'annotate_entries',
    'get_coverage',
)

# Enrichment categories reported by the catalog, in display order
COVERAGE_CATEGORIES = (
    ('lifecycle', _('Lifecycle')),
    ('thermal', _('Thermal')),
    ('environmental', _('Environmental')),
    ('operational', _('Operational')),
    ('platform', _('Platform')),
    ('snmp', _('SNMP')),
    ('gnmi', _('gNMI')),
    ('netconf', _('NETCONF')),
    ('redfish', _('Redfish')),
    ('modbus', _('Modbus')),
    ('imagery', _('Imagery')),
)


def annotate_entries(entries, user):
    """
    Attach each catalog entry's NDX ID and local import record (if any) using a single query.
    """
    from .models import ImportRecord

    for entry in entries:
        entry['ndx_id'] = f"{entry.get('vendor_slug')}/{entry.get('slug')}"
    records = ImportRecord.objects.restrict(user, 'view').filter(ndx_id__in=[e['ndx_id'] for e in entries])
    records = {record.ndx_id: record for record in records}
    for entry in entries:
        entry['import_record'] = records.get(entry['ndx_id'])
    return entries


def get_coverage(entry):
    """
    Return the catalog's enrichment coverage for an entry as a list of (label, percentage) tuples.
    """
    coverage = entry.get('enrichment_coverage') or {}
    flags = entry.get('enrichment_flags') or {}
    rows = []
    for key, label in COVERAGE_CATEGORIES:
        if key in coverage:
            ratio = coverage.get(key) or 0
        else:
            ratio = 1 if flags.get(key) else 0
        rows.append((label, round(ratio * 100)))
    return rows


class CatalogResults(Sequence):
    """
    A lazily evaluated sequence of catalog search results. Slices are retrieved from the NDX API on demand (in pages
    of up to 200 entries), allowing NetBox's paginator to page through the remote catalog. `prefetch` designates the
    slice (as an offset and limit) which is expected to be requested first: It is retrieved to determine the total
    number of results, avoiding a separate request.
    """
    def __init__(self, client, user, prefetch=None, **params):
        self.client = client
        self.user = user
        self.prefetch = prefetch
        self.params = params
        self.error = None
        self._total = None
        self._chunks = {}

    def _cached(self, offset, limit):
        for start, chunk in self._chunks.items():
            end = start + len(chunk)
            # A chunk which extends to the end of the results covers any range beyond it
            if start <= offset and (offset + limit <= end or end >= self._total):
                return chunk[offset - start:offset - start + limit]
        return None

    def _fetch(self, offset, limit):
        if (chunk := self._cached(offset, limit)) is not None:
            return chunk
        response = self.client.search(offset=offset, limit=limit, **self.params)
        if error := error_of(response):
            self.error = error
            self._total = 0
            return []
        self._total = response.get('total') or 0
        chunk = self._chunks[offset] = response.get('results') or []
        return chunk

    def __len__(self):
        if self._total is None:
            offset, limit = self.prefetch or (0, 1)
            self._fetch(offset, min(limit, CATALOG_MAX_PAGE_SIZE))
        return self._total

    def __getitem__(self, key):
        if not isinstance(key, slice):
            if key < 0:
                key += len(self)
            if not 0 <= key < len(self):
                raise IndexError(key)
            return self[key:key + 1][0]

        start, stop, step = key.indices(len(self))
        results = []
        offset = start
        while offset < stop:
            chunk = self._fetch(offset, min(stop - offset, CATALOG_MAX_PAGE_SIZE))
            if not chunk:
                break
            results.extend(chunk)
            offset += len(chunk)
        return annotate_entries(results[:stop - start], self.user)[::step]

    def __iter__(self):
        # Iterate only over the first page of results to avoid retrieving the entire catalog
        return iter(self[:CATALOG_MAX_PAGE_SIZE])
