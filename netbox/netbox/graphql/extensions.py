import hashlib
import json
import logging
import threading
import time

from graphql.language import (
    FloatValueNode,
    IntValueNode,
    ListValueNode,
    StringValueNode,
    Visitor,
    print_ast,
    visit,
)
from graphql.utilities import strip_ignored_characters
from strawberry.extensions import SchemaExtension

from utilities.request import get_client_ip

__all__ = (
    'QueryLogger',
    'log_graphql_queries',
    'normalize_query',
)

logger = logging.getLogger('netbox.graphql.query')

# Maximum length of the query and variables written to a log record
MAX_LOGGED_LENGTH = 4096

# Maximum number of normalized queries to cache
NORMALIZED_QUERY_CACHE_SIZE = 512

# Attribute on the request where QueryLogger leaves records for the view to complete and emit
REQUEST_ATTR = '_graphql_query_log'


class LiteralValueStripper(Visitor):
    """
    Replace literal argument values with fixed placeholders, so that queries differing only in the values they pass
    produce the same document. Variables, enums, booleans and nulls are kept, as are the keys of input objects.
    """
    def enter_string_value(self, node, *args):
        return StringValueNode(value='')

    def enter_int_value(self, node, *args):
        return IntValueNode(value='0')

    def enter_float_value(self, node, *args):
        return FloatValueNode(value='0')

    def leave_list_value(self, node, *args):
        # A list of placeholders collapses to an empty list so that its length doesn't matter. Lists containing any
        # other values (variables, enums, input objects, etc.) are kept, since those are part of the query shape.
        if all(isinstance(value, (StringValueNode, IntValueNode, FloatValueNode)) for value in node.values):
            return ListValueNode(values=())
        return None


def normalize_query(document):
    """
    Return the given GraphQL document as a single line, with its literal argument values replaced by placeholders.
    """
    return strip_ignored_characters(print_ast(visit(document, LiteralValueStripper())))


_normalized_queries = {}
_normalized_queries_lock = threading.Lock()


def _truncate(value):
    if value is not None and len(value) > MAX_LOGGED_LENGTH:
        return f'{value[:MAX_LOGGED_LENGTH]}...'
    return value


def _normalize_query_text(query, document):
    """
    Return the normalized form of the given query (and its parsed document), truncated for logging, along with the
    hash of the full normalized query. Clients typically send the same query text repeatedly (passing values as
    variables), so the result is cached. The cache is keyed on a digest of the query text, so that large queries don't
    occupy memory.
    """
    key = hashlib.sha256(query.encode()).digest()
    if (cached := _normalized_queries.get(key)) is not None:
        return cached
    normalized = normalize_query(document)
    cached = (_truncate(normalized), hashlib.sha256(normalized.encode()).hexdigest())
    with _normalized_queries_lock:
        if len(_normalized_queries) >= NORMALIZED_QUERY_CACHE_SIZE:
            # Evict the oldest entry
            _normalized_queries.pop(next(iter(_normalized_queries)), None)
        _normalized_queries[key] = cached
    return cached


def _emit(record):
    logger.info(
        "user=%s token_id=%s client_ip=%s operation_name=%s query_hash=%s duration_ms=%s error_count=%s "
        "response_size=%s query=%s variables=%s",
        json.dumps(record['user']),  # Encode to prevent log forging
        record['token_id'],
        record['client_ip'],
        json.dumps(record['operation_name']),  # Client-supplied; encode to prevent log forging
        record['query_hash'],
        record['duration_ms'],
        record['error_count'],
        record['response_size'],
        record['query'],
        _truncate(json.dumps(record['variables'], default=str)),
        extra={'graphql': record},
    )


def log_graphql_queries(request, response):
    """
    Complete and emit any records left on the request by QueryLogger, adding the response size and the total time
    taken (including serialization of the response).
    """
    records = getattr(request, REQUEST_ATTR, None)
    if not records:
        return
    try:
        response_size = None if getattr(response, 'streaming', False) else len(response.content)
        end = time.perf_counter()
        for record, start in records:
            record['duration_ms'] = round((end - start) * 1000, 1)
            record['response_size'] = response_size
            _emit(record)
    except Exception:
        # Never let a logging failure affect the response
        logger.exception("Failed to log GraphQL operation")


class QueryLogger(SchemaExtension):
    """
    Log each GraphQL operation to the `netbox.graphql.query` logger. Does nothing unless that logger is enabled for
    INFO messages.

    The record is left on the request, to be emitted by the view once the response has been rendered (see
    log_graphql_queries()). Operations executed without a request are logged immediately, without a response size.
    """
    def on_operation(self):
        if not logger.isEnabledFor(logging.INFO):
            yield
            return

        start = time.perf_counter()
        try:
            yield
        except Exception:
            # The operation could not be executed (e.g. the requested operation name doesn't exist in the document)
            self._record(start, failed=True)
            raise
        self._record(start)

    def _record(self, start, failed=False):
        try:
            record = self._get_record(failed)
            request = getattr(self.execution_context.context, 'request', None)
            if request is None:
                record['duration_ms'] = round((time.perf_counter() - start) * 1000, 1)
                _emit(record)
            else:
                if not hasattr(request, REQUEST_ATTR):
                    setattr(request, REQUEST_ATTR, [])
                getattr(request, REQUEST_ATTR).append((record, start))
        except Exception:
            # Never let a logging failure affect the operation (or replace the exception it raised)
            logger.exception("Failed to log GraphQL operation")

    def _get_record(self, failed):
        """
        Return the details of the operation to be logged.
        """
        execution_context = self.execution_context
        request = getattr(execution_context.context, 'request', None)

        # Identify the user, token, and client
        user = getattr(request, 'user', None)
        token = getattr(request, 'auth', None)
        try:
            client_ip = get_client_ip(request) if request is not None else None
        except ValueError:
            client_ip = None

        # Normalize the query (if it could be parsed)
        if execution_context.graphql_document is not None and execution_context.query:
            query, query_hash = _normalize_query_text(execution_context.query, execution_context.graphql_document)
        else:
            query = query_hash = None

        result = execution_context.result
        errors = (result.errors if result else None) or execution_context.pre_execution_errors or []
        error_count = len(errors) or int(failed)

        return {
            'user': user.username if user is not None and user.is_authenticated else None,
            'token_id': getattr(token, 'pk', None),
            'client_ip': str(client_ip) if client_ip else None,
            'operation_name': execution_context.operation_name,
            'query_hash': query_hash,
            'query': query,
            'variables': execution_context.variables,
            'duration_ms': None,
            'error_count': error_count,
            'response_size': None,
        }
