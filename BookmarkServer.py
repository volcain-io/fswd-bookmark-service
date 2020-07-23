#!/usr/bin/env python3
#
# A *bookmark server* or URI shortener that maintains a mapping (dictionary)
# between short names and long URIs, checking that each new URI added to the
# mapping actually works (i.e. returns a 200 OK).
#
# This server is intended to serve three kinds of requests:
#
#   * A GET request to the / (root) path.  The server returns a form allowing
#     the user to submit a new name/URI pairing.  The form also includes a
#     listing of all the known pairings.
#   * A POST request containing "long_uri" and "short_name" fields.  The server
#     checks that the URI is valid (by requesting it), and if so, stores the
#     mapping from short_name to long_uri in its dictionary.  The server then
#     redirects back to the root path.
#   * A GET request whose path contains a short name.  The server looks up
#     that short name in its dictionary and redirects to the corresponding
#     long URI.

import os
import http.server
import requests
from urllib.parse import unquote, parse_qs
# import threading
from socketserver import ThreadingMixIn

memory = {}

form = '''<!DOCTYPE html>
<title>Bookmark Server</title>
<form method="POST">
    <label>Long URI:
        <input name="long_uri">
    </label>
    <br>
    <label>Short name:
        <input name="short_name">
    </label>
    <br>
    <button type="submit">Save it!</button>
</form>
<p>URIs I know about:
<pre>
{}
</pre>
'''


def check_uri(uri, timeout=5):
    # check URI and return True if the URI could be successfully fetched
    try:
        r = requests.get(uri, timeout=timeout)
        return r.status_code == requests.codes.ok
    except (requests.exceptions.RequestException):
        # and False if not
        return False


class url_shortener(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # A GET request will either be for / (the root path) or for /some-name.
        # Strip off the / and we have either empty string or a name.
        name = unquote(self.path[1:])

        if name:
            if name in memory:
                # Send a 303 redirect to the long URI in memory[name].
                self.send_response(303)
                self.send_header('Location', memory[name])
                self.end_headers()
            else:
                # We don't know that name! Send a 404 error.
                self.send_response(404)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write("I don't know '{}'.".format(name).encode())
        else:
            # Root path. Send the form.
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # List the known associations in the form.
            known = "\n".join("{} : {}".format(key, memory[key])
                              for key in sorted(memory.keys()))
            self.wfile.write(form.format(known).encode())

    def do_POST(self):
        # Decode the form data.
        length = int(self.headers.get('Content-length', 0))
        body = self.rfile.read(length).decode()
        params = parse_qs(body)

        # Check that the user submitted the form fields.
        if "long_uri" not in params or "short_name" not in params:
            # Serve a 400 error with a useful message.
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('All fields are mandatory'.encode())

        long_uri = params["long_uri"][0]
        short_name = params["short_name"][0]

        if check_uri(long_uri):
            # This URI is good!  Remember it under the specified name.
            memory[short_name] = long_uri

            # Serve a redirect to the root page (the form).
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            # Didn't successfully fetch the long URI.
            # Send a 404 error with a useful message.
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile().write(
                'URI couldn\'t be found: {}'.format(long_uri).encode())


class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    """This is an HTTPServer that supports thread-based concurrency."""


if __name__ == '__main__':
    # Use PORT if it's there
    port = int(os.environ.get('PORT', 8000))
    server_address = ('', port)
    httpd = ThreadHTTPServer(server_address, url_shortener)
    httpd.serve_forever()
