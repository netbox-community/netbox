import hashlib
import hmac
import logging

import requests
from django.conf import settings
from django_rq import job
from jinja2.exceptions import TemplateError

from .constants import WEBHOOK_EVENT_TYPES

logger = logging.getLogger('netbox.webhooks')


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
def send_webhook(event_rule, model_name, event_type, data, timestamp, username, request_id=None, snapshots=None):
    """
    Make a POST request to the defined Webhook
    """
    webhook = event_rule.action_object

    # Prepare context data for headers & body templates
    context = {
        'event': WEBHOOK_EVENT_TYPES.get(event_type, event_type),
        'timestamp': timestamp,
        'model': model_name,
        'username': username,
        'request_id': request_id,
        'data': data,
    }
    if snapshots:
        context.update({
            'snapshots': snapshots
        })

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
    params = {
        'method': webhook.http_method,
        'url': webhook.render_payload_url(context),
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
        response = session.send(prepared_request, proxies=settings.HTTP_PROXIES)

    if 200 <= response.status_code <= 299:
        logger.info(f"Request succeeded; response status {response.status_code}")
        return f"Status {response.status_code} returned, webhook successfully processed."
    else:
        logger.warning(f"Request failed; response status {response.status_code}: {response.content}")
        raise requests.exceptions.RequestException(
            f"Status {response.status_code} returned with content '{response.content}', webhook FAILED to process."
        )
