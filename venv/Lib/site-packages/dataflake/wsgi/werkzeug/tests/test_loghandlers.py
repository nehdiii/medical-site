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


IPv6 = '2001:4800:1be1:500:2bd2:ef:d1ed:df14'
IPv4 = '72.32.182.192'


class FakeRecord(object):

    def __init__(self, msg):
        setattr(self, 'msg', msg)


class LogHandlerTests(unittest.TestCase):

    def test__startsWithIp(self):
        from dataflake.wsgi.werkzeug.loghandlers import _startsWithIP

        self.assertTrue(_startsWithIP('::1 Message'))
        self.assertTrue(_startsWithIP('127.0.0.1 Message'))
        self.assertTrue(_startsWithIP('%s Message' % IPv4))
        self.assertTrue(_startsWithIP('%s Message' % IPv6))
        self.assertFalse(_startsWithIP(' * Message'))
        self.assertFalse(_startsWithIP(None))
        self.assertFalse(_startsWithIP(''))

    def test_AccessLogFilter(self):
        from dataflake.wsgi.werkzeug.loghandlers import AccessLogFilter
        fltr = AccessLogFilter()

        self.assertTrue(fltr.filter(FakeRecord('::1 Message')))
        self.assertTrue(fltr.filter(FakeRecord('127.0.0.1 Message')))
        self.assertTrue(fltr.filter(FakeRecord('%s Message' % IPv4)))
        self.assertTrue(fltr.filter(FakeRecord('%s Message' % IPv6)))
        self.assertFalse(fltr.filter(FakeRecord(' * Message')))
        self.assertFalse(fltr.filter(FakeRecord(None)))
        self.assertFalse(fltr.filter(FakeRecord('')))

    def test_EventLogFilter(self):
        from dataflake.wsgi.werkzeug.loghandlers import EventLogFilter
        fltr = EventLogFilter()

        self.assertFalse(fltr.filter(FakeRecord('::1 Message')))
        self.assertFalse(fltr.filter(FakeRecord('127.0.0.1 Message')))
        self.assertFalse(fltr.filter(FakeRecord('%s Message' % IPv4)))
        self.assertFalse(fltr.filter(FakeRecord('%s Message' % IPv6)))
        self.assertTrue(fltr.filter(FakeRecord(' * Message')))
        self.assertTrue(fltr.filter(FakeRecord(None)))
        self.assertTrue(fltr.filter(FakeRecord('')))
