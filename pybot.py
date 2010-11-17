#!/usr/bin/python
# coding: utf-8

# pybot.py
# Initial Copyright (c) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>
# Modification Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2010 -Esprit-
# Part of code Copyright (c) Boris Kotov <admin@avoozl.ru>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from __future__ import with_statement

import codecs
import math
import os
import random
import re
import sys
import threading
import time
import traceback
import urllib

import chardet
import database
import macros
import simplejson

from xmpp import client, debug, protocol, simplexml
from utils import utils

CSS_DIR = "css"
CONFIG_DIR = "config"
PLUGIN_DIR = "plugins"
SYSLOG_DIR = "syslogs"
RESOURCE_DIR = "resource"

PID_FILE = "pid.txt"
BOTCONFIG_FILE = "config.py"

ACCESS_FILE = "access.txt"
CONFIG_FILE = "config.txt"
CONF_FILE = "conferences.txt"
LOG_ERROR_FILE = "%Y.%m.%d_error.txt"
LOG_CRASH_FILE = "%Y.%m.%d_crash.txt"
LOG_WARN_FILE = "%Y.%m.%d_warn.txt"

FLAG_INFO = "info"
FLAG_ERROR = "error"
FLAG_WARNING = "warning"
FLAG_SUCCESS = "success"

ADDCONF = 0x1
DELCONF = 0x2
STARTUP = 0x3
INIT_2 = 0x4
SHUTDOWN = 0x5

CHAT = 1 << 1
ROSTER = 1 << 2
FROZEN = 1 << 3
NONPARAM = 1 << 4
PARAM = 1 << 5
ANY = CHAT | ROSTER

NICK_JID = "jid"
NICK_IDLE = "idle"
NICK_HERE = "here"
NICK_MODER = "moder"
NICK_JOINED = "joined"
NICK_SHOW = "show"
NICK_STATUS = "status"

STATUS_STRINGS = (
	protocol.PRS_AWAY, 
	protocol.PRS_NA, 
	protocol.PRS_DND, 
	protocol.PRS_CHAT
)

ROLES = {
	protocol.ROLE_NONE: 0, 
	protocol.ROLE_VISITOR: 0, 
	protocol.ROLE_PARTICIPANT: 10, 
	protocol.ROLE_MODERATOR: 15
}

AFFILIATIONS = {
	protocol.AFF_OUTCAST: 0, 
	protocol.AFF_NONE: 0, 
	protocol.AFF_MEMBER: 1, 
	protocol.AFF_ADMIN: 5, 
	protocol.AFF_OWNER: 15
}

FORBIDDEN_TYPES = (
	protocol.TYPE_NORMAL,
	protocol.TYPE_HEADLINE
)

LOG_CRASH = 0x1
LOG_ERROR = 0x2
LOG_WARN = 0x3

LOG_TYPES = {
	LOG_CRASH: LOG_CRASH_FILE, 
	LOG_ERROR: LOG_ERROR_FILE, 
	LOG_WARN: LOG_WARN_FILE
}

REJOIN_DELAY = 120
RECONNECT_DELAY = 15
RESTART_DELAY = 5

CMD_DESC = 0x1
CMD_ACCESS = 0x2
CMD_SYNTAX = 0x3
CMD_EXAMPLE = 0x4
CMD_TYPE = 0x5

gCurrentDir = os.path.dirname(sys.argv[0])
if gCurrentDir:
	os.chdir(gCurrentDir)
execfile(BOTCONFIG_FILE) in globals()

gUserName, gServer = gJid.split("@")
gClient = client.Client(server=gServer, port=gPort, debugFlags=gXMPPDebug)
gRoster = None
gDebug = debug.Debug(gCoreDebug, showFlags=False)
gTagPtrn = re.compile(r"<.+?>")
gJidPtrn = re.compile(r"\w+@\w+\.\w+", re.UNICODE)
gSrvPtrn = re.compile(r"\w+\.\w+", re.UNICODE)
gURLPtrn = re.compile(r"(http|ftp|svn)(\:\/\/[^\s<]+)")

