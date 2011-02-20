# coding: utf-8

# functions.py
# Initial Copyright (с) 2010 -Esprit-

# Различные функции и переменные, необходимые для работы некоторых плагинов

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import urllib
import urllib2

HTML_TAG_RE = re.compile(r"<.+?>")
USERJID_RE = re.compile(r"\w+@\w+\.\w+", re.UNICODE)
SERVER_RE = re.compile(r"\w+\.\w+", re.UNICODE)
URL_RE = re.compile(r"(http|ftp|svn)(\:\/\/[^\s<]+)")

gStanzaID = 0

def getUniqueID(text):
	global gStanzaID
	gStanzaID += 1
	return "%s_%d" % (text, gStanzaID)

getConferences = gConferences.keys

def getMUCSetRoleStanza(conference, user, role, reason=None):
	iq = protocol.Iq(protocol.TYPE_SET)
	iq.setTo(conference)
	query = protocol.Node("query", {"xmlns": protocol.NS_MUC_ADMIN})
	role = query.addChild("item", {"nick": user, "role": role})
	if reason:
		role.setTagData("reason", reason)
	iq.addChild(node=query)
	return iq

def setMUCRole(conference, user, role, reason=None):
	iq = getMUCSetRoleStanza(conference, user, role, reason)
	gClient.send(iq)

def getMUCSetAffiliationStanza(conference, user, itemType, aff, reason=None):
	iq = protocol.Iq(protocol.TYPE_SET)
	iq.setTo(conference)
	query = protocol.Node("query", {"xmlns": protocol.NS_MUC_ADMIN})
	aff = query.addChild("item", {itemType: user, "affiliation": aff})
	if reason:
		aff.setTagData("reason", reason)
	iq.addChild(node=query)
	return iq

def setMUCAffiliation(conference, user, itemType, aff, reason=None):
	iq = getMUCSetAffiliationStanza(conference, user, itemType, aff, reason)
	gClient.send(iq)

def setConferenceStatus(conference, show, status):
	prs = getPresenceNode(show, status, gConfig.PRIORITY)
	prs.setTo(conference)
	gClient.send(prs)

def isJID(jid):
	if USERJID_RE.search(jid):
		return True
	return False

def isServer(server):
	if not server.count(" "):
		if SERVER_RE.search(server):
			return True
	return False

def isConferenceInList(conference):
	return conference in gConferences

def isNickModerator(conference, nick):
	return getNickKey(conference, nick, NICK_ROLE) == protocol.ROLE_MODERATOR

def getUsedMemorySize():
	if os.name == "posix":
		pipe = os.popen("ps -o rss -p %s" % os.getpid())
		pipe.readline()
		return float(pipe.readline().strip()) / 1024
	return 0

def getUptimeStr(time):
	minutes, seconds = divmod(time, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
	timeStr = "%02d:%02d:%02d" % (hours, minutes, seconds)
	if days:
		timeStr = u"%d дн. %s" % (days, timeStr)
	return timeStr

def getTimeStr(time):
	minutes, seconds = divmod(time, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
	timeStr = ""
	if seconds:
		timeStr = u"%d сек." % (seconds)
	if minutes:
		timeStr = u"%d мин. %s" % (minutes, timeStr)
	if hours:
		timeStr = u"%d ч. %s" % (hours, timeStr)
	if days:
		timeStr = u"%d дн. %s" % (days, timeStr)
	return timeStr

def getURL(url, param=None, data=None, headers=None):
	if param:
		query = urllib.urlencode(param)
		url = u"%s?%s" % (url, query)
	if data:
		data = urllib.urlencode(data)
	if headers:
		request = urllib2.Request(url, data, headers)
	else:
		request = urllib2.Request(url, data)
	try:
		return urllib2.urlopen(request)
	except IOError, e:
		printf(u"Unable to open %s (%s)" % (url, e), FLAG_WARNING)
	return None

def decode(text, encoding=None):
	if encoding:
		text = unicode(text, encoding)
	text = HTML_TAG_RE.sub("", text.replace("<br />","\n").replace("<br>","\n"))
	return utils.unescapeHTML(text)

def isURL(url):
	if URL_RE.search(url):
		return True
	return False
