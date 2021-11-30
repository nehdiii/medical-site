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
import ipaddress
import logging


def _startsWithIP(msg):
    """ Check if the first element of the logged message is an IP address

    Args:
        msg (str): The logged message string

    Returns:
        Boolean True or False
    """
    if not msg:
        return False

    first_element = msg.split(' ', 1)[0]
    try:
        if isinstance(first_element, bytes):
            first_element = first_element.decode('UTF-8')
        ipaddress.ip_address(first_element)
        return True
    except ValueError:
        pass

    return False


class AccessLogFilter(logging.Filter):
    """ Filter that only lets "real" access log entries through """

    def filter(self, record):
        if _startsWithIP(record.msg):
            return True
        return False


class EventLogFilter(logging.Filter):
    """ Filter that holds back access log entries """

    def filter(self, record):
        if not _startsWithIP(record.msg):
            return True
        return False


class AccessLogHandler(logging.FileHandler):

    def __init__(self, *args, **kw):
        super(AccessLogHandler, self).__init__(*args, **kw)
        self.addFilter(AccessLogFilter())


class EventLogHandler(logging.FileHandler):

    def __init__(self, *args, **kw):
        super(EventLogHandler, self).__init__(*args, **kw)
        self.addFilter(EventLogFilter())


class ConsoleHandler(logging.StreamHandler):

    def __init__(self, *args, **kw):
        super(ConsoleHandler, self).__init__(*args, **kw)
        self.addFilter(EventLogFilter())
