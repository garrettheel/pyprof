import logging
import os
import pstats
import StringIO

import gevent
from gevent import pywsgi, Greenlet

import greenlet
import yappi


logger = logging.getLogger('pyprof')


_server = None
_profiling = False


TEMPLATE = """
<html>
<body>
<pre>
{}
</pre>
</body>
</html>
"""


def start(host=None, port=6060):
    global _server
    if not _server:
        host = host or ''
        _server = pywsgi.WSGIServer((host, port), handler)
        server_greenlet = Greenlet.spawn(_server.serve_forever)

    start_profiling()


def start_profiling(use_gevent=True):
    global _profiling
    if _profiling:
        return

    logger.info('Starting profiling. pid=%s', os.getpid())

    _profiling = True
    yappi.set_clock_type('cpu')
    if use_gevent:
        yappi.set_context_id_callback(lambda: id(greenlet.getcurrent()))
        yappi.set_context_name_callback(lambda: greenlet.getcurrent().__class__.__name__)
    yappi.start(builtins=True, profile_threads=False)


def handler(env, start_response):
    path = env['PATH_INFO']
    method = env['REQUEST_METHOD']

    if path == '/':
        # TODO: redirect to /pyprof
        return handle_profile(env, start_response)
    elif path == '/pyprof':
        return handle_profile(env, start_response)
    elif path == '/clear' and method == 'POST':
        yappi.clear_stats()
        start_response('204 NO CONTENT', [])
        return []
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<h1>Not Found</h1>']


def handle_profile(env, start_response):
    ps = yappi.convert2pstats(yappi.get_func_stats())

    s = StringIO.StringIO()
    ps.stream = s
    ps.sort_stats('cumulative')
    ps.print_stats()

    stats = TEMPLATE.format(s.getvalue())

    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b"{}".format(stats)]
