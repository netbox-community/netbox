import logging

import requests
from django.conf import settings
from django_rq import job
from jinja2.exceptions import TemplateError

from .choices import ObjectChangeActionChoices
from .webhooks import generate_signature

logger = logging.getLogger('netbox.webhooks_worker')


@job('default')
def process_webhook(webhook, data, model_name, event, timestamp, username, request_id):
    """
    Make a POST request to the defined Webhook
    """
    context = {
        'event': dict(ObjectChangeActionChoices)[event].lower(),
        'timestamp': timestamp,
        'model': model_name,
        'username': username,
        'request_id': request_id,
        'data': data
    }

    # Build the headers for the HTTP request
    headers = {
        'Content-Type': webhook.http_content_type,
    }
    try:
        headers.update(webhook.render_headers(context))
    except (TemplateError, ValueError) as e:
        logger.error("Error parsing HTTP headers for webhook {}: {}".format(webhook, e))
        raise e

    # Render the request body
    try:
        body = webhook.render_body(context)
    except TemplateError as e:
        logger.error("Error rendering request body for webhook {}: {}".format(webhook, e))
        raise e

    # Prepare the HTTP request
    params = {
        'method': webhook.http_method,
        'url': webhook.payload_url,
        'headers': headers,
        'data': body.encode('utf8'),
    }
    logger.info(
        "Sending {} request to {} ({} {})".format(
            params['method'], params['url'], context['model'], context['event']
        )
    )
    logger.debug(params)
    try:
        prepared_request = requests.Request(**params).prepare()
    except requests.exceptions.RequestException as e:
        logger.error("Error forming HTTP request: {}".format(e))
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
        logger.info("Request succeeded; response status {}".format(response.status_code))
        return 'Status {} returned, webhook successfully processed.'.format(response.status_code)
    else:
        logger.warning("Request failed; response status {}: {}".format(response.status_code, response.content))
        raise requests.exceptions.RequestException(
            "Status {} returned with content '{}', webhook FAILED to process.".format(
                response.status_code, response.content
            )
        )
