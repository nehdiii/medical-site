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

from Zope2.utilities import mkwsgiinstance


def mkzope():
    """ Create a WSGI configuration for Zope and werkzeug """
    # We want to override the source of the skeleton files.
    # Make sure they are not already passed in.
    already_set = False

    for arg in sys.argv[1:]:
        if arg in ('-s', '--skelsrc') or arg.startswith('--skelsrc'):
            already_set = True
            break

    if not already_set:
        # Only go into action of the skeleton source has not been passed in.
        skelsrc = os.path.join(os.path.dirname(__file__), 'skel')
        sys.argv.extend(['-s', skelsrc])

    return mkwsgiinstance.main()