gSemaphore = threading.BoundedSemaphore(30)

gInfo = {"msg": 0, "prs": 0, "iq": 0, "cmd": 0, "thr": 0, "err": 0, "tmr": 0, "warn": 0}
gVersion = ("Jimm", "0.6.4v [06.07.2010]", "NokiaE51-1/0.34.011")

gBotMsgHandlers = []
gJoinHandlers = []
gLeaveHandlers = []
gIqHandlers = []
gCmdHandlers = {}

gEventHandlers = {
	ADDCONF: [], 
	DELCONF: [], 
	STARTUP: [], 
	INIT_2: [], 
	SHUTDOWN: []
}
gPresenceHandlers = {ROSTER: [], CHAT: []}
gMessageHandlers = {ROSTER: [], CHAT: []}

gGlobalAccess = {}
gTempAccess = {}
gPermAccess = {}

gCommands = {}
gCmdOff = {}
gMacros = macros.Macros(CONFIG_DIR)

gConferenceConfig = {}
gConferences = {}
gIsJoined = {}

gJokes = []

gID = 0

gDebug.colors[FLAG_ERROR] = debug.colorBrightRed
gDebug.colors[FLAG_WARNING] = debug.colorYellow
gDebug.colors[FLAG_SUCCESS] = debug.colorBrightCyan

def clearEventHandlers(evtType):
	gEventHandlers[evtType] = []

def registerMessageHandler(function, msgType):
	gMessageHandlers[msgType].append(function)
	
def registerBotMessageHandler(function):
	gBotMsgHandlers.append(function)

def registerJoinHandler(function):
	gJoinHandlers.append(function)

def registerLeaveHandler(function):
	gLeaveHandlers.append(function)

def registerIqHandler(function):
	gIqHandlers.append(function)

def registerPresenceHandler(function, prsType):
	gPresenceHandlers[prsType].append(function)

def registerEvent(function, evtType):
	gEventHandlers[evtType].append(function)

def registerCommand(function, command, access, desc, syntax, examples, cmdType=ANY):
	gCmdHandlers[command] = function
	gCommands[command] = {CMD_ACCESS: access, CMD_DESC: desc, CMD_SYNTAX: syntax, CMD_EXAMPLE: examples, CMD_TYPE: cmdType}

def callBotMessageHandlers(msgType, jid, text):
	for function in gBotMsgHandlers:
		startThread(function, (msgType, jid, text))

def callJoinHandlers(conference, nick, trueJid, aff, role):
	for function in gJoinHandlers:
		startThread(function, (conference, nick, trueJid, aff, role))

def callLeaveHandlers(conference, nick, trueJid, reason, code):
	for function in gLeaveHandlers:
		startThread(function, (conference, nick, trueJid, reason, code))

def callMessageHandlers(msgType, stanza, evtType, conference, nick, trueJid, body):
	gInfo["msg"] += 1
	for function in gMessageHandlers[evtType]:
		startThread(function, (stanza, msgType, conference, nick, trueJid, body))

def callIqHandlers(stanza, jid, resource):
	gInfo["iq"] += 1
	for function in gIqHandlers:
		startThread(function, (stanza, jid, resource))

def callPresenceHandlers(stanza, prsType, jid, resource, trueJid):
	gInfo["prs"] += 1
	for function in gPresenceHandlers[prsType]:
		startThread(function, (stanza, jid, resource, trueJid))

def callEventHandlers(evtType, args=None):
	if args:
		for function in gEventHandlers[evtType]:
			function(*args)
	else:
		for function in gEventHandlers[evtType]:
			function()

def callCommandHandlers(command, cmdType, jid, resource, param):
	gInfo["cmd"] += 1
	if command in gCmdHandlers:
		startThread(gCmdHandlers[command], (cmdType, jid, resource, param))

def startThread(function, args=None):
	gInfo["thr"] += 1
	threading.Thread(None, execute, function.__name__, (function, args)).start()

