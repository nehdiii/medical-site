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
import os
import sys
import unittest


class FakeMkwsgiinstance(object):

    def main(self):
        pass


class ConfigBuilderTests(unittest.TestCase):

    def test_argument_switch(self):
        # Patch a fake object for the mkwsgiinstance import
        from dataflake.wsgi.werkzeug import configurator
        old_impl = configurator.mkwsgiinstance
        configurator.mkwsgiinstance = FakeMkwsgiinstance()

        # Save the "real" sys.argv
        old_args = sys.argv

        # Value passed in, no change
        sys.argv = [None, '-s', 'passed-in']
        configurator.mkzope()
        self.assertEqual(sys.argv, [None, '-s', 'passed-in'])

        # value passwd in, no change
        sys.argv = [None, '--skelsrc=passed-in']
        configurator.mkzope()
        self.assertEqual(sys.argv, [None, '--skelsrc=passed-in'])

        # Value not passed in, now we have a change
        skel_path = os.path.join(os.path.dirname(configurator.__file__),
                                 'skel')
        sys.argv = [None]
        configurator.mkzope()
        self.assertEqual(sys.argv, [None, '-s', skel_path])

        # clean up the patched module variable
        configurator.mkwsgiinstance = old_impl

        # Restore sys.argv
        sys.argv = old_args
