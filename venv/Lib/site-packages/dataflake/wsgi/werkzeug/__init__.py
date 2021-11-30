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
from werkzeug.debug import DebuggedApplication
from werkzeug.serving import run_simple


def _makeBool(value, default=True):
    """ Helper to make boolean out of a .ini value """
    if default is True:
        if (value or '').lower() in ('off', 'false', '0'):
            return False
    else:
        if (value or '').lower() in ('on', 'true', '1'):
            return True

    return default


def _sanitizeParameters(kw):
    """ Clean up parameters so the server can work with them

    Separates out host/port values and removes them from mapping.

    Separates mapping into two mappings, one for the server and one
    for the debugger.
    """
    debugger_kw = {}
    host = '0.0.0.0'

    if 'hostname' in kw:
        host = kw.pop('hostname')
    elif 'host' in kw:
        host = kw.pop('host')
    port = int(kw.pop('port', '8080'))

    for key in ('use_evalex', 'pin_security', 'pin_logging'):
        # fix up arguments that should be booleans, default True
        if key in kw:
            kw[key] = _makeBool(kw[key], default=True)

    for key in ('use_reloader', 'use_debugger', 'threaded',
                'passthrough_errors', 'evalex', 'show_hidden_frames'):
        # fix up arguments that should be booleans, default False
        if key in kw:
            kw[key] = _makeBool(kw[key], default=False)

    for key in ('reloader_interval', 'processes'):
        # fix up arguments that should be integers
        if key in kw:
            kw[key] = int(kw[key])

    for key in ('evalex', 'request_key', 'console_path', 'console_init_func',
                'show_hidden_frames', 'pin_security', 'pin_logging'):
        if key in kw:
            debugger_kw[key] = kw.pop(key)

    return (host, port, kw, debugger_kw)


def serve_paste(app, global_conf, **kw):
    """ A handler for PasteDeploy-compatible runners.

    Sample minimal .ini configuration:

      [server:main]
      use = egg:dataflake.wsgi.werkzeug#main
      hostname = 127.0.0.1
      port = 8080
    """
    (host, port, server_kw, debugger_kw) = _sanitizeParameters(kw)
    if server_kw.pop('use_debugger', False) is True:
        app = DebuggedApplication(app, **debugger_kw)
    run_simple(host, port, app, **server_kw)
    return 0


def serve_debugger(app, global_conf, **kw):
    """ A handler for PasteDeploy-compatible runners that adds a live debugger

    DO NOT USE THIS IN PRODUCTION! SECURITY RISK!

    Sample minimal .ini configuration:

      [server:main]
      use = egg:dataflake.wsgi.werkzeug#debugger
      hostname = 127.0.0.1
      port = 8080
    """
    (host, port, server_kw, debugger_kw) = _sanitizeParameters(kw)
    debugger_kw['evalex'] = True
    app = DebuggedApplication(app, **debugger_kw)
    run_simple(host, port, app, **server_kw)
    return 0