def startTimer(timeout, function, args=None):
	gInfo["tmr"] += 1
	timer = threading.Timer(timeout, execute, (function, args))
	timer.setName(function.__name__)
	timer.start()
	return timer

def execute(function, args=None):
	try:
		if args:
			with gSemaphore:
				function(*args)
		else:
			with gSemaphore:
				function()
	except Exception:
		printf("Exception in %s function" % (function.__name__), FLAG_ERROR)
		writeToLog(traceback.format_exc(), LOG_ERROR)

def getUsedMemorySize():
	if os.name == "posix":
		pipe = os.popen("ps -o rss -p %s" % os.getpid())
		pipe.readline()
		return float(pipe.readline().strip()) / 1024
	return 0

def printf(text, flag = FLAG_INFO):
	gDebug.show(text, flag, flag)

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

getFilePath = os.path.join

def getConfigPath(*param):
	return os.path.join(CONFIG_DIR, *param)

def getURL(url, param=None):
	if param:
		query = urllib.urlencode(param)
		url = u"%s?%s" % (url, query)
	try:
		return urllib.urlopen(url)
	except (IOError), e:
		text = u"Unable to open %s (%s)" % (url, e)
		printf(text, FLAG_WARNING)
		writeToLog(text, LOG_WARN)
	return None

def openURL(url, param=None):
	responce = getURL(url, param)
	if responce:
		return responce.read()
	return None

def decode(text, encoding=None):
	if encoding:
		text = unicode(text, encoding)
	text = gTagPtrn.sub("", text.replace("<br />","\n").replace("<br>","\n"))
	return utils.unescapeHTML(text)

def saveConferences():
	utils.writeFile(getConfigPath(CONF_FILE), str(gConferences.keys()))

def loadConferenceConfig(conference):
	path = getConfigPath(conference, CONFIG_FILE)
	utils.createFile(path, "{}")
	gConferenceConfig[conference] = eval(utils.readFile(path))

def saveConferenceConfig(conference):
	path = getConfigPath(conference, CONFIG_FILE)
	utils.writeFile(path, str(gConferenceConfig[conference]))

def getConferenceConfigKey(conference, key):
	return gConferenceConfig[conference].get(key)

def setConferenceConfigKey(conference, key, value):
	gConferenceConfig[conference][key] = value

def addConference(conference):
	gConferences[conference] = {}
	gIsJoined[conference] = False
	loadConferenceConfig(conference)
	for function in gEventHandlers[ADDCONF]:
		function(conference)

def delConference(conference):
	for function in gEventHandlers[DELCONF]:
		function(conference)
	del gIsJoined[conference]
	del gConferenceConfig[conference]
	del gConferences[conference]

def joinConference(conference, nick, password):
	setConferenceConfigKey(conference, "nick", nick)
	setConferenceConfigKey(conference, "password", password)
	prs = protocol.Presence("%s/%s" % (conference, nick), priority=gPriority)
	status = getConferenceConfigKey(conference, "status")
	show = getConferenceConfigKey(conference, "show")
	if status:
		prs.setStatus(status)
	if show:
		prs.setShow(show)
	prs.addChild(node=gClient.getCapsNode())
	mucTag = prs.setTag("x", namespace=protocol.NS_MUC)
	mucTag.addChild("history", {"maxchars": "0"})
	if password:
		mucTag.setTagData("password", password)
	gClient.send(prs)

def leaveConference(conference, status=None):
	prs = protocol.Presence(conference, protocol.PRS_OFFLINE)
	if status:
		prs.setStatus(status)
	gClient.send(prs)
	delConference(conference)

def getBotNick(conference):
	if conference in gConferences:
		return getConferenceConfigKey(conference, "nick") or gBotNick
	return gBotNick

def getUniqueID(text):
	global gID
	gID += 1
	return "%s_%d" % (text, gID)

