{!models/extras/webhook.md!}

## Webhook Processing

When a change is detected, any resulting webhooks are placed into a Redis queue for processing. This allows the user's request to complete without needing to wait for the outgoing webhook(s) to be processed. The webhooks are then extracted from the queue by the `rqworker` process and HTTP requests are sent to their respective destinations. The current webhook queue and any failed webhooks can be inspected in the admin UI under System > Background Tasks.

A request is considered successful if the response has a 2XX status code; otherwise, the request is marked as having failed. Failed requests may be retried manually via the admin UI.

## Troubleshooting

To assist with verifying that the content of outgoing webhooks is rendered correctly, NetBox provides a simple HTTP listener that can be run locally to receive and display webhook requests. First, modify the target URL of the desired webhook to `http://localhost:9000/`. This will instruct NetBox to send the request to the local server on TCP port 9000. Then, start the webhook receiver service from the NetBox root directory:

```no-highlight
$ python netbox/manage.py webhook_receiver
Listening on port http://localhost:9000. Stop with CONTROL-C.
```

You can test the receiver itself by sending any HTTP request to it. For example:

```no-highlight
$ curl -X POST http://localhost:9000 --data '{"foo": "bar"}'
```

The server will print output similar to the following:

```no-highlight
[1] Tue, 07 Apr 2020 17:44:02 GMT 127.0.0.1 "POST / HTTP/1.1" 200 -
Host: localhost:9000
User-Agent: curl/7.58.0
Accept: */*
Content-Length: 14
Content-Type: application/x-www-form-urlencoded

{"foo": "bar"}
------------
```

Note that `webhook_receiver` does not actually _do_ anything with the information received: It merely prints the request headers and body for inspection.

Now, when the NetBox webhook is triggered and processed, you should see its headers and content appear in the terminal where the webhook receiver is listening. If you don't, check that the `rqworker` process is running and that webhook events are being placed into the queue (visible under the NetBox admin UI).
