import hashlib
import hmac

import requests
from django_rq import job

from extras.constants import WEBHOOK_CT_JSON, WEBHOOK_CT_X_WWW_FORM_ENCODED


@job('default')
def process_webhook(webhook, data, model_class, event, timestamp):
    """
    Make a POST request to the defined Webhook
    """
    payload = {
        'event': event,
        'timestamp': timestamp,
        'model': model_class.__name__,
        'data': data
    }
    headers = {
        'Content-Type': webhook.get_http_content_type_display(),
    }
    params = {
        'method': 'POST',
        'url': webhook.payload_url,
        'headers': headers
    }

    if webhook.http_content_type == WEBHOOK_CT_JSON:
        params.update({'json': payload})
    elif webhook.http_content_type == WEBHOOK_CT_X_WWW_FORM_ENCODED:
        params.update({'data': payload})

    prepared_request = requests.Request(**params).prepare()

    if webhook.secret != '':
        # sign the request with the secret
        hmac_prep = hmac.new(bytearray(webhook.secret, 'utf8'), prepared_request.body, digestmod=hashlib.sha512)
        prepared_request.headers['X-Hook-Signature'] = hmac_prep.hexdigest()

    with requests.Session() as session:
        session.verify = webhook.ssl_verification
        response = session.send(prepared_request)

    if response.status_code >= 200 and response.status_code <= 299:
        return 'Status {} returned, webhook successfully processed.'.format(response.status_code)
    else:
        raise requests.exceptions.RequestException(
            "Status {} returned, webhook FAILED to process.".format(response.status_code)
        )
