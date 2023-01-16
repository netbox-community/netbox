import logging
import time

from django.db.backends.utils import CursorWrapper as _CursorWrapper

from netbox.exceptions import DatabaseWriteDenied

logger = logging.getLogger('netbox.db')

class ReadOnlyCursorWrapper:
    """
    This wrapper prevents write operations from being performed on the database. It is used to prevent changes to the
    database during a read-only request.
    """

    SQL_BLACKLIST = (
        # Data definition
        'CREATE',
        'ALTER',
        'DROP',
        'TRUNCATE',
        'RENAME',
        # Data manipulation
        'INSERT',
        'UPDATE',
        'DELETE',
        'MERGE',
        'REPLACE',
    )

    def __init__(self, cursor, db, *args, **kwargs):
        self.cursor = cursor
        self.db = db

    def __check_sql(self, sql):
        if self._write_sql(sql):
            raise DatabaseWriteDenied

    def execute(self, sql, params=()):
        # Check the SQL
        self.__check_sql(sql)
        return self.cursor.execute(sql, params)

    def executemany(self, sql, param_list):
        # Check the SQL
        self.__check_sql(sql)
        return self.cursor.executemany(sql, param_list)

    def __getattr__(self, item):
        return getattr(self.cursor, item)

    def __iter__(self):
        return iter(self.cursor)

    def _write_sql(self, sql):
        """
        Check the SQL to determine if it is a write operation.
        """
        return any(
            s.strip().upper().startswith(self.SQL_BLACKLIST) for s in sql.split(';')
        )

    @property
    def _last_executed(self):
        return getattr(self.cursor, '_last_executed', '')

class CursorWrapper(_CursorWrapper):
    def __init__(self, cursor, db):
        self.cursor = ReadOnlyCursorWrapper(cursor, db)
        self.db = db

class CursorDebugWrapper(CursorWrapper):
    def execute(self, sql, params=None):
        start = time.time()
        try:
            return self.cursor.execute(sql, params)
        finally:
            stop = time.time()
            duration = stop - start
            sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            self.db.queries_log.append({
                'sql': sql,
                'time': '%.3f' % duration,
            })
            logger.debug(
                "(%.3f) %s; args=%s",
                duration,
                sql,
                params,
                extra={"duration": duration, "sql": sql, "params": params},
            )

    def executemany(self, sql, param_list):
        start = time.time()
        try:
            return self.cursor.executemany(sql, param_list)
        finally:
            stop = time.time()
            duration = stop - start
            self.db.queries.append({
                "sql": "%s times: %s" % (len(param_list), sql),
                "time": "%.3f" % duration,
            })
            logger.debug(
                "(%.3f) %s; args=%s",
                duration,
                sql,
                param_list,
                extra={"duration": duration, "sql": sql, "params": param_list},
            )
