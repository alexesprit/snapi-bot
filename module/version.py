# version.py

import base64
import hashlib
import os
import platform

from module.xmpp import protocol

MAJOR = "0"
MINOR = "1"

BOT_FEATURES = (
	protocol.NS_ACTIVITY,
	protocol.NS_DISCO_INFO,
	protocol.NS_DISCO_ITEMS,
	protocol.NS_MOOD,
	protocol.NS_MUC,
	protocol.NS_VERSION,
	protocol.NS_PING,
	protocol.NS_RECEIPTS,
	protocol.NS_ENTITY_TIME,
	protocol.NS_VCARD
)

identcat = "bot"
identname = "snapi"
identtype = "pc"

appname = "Snapi-Snup"
caps = "http://snapi-bot.googlecode.com/caps"

osinfo = platform.uname()
osname = u"%s %s" % (osinfo[0], osinfo[2])

revision = os.popen("svnversion -n").read()
if not revision:
	revision = "0"
version = u"%s.%s.%s" % (MAJOR, MINOR, revision)

features = "<".join(BOT_FEATURES)
string = u"%s/%s//%s<%s<" % (identcat, identtype, identname, features)
verhash = base64.b64encode(hashlib.sha1(string).digest())

del features
del string
del osinfo
del MAJOR
del MINOR

