import hashlib
import json
import logging
import time

from graphql.language import (
    FloatValueNode,
    IntValueNode,
    ListValueNode,
    ObjectValueNode,
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
    'normalize_query',
)

logger = logging.getLogger('netbox.graphql.query')


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
        # A list of scalars collapses to an empty list so that its length doesn't matter. Lists of input objects
        # (e.g. OR clauses in a filter) are kept, since their structure is part of the query shape.
        if any(isinstance(value, (ListValueNode, ObjectValueNode)) for value in node.values):
            return None
        return ListValueNode(values=())


def normalize_query(document):
    """
    Return the given GraphQL document as a single line, with its literal argument values replaced by placeholders.
    """
    return strip_ignored_characters(print_ast(visit(document, LiteralValueStripper())))


class QueryLogger(SchemaExtension):
    """
    Log each GraphQL operation to the `netbox.graphql.query` logger. Does nothing unless that logger is enabled for
    INFO messages.
    """
    def on_operation(self):
        if not logger.isEnabledFor(logging.INFO):
            yield
            return

        start = time.perf_counter()
        yield
        duration = (time.perf_counter() - start) * 1000

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
        if execution_context.graphql_document is not None:
            query = normalize_query(execution_context.graphql_document)
            query_hash = hashlib.sha256(query.encode()).hexdigest()
        else:
            query = query_hash = None

        # Summarize the result
        result = execution_context.result
        errors = (result.errors if result else None) or execution_context.pre_execution_errors or []
        if result is not None and result.data is not None:
            response_size = len(json.dumps(result.data, default=str).encode())
        else:
            response_size = 0

        data = {
            'user': user.username if user is not None and user.is_authenticated else None,
            'token_id': getattr(token, 'pk', None),
            'client_ip': str(client_ip) if client_ip else None,
            'operation_name': execution_context.operation_name,
            'query_hash': query_hash,
            'query': query,
            'variables': execution_context.variables,
            'duration_ms': round(duration, 1),
            'error_count': len(errors),
            'response_size': response_size,
        }
        logger.info(
            "user=%s token_id=%s client_ip=%s operation_name=%s query_hash=%s duration_ms=%s error_count=%s "
            "response_size=%s query=%s variables=%s",
            data['user'],
            data['token_id'],
            data['client_ip'],
            data['operation_name'],
            data['query_hash'],
            data['duration_ms'],
            data['error_count'],
            data['response_size'],
            data['query'],
            json.dumps(data['variables'], default=str),
            extra={'graphql': data},
        )
