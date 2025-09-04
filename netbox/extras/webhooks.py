import hashlib
import hmac
import logging

import requests
from django_rq import job
from jinja2.exceptions import TemplateError

from netbox.registry import registry
from utilities.proxy import resolve_proxies
from .constants import WEBHOOK_EVENT_TYPES

__all__ = (
    'generate_signature',
    'register_webhook_callback',
    'send_webhook',
)

logger = logging.getLogger('netbox.webhooks')


def register_webhook_callback(func):
    """
    Register a function as a webhook callback.
    """
    registry['webhook_callbacks'].append(func)
    logger.debug(f'Registered webhook callback {func.__module__}.{func.__name__}')
    return func


def generate_signature(request_body, secret):
    """
    Return a cryptographic signature that can be used to verify the authenticity of webhook data.
    """
    hmac_prep = hmac.new(
        key=secret.encode('utf8'),
        msg=request_body,
        digestmod=hashlib.sha512
    )
    return hmac_prep.hexdigest()


@job('default')
def send_webhook(event_rule, object_type, event_type, data, timestamp, username, request=None, snapshots=None):
    """
    Make a POST request to the defined Webhook
    """
    webhook = event_rule.action_object

    # Prepare context data for headers & body templates
    context = {
        'event': WEBHOOK_EVENT_TYPES.get(event_type, event_type),
        'timestamp': timestamp,
        'object_type': '.'.join(object_type.natural_key()),
        'model': object_type.model,
        'username': username,
        'request_id': request.id if request else None,
        'data': data,
    }
    if snapshots:
        context.update({
            'snapshots': snapshots
        })

    # Add any additional context from plugins
    callback_data = {}
    for callback in registry['webhook_callbacks']:
        try:
            if ret := callback(object_type, event_type, data, request):
                callback_data.update(**ret)
        except Exception as e:
            logger.warning(f"Caught exception when processing callback {callback}: {e}")
            pass
    if callback_data:
        context['context'] = callback_data

    # Build the headers for the HTTP request
    headers = {
        'Content-Type': webhook.http_content_type,
    }
    try:
        headers.update(webhook.render_headers(context))
    except (TemplateError, ValueError) as e:
        logger.error(f"Error parsing HTTP headers for webhook {webhook}: {e}")
        raise e

    # Render the request body
    try:
        body = webhook.render_body(context)
    except TemplateError as e:
        logger.error(f"Error rendering request body for webhook {webhook}: {e}")
        raise e

    # Prepare the HTTP request
    url = webhook.render_payload_url(context)
    params = {
        'method': webhook.http_method,
        'url': url,
        'headers': headers,
        'data': body.encode('utf8'),
    }
    logger.info(
        f"Sending {params['method']} request to {params['url']} ({context['model']} {context['event']})"
    )
    logger.debug(params)
    try:
        prepared_request = requests.Request(**params).prepare()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error forming HTTP request: {e}")
        raise e

    # If a secret key is defined, sign the request with a hash of the key and its content
    if webhook.secret != '':
        prepared_request.headers['X-Hook-Signature'] = generate_signature(prepared_request.body, webhook.secret)

    # Send the request
    with requests.Session() as session:
        session.verify = webhook.ssl_verification
        if webhook.ca_file_path:
            session.verify = webhook.ca_file_path
        proxies = resolve_proxies(url=url, context={'client': webhook})
        response = session.send(prepared_request, proxies=proxies)

    if 200 <= response.status_code <= 299:
        logger.info(f"Request succeeded; response status {response.status_code}")
        return f"Status {response.status_code} returned, webhook successfully processed."
    else:
        logger.warning(f"Request failed; response status {response.status_code}: {response.content}")
        raise requests.exceptions.RequestException(
            f"Status {response.status_code} returned with content '{response.content}', webhook FAILED to process."
        )