def setConferenceStatus(conference, status, show):
	prs = protocol.Presence(conference, priority=gPriority)
	if status:
		prs.setStatus(status)
	if show:
		prs.setShow(show)
	prs.addChild(node=gClient.getCapsNode())
	gClient.send(prs)

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

def isJid(jid):
	if not jid.count(" "):
		if gJidPtrn.search(jid):
			return True
	return False

def isServer(server):
	if not server.count(" "):
		if gSrvPtrn.search(server):
			return True	
	return False

def isAdmin(jid):
	return jid in gAdmins

def isCommand(command):
	return command in gCommands

def isCommandType(command, cmdType):
	return gCommands[command][CMD_TYPE] & cmdType

def isAvailableCommand(conference, command):
	return not(conference in gCmdOff and command in gCmdOff[conference])

def getNicks(conference):
	return gConferences[conference].keys()

def getOnlineNicks(conference):
	return [x for x in gConferences[conference] if getNickKey(conference, x, NICK_HERE)]

def getJidList(conference, offline=False):
	nicks = offline and getNicks(conference) or getOnlineNicks(conference)
	jidList = tuple(set([getTrueJid(conference,  nick) for nick in nicks]))
	return jidList
	
def getTrueJid(jid, resource=None):
	if isinstance(jid, protocol.UserJid):
		jid = unicode(jid)
	if not resource:
		if jid.find("/") > -1:
			jid, resource = jid.split("/", 1)
	if jid in gConferences:
		if nickInConference(jid, resource):
			jid = getNickKey(jid, resource, NICK_JID)
	return jid

def getNickByJid(conference, trueJid, offline=False):
	nicks = offline and getNicks(conference) or getOnlineNicks(conference)
	for nick in nicks:
		if getNickKey(conference, nick, NICK_JID) == trueJid:
			return nick
	return None

def getConferences():
	return gConferences.keys()

def getNickKey(conference, nick, key):
	return gConferences[conference][nick].get(key)

def setNickKey(conference, nick, key, value):
	gConferences[conference][nick][key] = value

def conferenceInList(conference):
	return conference in gConferences

def nickInConference(conference, nick):
	return nick in gConferences[conference]

def nickIsOnline(conference, nick):
	return nickInConference(conference, nick) and getNickKey(conference, nick, NICK_HERE)

def setTempAccess(conference, jid, level=0):
	gTempAccess[conference][jid] = None
	if level:
		gTempAccess[conference][jid] = level
	else:
		del gTempAccess[conference][jid]

def setPermAccess(conference, jid, level=0):
	gPermAccess[conference][jid] = None
	if level:
		gPermAccess[conference][jid] = level
	else:
		del gPermAccess[conference][jid]
	path = getConfigPath(conference, ACCESS_FILE)
	utils.writeFile(path, str(gPermAccess[conference]))

def setPermGlobalAccess(jid, level=0):
	tempAccess = eval(utils.readFile(path))
	tempAccess[jid] = None
	gGlobalAccess[jid] = None
	if level:
		tempAccess[jid] = level
		gGlobalAccess[jid] = level
	else:
		del tempAccess[jid]
		del gGlobalAccess[jid]
	path = getConfigPath(ACCESS_FILE)
	utils.writeFile(path, str(tempAccess))

def setTempGlobalAccess(jid, level=0):
	gGlobalAccess[jid] = None
	if level:
		gGlobalAccess[jid] = level
	else:
		del gGlobalAccess[jid]

def getAccess(conference, jid):
	if jid in gGlobalAccess:
		return gGlobalAccess[jid]
	if conference in gConferences:
		if jid in gPermAccess[conference]:
			return gPermAccess[conference][jid]
		if jid in gTempAccess[conference]:
			return gTempAccess[conference][jid]
	else:
		return 10
	return 0

def sendTo(msgType, jid, text):
	message = protocol.Message(jid)
	message.setType(msgType)
	text = text.strip()
	if text:
		message.setBody(text)
	gClient.send(message)
	callBotMessageHandlers(msgType, jid, text)

