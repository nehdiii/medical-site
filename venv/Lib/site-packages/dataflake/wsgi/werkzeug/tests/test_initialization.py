##############################################################################
#
# Copyright (c) 2019 Jens Vagelpohl and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import unittest


SERVER = {}
DEBUGGER = {}


class FakeDebugger:

    def __init__(self, app, **kw):
        global DEBUGGER
        DEBUGGER.clear()

        DEBUGGER['app'] = app
        DEBUGGER.update(kw)


def fake_run_simple(host, port, app, **kw):
    global SERVER
    SERVER.clear()

    SERVER['app'] = app
    SERVER['host'] = host
    SERVER['port'] = port
    SERVER.update(kw)

    return SERVER


class WerkzeugInitializationTests(unittest.TestCase):

    def test__makeBool(self):
        from dataflake.wsgi.werkzeug import _makeBool

        for value in ('On', 'TRUE', '1'):
            self.assertTrue(_makeBool(value, default=False))

        for value in ('off', 'False', '0'):
            self.assertFalse(_makeBool(value, default=True))

    def test__sanitize_parameters_host_port(self):
        from dataflake.wsgi.werkzeug import _sanitizeParameters
        input_dict = {}
        output = _sanitizeParameters(input_dict)
        self.assertEqual(output, ('0.0.0.0', 8080, {}, {}))

        input_dict = {'host': 'localhost', 'port': '8888'}
        output = _sanitizeParameters(input_dict)
        self.assertEqual(output, ('localhost', 8888, {}, {}))

        input_dict = {'hostname': 'otherhost', 'port': '9999'}
        output = _sanitizeParameters(input_dict)
        self.assertEqual(output, ('otherhost', 9999, {}, {}))

    def test__sanitize_parameters_with_true_defaults(self):
        from dataflake.wsgi.werkzeug import _sanitizeParameters
        input_dict = {'use_evalex': 'on',
                      'pin_security': 'False',
                      'pin_logging': 'off'}
        (host, port, server_kw, debugger_kw) = _sanitizeParameters(input_dict)
        self.assertFalse(debugger_kw['pin_security'])
        self.assertFalse(debugger_kw['pin_logging'])
        self.assertTrue(server_kw['use_evalex'])

    def test__sanitize_parameters_with_false_defaults(self):
        from dataflake.wsgi.werkzeug import _sanitizeParameters
        input_dict = {'use_reloader': '1',
                      'use_debugger': 'On',
                      'threaded': 'true',
                      'passthrough_errors': 'off',
                      'evalex': 'False',
                      'show_hidden_frames': 'on'}
        (host, port, server_kw, debugger_kw) = _sanitizeParameters(input_dict)
        self.assertTrue(server_kw['use_reloader'])
        self.assertTrue(server_kw['use_debugger'])
        self.assertTrue(server_kw['threaded'])
        self.assertFalse(server_kw['passthrough_errors'])
        self.assertFalse(debugger_kw['evalex'])
        self.assertTrue(debugger_kw['show_hidden_frames'])

    def test_serve_paste(self):
        # Install fake serve function first
        from dataflake.wsgi import werkzeug
        old_impl = werkzeug.run_simple
        werkzeug.run_simple = fake_run_simple

        from dataflake.wsgi.werkzeug import serve_paste

        global SERVER

        # The defaults
        serve_paste(None, None)
        self.assertEqual(SERVER['host'], '0.0.0.0')
        self.assertEqual(SERVER['port'], 8080)

        # Set some values
        serve_paste(None, None, host='localhost', port='8888', threaded='on')
        self.assertEqual(SERVER['host'], 'localhost')
        self.assertEqual(SERVER['port'], 8888)
        self.assertEqual(SERVER['threaded'], True)

        # Set some other values
        serve_paste(None, None, hostname='127.0.0.1', port='8888',
                    threaded='on')
        self.assertEqual(SERVER['host'], '127.0.0.1')
        self.assertEqual(SERVER['port'], 8888)
        self.assertEqual(SERVER['threaded'], True)

        # Clean up fake serve function
        werkzeug.run_simple = old_impl

    def test_serve_debugger(self):
        # Install fake serve function first
        from dataflake.wsgi import werkzeug
        old_impl = werkzeug.run_simple
        werkzeug.run_simple = fake_run_simple
        old_debugger = werkzeug.DebuggedApplication
        werkzeug.DebuggedApplication = FakeDebugger

        from dataflake.wsgi.werkzeug import serve_debugger

        global SERVER
        global DEBUGGER

        # The defaults
        serve_debugger(None, None)
        self.assertEqual(SERVER['host'], '0.0.0.0')
        self.assertEqual(SERVER['port'], 8080)
        self.assertEqual(DEBUGGER, {'app': None, 'evalex': True})

        # Set some values
        serve_debugger(None, None, host='localhost', port='8888',
                       threaded='on', show_hidden_frames='1')
        self.assertEqual(SERVER['host'], 'localhost')
        self.assertEqual(SERVER['port'], 8888)
        self.assertEqual(SERVER['threaded'], True)
        self.assertEqual(DEBUGGER, {'app': None, 'evalex': True,
                                    'show_hidden_frames': True})

        # Clean up fake serve function
        werkzeug.run_simple = old_impl
        werkzeug.DebuggedApplication = old_debugger
