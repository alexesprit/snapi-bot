# version.py

import base64
import hashlib
import os
import platform

identcat = "bot"
identname = "snapi"
identtype = "pc"

appname = "Snapi-Snup"
capsstr = "http://snapi-bot.googlecode.com/caps"

osinfo = platform.uname()
osname = u"%s %s" % (osinfo[0], osinfo[2])

major = "0"
minor = "1"
revision = os.popen("svnversion -n").read()
if not revision:
	revision = "0"
version = u"%s.%s.%s" % (major, minor, revision)
verhash = None

del osinfo
del major
del minor

def updateFeaturesHash(features):
	fString = "<".join(features)
	string = u"%s/%s//%s<%s<" % (identcat, identtype, identname, fString)
	verhash = base64.b64encode(hashlib.sha1(string).digest())
