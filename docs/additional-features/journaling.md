# Journaling

All primary objects in NetBox support journaling. A journal is a collection of human-generated notes and comments about an object maintained for historical context. It supplements NetBox's change log to provide additional information about why changes have been made or to convey events which occur outside NetBox. Unlike the change log, in which records typically expire after a configurable period of time, journal entries persist for the life of their associated object.

Each journal entry has a selectable kind (info, success, warning, or danger) and a user-populated `comments` field. Each entry automatically records the date, time, and associated user upon being created.
