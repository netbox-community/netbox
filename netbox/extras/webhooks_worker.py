import json
import logging

import requests
from django_rq import job
from jinja2.exceptions import TemplateError
from rest_framework.utils.encoders import JSONEncoder

from utilities.utils import render_jinja2
from .choices import ObjectChangeActionChoices
from .constants import HTTP_CONTENT_TYPE_JSON
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

    # Build HTTP headers
    headers = {
        'Content-Type': webhook.http_content_type,
    }
    if webhook.additional_headers:
        headers.update(webhook.additional_headers)

    params = {
        'method': 'POST',
        'url': webhook.payload_url,
        'headers': headers
    }

    logger.info(
        "Sending webhook to {}: {} {}".format(params['url'], context['model'], context['event'])
    )

    # Construct the request body. If a template has been defined, use it. Otherwise, dump the context as either JSON
    # or form data.
    if webhook.body_template:
        try:
            params['data'] = render_jinja2(webhook.body_template, context)
        except TemplateError as e:
            logger.error("Error rendering request body: {}".format(e))
            return
    elif webhook.http_content_type == HTTP_CONTENT_TYPE_JSON:
        params['data'] = json.dumps(context, cls=JSONEncoder)
    else:
        params['data'] = context

    prepared_request = requests.Request(**params).prepare()

    if webhook.secret != '':
        # Sign the request with a hash of the secret key and its content.
        prepared_request.headers['X-Hook-Signature'] = generate_signature(prepared_request.body, webhook.secret)

    with requests.Session() as session:
        session.verify = webhook.ssl_verification
        if webhook.ca_file_path:
            session.verify = webhook.ca_file_path
        response = session.send(prepared_request)

    logger.debug(params)

    if 200 <= response.status_code <= 299:
        logger.info("Request succeeded; response status {}".format(response.status_code))
        return 'Status {} returned, webhook successfully processed.'.format(response.status_code)
    else:
        logger.error("Request failed; response status {}: {}".format(response.status_code, response.content))
        raise requests.exceptions.RequestException(
            "Status {} returned with content '{}', webhook FAILED to process.".format(
                response.status_code, response.content
            )
        )