def sendToConference(conference, text):
	sendTo(protocol.TYPE_PUBLIC, conference, text)
		
def sendMsg(msgType, conference, nick, text, force=False):
	if protocol.TYPE_PUBLIC == msgType and not force:
		fools = getConferenceConfigKey(conference, "jokes")
		if fools and not random.randrange(0, 30):
			text = random.choice(gJokes)
		else:
			msgLimit = getConferenceConfigKey(conference, "msg")
			if msgLimit and len(text) > msgLimit:
				sendMsg(msgType, conference, nick, u"Смотри в привате (лимит %d символов)" % (msgLimit), True)
				msgType = protocol.TYPE_PRIVATE
	if protocol.TYPE_PUBLIC == msgType:
		text = u"%s: %s" % (nick, text)
		jid = conference
	else:
		jid = u"%s/%s" % (conference, nick)
	sendTo(msgType, jid, text)

def messageHandler(session, stanza):
	msgType = stanza.getType()
	if stanza.getTimestamp() or msgType in FORBIDDEN_TYPES:
		return
	fullJid = stanza.getFrom()
	conference = fullJid.getBareJid()
	isConference = conferenceInList(conference)
	if protocol.TYPE_PUBLIC == msgType and not isConference:
		return
	trueJid = getTrueJid(fullJid)
	if getAccess(conference, trueJid) == -100:
		return
	message = stanza.getBody() or ""
	message = message.strip()
	if protocol.TYPE_ERROR == msgType:
		errorCode = stanza.getErrorCode()
		if errorCode == "500":
			time.sleep(1)
		elif errorCode == "406":
			addConference(conference)
			joinConference(conference, gBotNick, getConferenceConfigKey(conference, "password"))
			time.sleep(0.5)
		else:
			return
		stanza = stanza.buildReply(message)
		stanza.setType(protocol.TYPE_PUBLIC)
		gClient.send(stanza)
		return
	if not message:
		return
	nick = fullJid.getResource()
	if protocol.TYPE_PUBLIC == msgType:
		if nickInConference(conference, nick):
			setNickKey(conference, nick, NICK_IDLE, time.time())
	else:
		if stanza.getTag("request"):
			reportMsg = protocol.Message(fullJid)
			reportMsg.setID(stanza.getID())
			reportMsg.addChild("received", None, None, protocol.NS_RECEIPTS)
			gClient.send(reportMsg)
	cmdType = isConference and CHAT or ROSTER
	callMessageHandlers(msgType, stanza, cmdType, conference, nick, trueJid, message)
	if isConference:
		botNick = getBotNick(conference)
		if botNick == nick:
			return
		if message.startswith(botNick):
			for x in [botNick + x for x in (":", ",")]:
				if message.startswith(x):
					message = message.replace(x, "").strip()
					break
		prefix = getConferenceConfigKey(conference, "prefix")
		if prefix:
			if message.startswith(prefix):
				message = message[len(prefix):].strip()
			elif protocol.TYPE_PUBLIC == msgType:
				return
		if not message:
			return
	rawBody = message.split(None, 1)
	command = rawBody[0].lower()
	if isConference and not isAvailableCommand(conference, command):
		return
	if isCommand(command):
		access = gCommands[command][CMD_ACCESS]
	else:
		if gMacros.hasMacros(command):
			access = gMacros.getAccess(command)
		elif isConference and gMacros.hasMacros(command, conference):
			access = gMacros.getAccess(command, conference)
		else:
			return
		message = gMacros.expand(message, (conference, nick, ), conference)
		rawBody = message.split(None, 1)
		command = rawBody[0].lower()
	if isCommand(command) and isAvailableCommand(conference, command):
		if isCommandType(command, cmdType):
			if getAccess(conference, trueJid) >= access:
				param = (len(rawBody) == 2) and rawBody[1] or None
				if param and isCommandType(command, NONPARAM):
					return
				if not param and isCommandType(command, PARAM):
					return
				callCommandHandlers(command, msgType, conference, nick, param)
			else:
				sendMsg(msgType, conference, nick, u"Недостаточно прав")

