# Journal Entries

All primary objects in NetBox support journaling. A journal is a collection of human-generated notes and comments about an object maintained for historical context. It supplements NetBox's change log to provide additional information about why changes have been made or to convey events which occur outside of NetBox. Unlike the change log, which is typically limited in the amount of history it retains, journal entries never expire.

Each journal entry has a user-populated `commnets` field. Each entry records the date and time, associated user, and object automatically upon being created.
