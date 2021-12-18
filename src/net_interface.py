#!/usr/bin/python3 -u
import http.server
import logging
from urllib.parse import parse_qs


class Handler(http.server.BaseHTTPRequestHandler):
    def __init__(self, buffer, *args):
        self.buffer = buffer
        self._logger = logging.getLogger()
        http.server.BaseHTTPRequestHandler.__init__(self, *args)

    def do_POST(self):
        try:
            # trying to get payload
            self._logger.debug('Got POST-request')
            length = int(self.headers['Content-Length'])
            self._logger.debug('Got length')
            protocolId = int(self.headers['protocolId'])
            self._logger.debug(f"Got protocolId={protocolId}")
            payload = self.rfile.read(length)
            self._logger.debug('Got payload')
            self.buffer.push(protocolId, payload)
            self._logger.debug('Got push')
            self.send_response(200, "Got payload")
            self.end_headers()
            self.wfile.write('Accepted'.encode())

        except Exception as exc:
            try:
                self.bad_request(400, exc)
            except Exception as exc:
                self._logger.debug(f"Bad connection with client {exc}")

    def bad_request(self, code, exc=""):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write('<html><head><meta charset="utf-8">'.encode())
        self.wfile.write('<title>Simple title</title></head>'.encode())
        self.wfile.write(f'<body><p>Bad request: {code} {exc}</p></body></html>'.encode())
        self._logger.debug('requested')

    def do_GET(self):
        try:
            try:
                if 'friction_tester' in dict(self.headers)['agent']:
                    self._logger.debug('Agent: friction_tester')
                    friction_tester_agent = True
            except:
                self._logger.debug('Agent: Browser')
                friction_tester_agent = False

            # analyzing of parameters
            fields = parse_qs(self.path)
            self._logger.debug(f"I've got a GET request, fields = {fields}")

            if 'protocolId' in fields:
                # asking scheduler about status of order
                protocolId = int(fields['protocolId'][0])
                output_data = self.buffer.pop_by_id(protocolId)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(output_data)
            else:
                self.bad_request(408)
        except Exception as exc:
            self._logger.debug("Error! {0}".format(exc))
            self.bad_request(520, exc)


class Net_Interface:
    def __init__(self, host, port):
        self.port = port
        self.host = host
        self._logger = logging.getLogger(self.__class__.__name__)

    def start_server(self, buffer):
        def handler(*args):
            Handler(buffer, *args)

        self.net_server = http.server.HTTPServer((self.host, self.port), handler)
        self._logger.debug('net_server Started')
        self.net_server.serve_forever()
