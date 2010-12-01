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

import os
import random
import re
import sys
import threading
import time
import traceback

import chardet
import database
import macros
import simplejson

from xmpp import client, debug, protocol, simplexml
from utils import utils

VER_MAJOR = 0
VER_MINOR = 1

IDENTITY_CAT = "bot"
IDENTITY_TYPE = "pc"
IDENTITY_NAME = "snapi"

VER_CAPS = "http://snapi-bot.googlecode.com/caps"

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
LOG_ERRORS_FILE = "%Y.%m.%d_errors.txt"
LOG_CRASHES_FILE = "%Y.%m.%d_crashes.txt"
LOG_WARNINGS_FILE = "%Y.%m.%d_warnings.txt"

FLAG_INFO = "info"
FLAG_ERROR = "error"
FLAG_WARNING = "warning"
FLAG_SUCCESS = "success"

CMD_CONFERENCE = 0x0001
CMD_ROSTER = 0x0002
CMD_FROZEN = 0x0004
CMD_NONPARAM = 0x0008
CMD_PARAM = 0x0010
CMD_ANY = CMD_CONFERENCE | CMD_ROSTER

CMD_DESC = 0x1
CMD_TYPE = 0x2
CMD_ACCESS = 0x3
CMD_SYNTAX = 0x4
CMD_EXAMPLE = 0x5

NICK_JID = "jid"
NICK_IDLE = "idle"
NICK_HERE = "here"
NICK_MODER = "moder"
NICK_JOINED = "joined"
NICK_SHOW = "show"
NICK_STATUS = "status"

LOG_ERRORS = 0x1
LOG_CRASHES = 0x2
LOG_WARNINGS = 0x3

LOG_TYPES = {
	LOG_CRASHES: LOG_CRASHES_FILE, 
	LOG_ERRORS: LOG_ERRORS_FILE, 
	LOG_WARNINGS: LOG_WARNINGS_FILE
}

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

STATUS_STRINGS = (
	protocol.PRS_AWAY, 
	protocol.PRS_NA, 
	protocol.PRS_DND, 
	protocol.PRS_CHAT
)

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

REJOIN_DELAY = 120
RECONNECT_DELAY = 15
RESTART_DELAY = 5

H_CONFERENCE = 0x1
H_ROSTER = 0x2

EVT_ADDCONFERENCE = 0x1
EVT_DELCONFERENCE = 0x2
EVT_STARTUP = 0x3
EVT_READY = 0x4
EVT_SHUTDOWN = 0x5

gBotMsgHandlers = []
gJoinHandlers = []
gLeaveHandlers = []
gIqHandlers = []
gCmdHandlers = {}

gEventHandlers = {
	EVT_ADDCONFERENCE: [], 
	EVT_DELCONFERENCE: [], 
	EVT_STARTUP: [], 
	EVT_READY: [], 
	EVT_SHUTDOWN: []
}
gPresenceHandlers = {
	H_ROSTER: [], 
	H_CONFERENCE: []
}
gMessageHandlers = {
	H_ROSTER: [], 
	H_CONFERENCE: []
}

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

gInfo = {"msg": 0, "prs": 0, "iq": 0, "cmd": 0, "thr": 0, "err": 0, "tmr": 0, "warn": 0}

THR_SEMAPHORE = threading.BoundedSemaphore(30)

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

def registerCommand(function, command, access, desc, syntax, examples, cmdType=CMD_ANY):
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

def callMessageHandlers(hType, msgType, stanza, conference, nick, trueJid, body):
	gInfo["msg"] += 1
	for function in gMessageHandlers[hType]:
		startThread(function, (stanza, msgType, conference, nick, trueJid, body))

def callIqHandlers(stanza, jid, resource):
	gInfo["iq"] += 1
	for function in gIqHandlers:
		startThread(function, (stanza, jid, resource))

def callPresenceHandlers(hType, stanza, jid, resource, trueJid):
	gInfo["prs"] += 1
	for function in gPresenceHandlers[hType]:
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
			with THR_SEMAPHORE:
				function(*args)
		else:
			with THR_SEMAPHORE:
				function()
	except Exception:
		printf("Exception in %s function" % (function.__name__), FLAG_ERROR)
		writeSystemLog(traceback.format_exc(), LOG_ERRORS)

def printf(text, flag=FLAG_INFO):
	gDebug.show(text, flag, flag)