def presenceHandler(session, stanza):
	fullJid = stanza.getFrom()
	prsType =  stanza.getType()
	jid = fullJid.getBareJid()
	if conferenceInList(jid):
		conference = jid
		trueJid = stanza.getJid()
		nick = fullJid.getResource()
		if trueJid:
			trueJid = protocol.UserJid(trueJid).getBareJid()
		if not prsType:
			if not trueJid:
				leaveConference(conference, u"Без прав модератора работа невозможна!")
				return
			aff = stanza.getAffiliation()
			role = stanza.getRole()
			if not nickIsOnline(conference, nick):
				if not nickInConference(conference, nick):
					gConferences[conference][nick] = {}
				setNickKey(conference, nick, NICK_JID, trueJid)
				setNickKey(conference, nick, NICK_IDLE, time.time())
				setNickKey(conference, nick, NICK_HERE, True)
				setNickKey(conference, nick, NICK_JOINED, time.time())
				if gIsJoined[conference]:
					callJoinHandlers(conference, nick, trueJid, aff, role)
				else:
					if nick == getBotNick(conference):
						gIsJoined[conference] = True
			roleAccess = ROLES[role]
			affAccess = AFFILIATIONS[aff]
			setTempAccess(conference, trueJid, roleAccess + affAccess)
			setNickKey(conference, nick, NICK_MODER, role == protocol.ROLE_MODERATOR)
		elif protocol.PRS_OFFLINE == prsType:
			if nickIsOnline(conference, nick):
				code = stanza.getStatusCode()
				reason = stanza.getReason() or stanza.getStatus()
				setNickKey(conference, nick, NICK_HERE, False)
				if not getNickByJid(conference, trueJid):
					setTempAccess(conference, trueJid)
				for key in (NICK_IDLE, NICK_MODER, NICK_STATUS, NICK_SHOW):
					if key in gConferences[conference][nick]:
						del gConferences[conference][nick][key]
				callLeaveHandlers(conference, nick, trueJid, reason, code)
		elif prsType == protocol.TYPE_ERROR:
			errorCode = stanza.getErrorCode()
			if errorCode == "409":
				newNick = getBotNick(conference) + "."
				password = getConferenceConfigKey(conference, "password")
				joinConference(conference, newNick, password)
			elif errorCode == "404":
				delConference(conference)
				saveConferences()
			elif errorCode == "503":
				botNick = getBotNick(conference)
				password = getConferenceConfigKey(conference, "password")
				startTimer(REJOIN_DELAY, conference, (conference, botNick, password, ))
			elif errorCode in ("401", "403", "405"):
				leaveConference(conference, u"got %s error code" % errorCode)
			printf(stanza, FLAG_WARNING)
		callPresenceHandlers(stanza, CHAT, conference, nick, trueJid)
	else:
		resource = fullJid.getResource()
		callPresenceHandlers(stanza, ROSTER, jid, resource, None)

def iqHandler(session, stanza):
	fullJid = stanza.getFrom()
	bareJid = fullJid.getBareJid()
	trueJid = getTrueJid(fullJid)
	if getAccess(bareJid, trueJid) == -100:
		return
	resource = fullJid.getResource()
	callIqHandlers(stanza, bareJid, resource)

def writeToLog(text, logtype):
	path = getFilePath(SYSLOG_DIR, time.strftime(LOG_TYPES[logtype]))
	utils.writeFile(path, text + "\n", "a")
	if LOG_WARN == logtype:
		gInfo["warn"] += 1
	else:
		gInfo["err"] += 1

