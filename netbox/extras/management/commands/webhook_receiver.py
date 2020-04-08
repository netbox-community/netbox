import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

from django.core.management.base import BaseCommand


request_counter = 1


class WebhookHandler(BaseHTTPRequestHandler):
    show_headers = True

    def __getattr__(self, item):

        # Return the same method for any type of HTTP request (GET, POST, etc.)
        if item.startswith('do_'):
            return self.do_ANY

        raise AttributeError

    def log_message(self, format_str, *args):
        global request_counter

        print("[{}] {} {} {}".format(
            request_counter,
            self.date_time_string(),
            self.address_string(),
            format_str % args
        ))

    def do_ANY(self):
        global request_counter

        # Send a 200 response regardless of the request content
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Webhook received!\n')

        request_counter += 1

        # Print the request headers to stdout
        if self.show_headers:
            for k, v in self.headers.items():
                print('{}: {}'.format(k, v))
            print()

        # Print the request body (if any)
        content_length = self.headers.get('Content-Length')
        if content_length is not None:
            body = self.rfile.read(int(content_length))
            print(body.decode('utf-8'))
        else:
            print('(No body)')

        print('------------')


class Command(BaseCommand):
    help = "Start a simple listener to display received HTTP requests"

    default_port = 9000

    def add_arguments(self, parser):
        parser.add_argument(
            '--port', type=int, default=self.default_port,
            help="Optional port number (default: {})".format(self.default_port)
        )
        parser.add_argument(
            "--no-headers", action='store_true', dest='no_headers',
            help="Hide HTTP request headers"
        )

    def handle(self, *args, **options):
        port = options['port']
        quit_command = 'CTRL-BREAK' if sys.platform == 'win32' else 'CONTROL-C'

        WebhookHandler.show_headers = not options['no_headers']

        self.stdout.write('Listening on port http://localhost:{}. Stop with {}.'.format(port, quit_command))
        httpd = HTTPServer(('localhost', port), WebhookHandler)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            self.stdout.write("\nExiting...")