getFilePath = os.path.join

def getConfigPath(*param):
	return os.path.join(CONFIG_DIR, *param)

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
	callEventHandlers(EVT_ADDCONFERENCE, (conference, ))

def delConference(conference):
	callEventHandlers(EVT_DELCONFERENCE, (conference, ))
	del gIsJoined[conference]
	del gConferenceConfig[conference]
	del gConferences[conference]

def joinConference(conference, nick, password):
	setConferenceConfigKey(conference, "nick", nick)
	setConferenceConfigKey(conference, "password", password)

	status = getConferenceConfigKey(conference, "status")
	show = getConferenceConfigKey(conference, "show")
	prs = getPresenceNode(show, status, PROFILE_PRIORITY)
	prs.setTo(u"%s/%s" % (conference, nick))
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
	return getConferenceConfigKey(conference, "nick") or PROFILE_NICK

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
	
def getTrueJid(jid, resource=None):
	if isinstance(jid, protocol.UserJid):
		jid = unicode(jid)
	if not resource:
		if jid.find("/") > -1:
			jid, resource = jid.split("/", 1)
	if jid in gConferences:
		if isNickInConference(jid, resource):
			jid = getNickKey(jid, resource, NICK_JID)
	return jid

def getNickByJid(conference, trueJid, offline=False):
	nicks = offline and getNicks(conference) or getOnlineNicks(conference)
	for nick in nicks:
		if getNickKey(conference, nick, NICK_JID) == trueJid:
			return nick
	return None

def getNickKey(conference, nick, key):
	return gConferences[conference][nick].get(key)

def setNickKey(conference, nick, key, value):
	gConferences[conference][nick][key] = value

def isConferenceInList(conference):
	return conference in gConferences

def isNickInConference(conference, nick):
	return nick in gConferences[conference]

def isNickOnline(conference, nick):
	return isNickInConference(conference, nick) and getNickKey(conference, nick, NICK_HERE)

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
	path = getConfigPath(ACCESS_FILE)
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

def getPresenceNode(show, status, priority):
	prs = protocol.Presence(priority=priority)
	prs.setAttr("ver", VER_FULL)
	if status:
		prs.setStatus(status)
	if show:
		prs.setShow(show)

	caps = protocol.Node("c")
	caps.setNamespace(protocol.NS_CAPS)
	caps.setAttr("node", VER_CAPS)
	caps.setAttr("ver", VER_HASH)
	caps.setAttr("hash", "sha-1")

	prs.addChild(node=caps)
	return prs
	
def setStatus(show, status, priority):
	gClient.send(getPresenceNode(show, status, priority))

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
	isConference = isConferenceInList(conference)
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
	if isConference:
		if stanza.getTag("subject"):
			message = stanza.getSubject()
	if not message:
		return
	nick = fullJid.getResource()
	if protocol.TYPE_PUBLIC == msgType:
		if isNickInConference(conference, nick):
			setNickKey(conference, nick, NICK_IDLE, time.time())
	else:
		if stanza.getTag("request"):
			reportMsg = protocol.Message(fullJid)
			reportMsg.setID(stanza.getID())
			reportMsg.addChild("received", None, None, protocol.NS_RECEIPTS)
			gClient.send(reportMsg)
	cmdType = isConference and CMD_CONFERENCE or CMD_ROSTER
	hType = isConference and H_CONFERENCE or H_ROSTER
	callMessageHandlers(hType, msgType, stanza, conference, nick, trueJid, message)
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
		message = gMacros.expand(message, (conference, nick), conference)
		rawBody = message.split(None, 1)
		command = rawBody[0].lower()
	if isCommand(command) and isAvailableCommand(conference, command):
		if isCommandType(command, cmdType):
			if getAccess(conference, trueJid) >= access:
				param = (len(rawBody) == 2) and rawBody[1] or None
				if param and isCommandType(command, CMD_NONPARAM):
					return
				if not param and isCommandType(command, CMD_PARAM):
					return
				callCommandHandlers(command, msgType, conference, nick, param)
			else:
				sendMsg(msgType, conference, nick, u"Недостаточно прав")