def loadPlugins():
	printf("Loading plugins...")
	validPlugins = 0
	invalidPlugins = 0
	plugins = os.listdir(PLUGIN_DIR)
	for plugin in plugins:
		try:
			path = os.path.join(PLUGIN_DIR, plugin)
			if os.path.isfile(path):
				exec(file(path)) in globals()
				validPlugins += 1
		except (SyntaxError, NameError):
			printf("Exception in loadPlugins function", FLAG_ERROR)
			writeToLog(traceback.format_exc(), LOG_ERROR)
			invalidPlugins += 1
	if not invalidPlugins:
		printf("Loaded %d plugins" % (validPlugins), FLAG_SUCCESS)
	else:
		printf("Loaded %d plugins (%d with errors)" % (validPlugins, invalidPlugins), FLAG_WARNING)

def detectMultiLaunch():
	if os.name == "posix":
		try:
			pid = int(utils.readFile(PID_FILE))
			os.getsid(pid)
			return pid
		except (OSError, IOError):
			utils.writeFile(PID_FILE, str(os.getpid()))
	return None

def shutdown(restart=False):
	gClient.disconnected()
	callEventHandlers(SHUTDOWN)
	if restart:
		printf("Restarting...")
		time.sleep(RESTART_DELAY)
		if os.path.exists(PID_FILE):
			os.remove(PID_FILE)
		os.execl(sys.executable, sys.executable, sys.argv[0])
	else:
		printf("Terminating...")
		os.abort()

if __name__ == "__main__":
	try:
		pid = detectMultiLaunch()
		if not pid:
			gInfo["start"] = time.time()

			loadPlugins()

			printf("Connecting...")
			if gClient.connect(secureMode=gSecureMode, useResolver=gUseResolver):
				printf("Connection established (%s)" % gClient.isConnected(), FLAG_SUCCESS)
			else:
				printf("Unable to connect", FLAG_ERROR)
				if gRestart:
					printf("Sleeping for %d seconds..." % RECONNECT_DELAY)
					time.sleep(RECONNECT_DELAY)
					shutdown(True)
				else:
					shutdown()

			printf("Waiting for authentication...")
			if gClient.auth(gUserName, gPassword, gResource):
				printf("Connected", FLAG_SUCCESS)
			else:
				printf("Incorrect login/password", FLAG_ERROR)
				shutdown()

			callEventHandlers(STARTUP)
			clearEventHandlers(STARTUP)

			gClient.registerHandler("message", messageHandler)
			gClient.registerHandler("presence", presenceHandler)
			gClient.registerHandler("iq", iqHandler)
			printf("Handlers registered", FLAG_SUCCESS)

			gRoster = gClient.getRoster()
			gClient.setStatus(None, None, gPriority)

			path = getConfigPath(CONF_FILE)
			utils.createFile(path, "[]")
			conferences = eval(utils.readFile(path))
			if conferences:
				for conference in conferences:
					addConference(conference)
					joinConference(conference, getBotNick(conference), getConferenceConfigKey(conference, "password"))
					saveConferenceConfig(conference)
				printf("Entered in %d rooms" % (len(conferences)), FLAG_SUCCESS)

			callEventHandlers(INIT_2)
			clearEventHandlers(INIT_2)
			
			printf("Now I am ready to work :)")
			while True:
				gClient.process(10)
		else:
			printf("Another instance is running (pid: %s)" % (pid), FLAG_ERROR)
	except KeyboardInterrupt:
		if gClient.isConnected():
			prs = protocol.Presence(typ=protocol.PRS_OFFLINE)
			prs.setStatus(u"Выключаюсь (CTRL+C)")
			gClient.send(prs)
		shutdown()
	except protocol.SystemShutdown:
		printf("Remote server was switched off", FLAG_WARNING)
		shutdown()
	except protocol.Conflict:
		printf("Resource conflict", FLAG_WARNING)
		shutdown()
	except Exception:
		printf("Exception in main thread", FLAG_ERROR)
		writeToLog(traceback.format_exc(), LOG_CRASH)
		if gClient.isConnected():
			prs = protocol.Presence(typ=protocol.PRS_OFFLINE)
			prs.setStatus(u"что-то сломалось...")
			gClient.send(prs)
		shutdown(gRestart)
