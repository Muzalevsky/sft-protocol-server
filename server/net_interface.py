#!/usr/bin/python3 -u
import http.server
import logging
import sys
from urllib.parse import parse_qs
from utils import Order_Status, get_log_path


class Handler(http.server.BaseHTTPRequestHandler):
    def __init__(self, pipe_conn, buffer, *args):
        self.pipe_conn = pipe_conn
        self.buffer = buffer
        http.server.BaseHTTPRequestHandler.__init__(self, *args)

    def do_POST(self):
        try:
            # trying to get payload
            logging.debug('Got POST-request')
            length = int(self.headers['Content-Length'])
            logging.debug('Got length')
            orderId = int(self.headers['protocolId'])
            logging.debug('Got protocolId')
            payload = self.rfile.read(length)
            logging.debug('Got payload')
            self.buffer.push(orderId, payload)
            logging.debug('Got push')
            self.send_response(200, "Got payload")
            self.end_headers()
            self.wfile.write('Accepted'.encode())

        except Exception as exc:
            try:
                self.bad_request(400, exc)
            except Exception as exc:
                logging.debug(f"Bad connection with client {exc}")

    def bad_request(self, code, exc=""):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write('<html><head><meta charset="utf-8">'.encode())
        self.wfile.write('<title>Simple title</title></head>'.encode())
        self.wfile.write(f'<body><p>Bad request: {code} {exc}</p></body></html>'.encode())
        logging.debug('requested')

    def clear_pipe(self):
        while True:
            logging.debug('clear pipe start')
            if self.pipe_conn.poll():
                self.pipe_conn.recv()
                continue
            logging.debug('clear pipe finish')
            break

    def do_GET(self):
        try:
            #analyzing agent
            try:
                if 'friction_tester' in dict(self.headers)['agent']:
                    logging.debug('Agent: friction_tester')
                    friction_tester_agent = True
            except:
                logging.debug('Agent: Browser')
                friction_tester_agent = False

            # analyzing of parameters
            fields = parse_qs(self.path)
            logging.debug(f"I've got a GET request, fields = {fields}")

            if 'protocolId' in fields:
                # asking scheduler about status of order
                protocolId = int(fields['protocolId'][0])
                self.clear_pipe()
                self.pipe_conn.send((1, protocolId))

                # obtaining id from scheduler
                if self.pipe_conn.poll(2):
                    status = self.pipe_conn.recv()
                    if status == Order_Status.READY:
                        output_data, img_format = self.buffer.pop_by_id(protocolId)
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(output_data)
                    elif status == Order_Status.ERROR:
                        self.bad_request(500)
                    elif status == Order_Status.UNKNOWN:
                        self.bad_request(400)
                    else:
                        logging.debug('return 202')
                        self.bad_request(202)
                else:
                    self.bad_request(408)

        except Exception as exc:
            logging.debug("Error! {0}".format(exc))
            self.bad_request(520, exc)


class Net_Interface():
    def __init__(self, host, port):
        self.port = port
        self.host = host
        self.init_logging()

    def init_logging(self):
        log_path = get_log_path()
        if log_path is None:
            logging.debug("Could not find SFT_ROOT environment variable")
            sys.exit(1)

        log_path += '/server.log'
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename=log_path, encoding='utf-8', level=logging.DEBUG)

    def start_server(self, pipe_conn, buffer):
        def handler(*args):
            Handler(pipe_conn, buffer, *args)

        self.net_server = http.server.HTTPServer((self.host, self.port), handler)
        logging.debug('net_server Started')
        self.net_server.serve_forever()
