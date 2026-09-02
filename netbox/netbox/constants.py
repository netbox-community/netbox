CORE_APPS = (
    'account',
    'circuits',
    'core',
    'dcim',
    'extras',
    'ipam',
    'tenancy',
    'users',
    'utilities',
    'virtualization',
    'vpn',
    'wireless',
)

# RQ queue names
RQ_QUEUE_DEFAULT = 'default'
RQ_QUEUE_HIGH = 'high'
RQ_QUEUE_LOW = 'low'

# Keys for PostgreSQL advisory locks. These are arbitrary bigints used by the advisory_lock
# context manager. When a lock is acquired, one of these keys will be used to identify said lock.
# When adding a new key, pick something arbitrary and unique so that it is easily searchable in
# query logs.
ADVISORY_LOCK_KEYS = {
    # Available object locks
    'available-prefixes': 100100,
    'available-ips': 100200,
    'available-vlans': 100300,
    'available-asns': 100400,

    # Jobs
    'job-schedules': 110100,

    # Custom field data
    'custom-field-data': 115100,
}

# General-purpose tokens
CENSOR_TOKEN = '********'
CENSOR_TOKEN_CHANGED = '***CHANGED***'

# Placeholder text for empty tables
EMPTY_TABLE_TEXT = 'No results found'

# Batch size for deleting a JobsMixin object's associated jobs during cascade deletion. Job
# cannot be fast-deleted (a global pre_delete receiver forces per-instance signals), so deleting
# in chunks bounds the work per delete cycle rather than building one huge collection and running
# one long DELETE. 1000 matches EXPORT_CHUNK_SIZE and, in benchmarking a 200k-job deletion, was
# the fastest of 100/1000/5000 while keeping peak memory flat. See #22812.
JOB_DELETE_BATCH_SIZE = 1000
