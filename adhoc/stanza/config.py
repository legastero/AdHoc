"""
    Adhoc: A command-line XMPP ad-hoc command runner.
    Copyright (C) 2011 Lance Stout
    This file is part of Adhoc.

    See the file LICENSE for copying permission.
"""

import sleekxmpp
from sleekxmpp.xmlstream import ElementBase, ET, register_stanza_plugin


class Config(ElementBase):

    name = 'config'
    namespace = 'adhoc:config'
    interfaces = set(('jid', 'password'))
    sub_interfaces = interfaces