def presenceHandler(session, stanza):
	fullJid = stanza.getFrom()
	prsType =  stanza.getType()
	jid = fullJid.getBareJid()
	if isConferenceInList(jid):
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
			if not isNickOnline(conference, nick):
				if not isNickInConference(conference, nick):
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
			if isNickOnline(conference, nick):
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
				writeSystemLog(u"%s is deleted (%s)" % (conference, errorCode), LOG_WARNINGS, True)
			elif errorCode == "503":
				botNick = getBotNick(conference)
				password = getConferenceConfigKey(conference, "password")
				startTimer(REJOIN_DELAY, conference, (conference, botNick, password))
			elif errorCode in ("401", "403", "405"):
				leaveConference(conference, u"got %s error code" % errorCode)
				writeSystemLog(u"Got error in %s (%s)" % (conference, errorCode), LOG_WARNINGS, True)
		callPresenceHandlers(H_CONFERENCE, stanza, conference, nick, trueJid)
	else:
		resource = fullJid.getResource()
		callPresenceHandlers(H_ROSTER, stanza, jid, resource, None)

def iqHandler(session, stanza):
	fullJid = stanza.getFrom()
	bareJid = fullJid.getBareJid()
	trueJid = getTrueJid(fullJid)
	if getAccess(bareJid, trueJid) == -100:
		return
	resource = fullJid.getResource()
	if protocol.TYPE_ERROR != stanza.getType():
		if stanza.getTags("query", {}, protocol.NS_VERSION):
			iq = stanza.buildReply(protocol.TYPE_RESULT)
			query = iq.getTag("query")
			query.setTagData("name", "Snapi-Snup")
			query.setTagData("version", VER_FULL)
			query.setTagData("os", OS_NAME)
		elif stanza.getTags("query", {}, protocol.NS_LAST):
			iq = stanza.buildReply(protocol.TYPE_RESULT)
			query = iq.getTag("query")
			query.setAttr("seconds", int(time.time() - gInfo["start"]))
		elif stanza.getTags("time", {}, protocol.NS_ENTITY_TIME):
			tZone = time.altzone if time.localtime()[8] else time.timezone
			sign = (tZone < 0) and "+" or "-"
			tzo = "%s%02d:%02d" % (sign, abs(tZone) / 3600, abs(tZone) / 60 % 60)
			utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
			iq = stanza.buildReply(protocol.TYPE_RESULT)
			tNode = iq.addChild("time", {}, [], protocol.NS_ENTITY_TIME)
			tNode.setTagData("tzo", tzo)
			tNode.setTagData("utc", utc)
		elif stanza.getTags("ping", {}, protocol.NS_PING):
			iq = stanza.buildReply(protocol.TYPE_RESULT)
		elif stanza.getTags("query", {}, protocol.NS_DISCO_INFO):
			iq = stanza.buildReply(protocol.TYPE_RESULT)
			query = iq.addChild("query", {}, [], protocol.NS_DISCO_ITEMS)
			query.addChild("identity", {"category": IDENTITY_CAT, "type": IDENTITY_TYPE, "name": IDENTITY_NAME})
			for feat in BOT_FEATURES:
				query.addChild("feature", {"var": feat})
		else:
			iq = stanza.buildReply(protocol.TYPE_ERROR)
			error = iq.addChild("error", {"type": "cancel"})
			error.addChild("feature-not-implemented", {}, [], protocol.NS_STANZAS)
		gClient.send(iq)
	callIqHandlers(stanza, bareJid, resource)

def writeSystemLog(text, logtype, show=False):
	path = getFilePath(SYSLOG_DIR, time.strftime(LOG_TYPES[logtype]))
	utils.writeFile(path, text.encode("utf-8") + "\n", "a")
	if LOG_WARNINGS == logtype:
		gInfo["warn"] += 1
	else:
		gInfo["err"] += 1
	if show:
		if LOG_WARNINGS == logtype:
			printf(text, FLAG_WARNING)
		else:
			printf(text, FLAG_ERROR)

def loadMainConfig():
	f = file(BOTCONFIG_FILE)
	exec f in globals()
	
	global PROFILE_USERNAME, PROFILE_SERVER
	PROFILE_USERNAME, PROFILE_SERVER = PROFILE_JID.split("@")

def initVersions():
	import base64, hashlib, platform
	global OS_NAME, VER_HASH, VER_FULL

	osinfo = platform.uname()
	OS_NAME = u"%s %s" % (osinfo[0], osinfo[2])
	
	pipe = os.popen("svnversion")
	rawrev = pipe.read()
	pipe.close()

	if not rawrev:
		rawrev = 0
		
	VER_FULL = u"%d.%d.%s" % (VER_MAJOR, VER_MINOR, rawrev)
		
	features = "<".join(BOT_FEATURES)
	string = u"%s/%s//%s<%s<" % (IDENTITY_TYPE, IDENTITY_CAT, IDENTITY_NAME, features)
	VER_HASH = base64.b64encode(hashlib.sha1(string).digest())

def initDebugger():
	global gDebug
	gDebug = debug.Debug(CORE_DBG, showFlags=False)
	gDebug.colors[FLAG_ERROR] = debug.colorBrightRed
	gDebug.colors[FLAG_WARNING] = debug.colorYellow
	gDebug.colors[FLAG_SUCCESS] = debug.colorBrightCyan

def loadPlugins():
	printf("Loading plugins...")
	validPlugins = 0
	invalidPlugins = 0
	plugins = os.listdir(PLUGIN_DIR)
	for plugin in plugins:
		try:
			path = os.path.join(PLUGIN_DIR, plugin)
			if os.path.isfile(path):
				f = file(path)
				exec f in globals()
				validPlugins += 1
		except (SyntaxError, NameError):
			printf("Exception in loadPlugins function", FLAG_ERROR)
			writeSystemLog(traceback.format_exc(), LOG_ERRORS)
			invalidPlugins += 1
	if not invalidPlugins:
		printf("Loaded %d plugins" % (validPlugins), FLAG_SUCCESS)
	else:
		printf("Loaded %d plugins (%d with errors)" % (validPlugins, invalidPlugins), FLAG_WARNING)

def findAnotherInstance():
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
	callEventHandlers(EVT_SHUTDOWN)
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
	global gDebug, gClient, gRoster

	gInfo["start"] = time.time()

	currentDir = os.path.dirname(sys.argv[0])
	if currentDir:
		os.chdir(currentDir)

	loadMainConfig()
	initDebugger()
	initVersions()

	pid = findAnotherInstance()
	if not pid:
		try:
			loadPlugins()

			printf("Connecting...")
			gClient = client.Client(server=PROFILE_SERVER, port=PROFILE_PORT, debugFlags=XMPP_DBG)
			if gClient.connect(secureMode=PROFILE_SECURE, useResolver=PROFILE_USE_RESOLVER):
				printf("Connection established (%s)" % gClient.isConnected(), FLAG_SUCCESS)
			else:
				printf("Unable to connect", FLAG_ERROR)
				if RESTART_IF_ERROR:
					printf("Sleeping for %d seconds..." % RECONNECT_DELAY)
					time.sleep(RECONNECT_DELAY)
					shutdown(True)
				else:
					shutdown()

			printf("Waiting for authentication...")
			if gClient.auth(PROFILE_USERNAME, PROFILE_PASSWORD, PROFILE_RESOURCE):
				printf("Connected", FLAG_SUCCESS)
			else:
				printf("Incorrect login/password", FLAG_ERROR)
				shutdown()

			callEventHandlers(EVT_STARTUP)
			clearEventHandlers(EVT_STARTUP)

			gClient.registerHandler("message", messageHandler)
			gClient.registerHandler("presence", presenceHandler)
			gClient.registerHandler("iq", iqHandler)
			printf("Handlers registered", FLAG_SUCCESS)

			gRoster = gClient.getRoster()
			gClient.setStatus = setStatus
			gClient.setStatus(None, None, PROFILE_PRIORITY)

			path = getConfigPath(CONF_FILE)
			utils.createFile(path, "[]")
			conferences = eval(utils.readFile(path))
			if conferences:
				for conference in conferences:
					addConference(conference)
					joinConference(conference, getBotNick(conference), getConferenceConfigKey(conference, "password"))
					saveConferenceConfig(conference)
				printf("Entered in %d rooms" % (len(conferences)), FLAG_SUCCESS)

			callEventHandlers(EVT_READY)
			clearEventHandlers(EVT_READY)
			
			printf("Now I am ready to work :)")
			while True:
				gClient.process(10)
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
			writeSystemLog(traceback.format_exc(), LOG_CRASHES)
			if gClient.isConnected():
				prs = protocol.Presence(typ=protocol.PRS_OFFLINE)
				prs.setStatus(u"что-то сломалось...")
				gClient.send(prs)
			shutdown(RESTART_IF_ERROR)
	else:
		printf("Another instance is running (pid: %s)" % (pid), FLAG_ERROR)
