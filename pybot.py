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

from classes import config
from classes import database
from classes import macros
from classes import version

from utils import utils

from xmpp import client
from xmpp import debug
from xmpp import protocol

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

MODE_ASYNC = 0x1
MODE_SYNC = 0x2

CMD_CONFERENCE = 0x01
CMD_ROSTER = 0x02
CMD_FROZEN = 0x04
CMD_NONPARAM = 0x08
CMD_PARAM = 0x10
CMD_ANY = CMD_CONFERENCE | CMD_ROSTER

CMD_DESC = 0x1
CMD_TYPE = 0x2
CMD_ACCESS = 0x3
CMD_SYNTAX = 0x4
CMD_EXAMPLE = 0x5

NICK_JID = "jid"
NICK_IDLE = "idle"
NICK_HERE = "here"
NICK_ROLE = "role"
NICK_AFF = "aff"
NICK_SHOW = "show"
NICK_STATUS = "status"
NICK_JOINED = "joined"

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

H_CONFERENCE = 0x0001
H_ROSTER = 0x0002

EVT_IQ = 0x0004
EVT_MSG = 0x0008
EVT_PRS = 0x0010

EVT_SELFMSG = 0x0020

EVT_USERJOIN = 0x0040
EVT_USERLEAVE = 0x0080

EVT_ADDCONFERENCE = 0x0100
EVT_DELCONFERENCE = 0x0200

EVT_STARTUP = 0x0400
EVT_READY = 0x0800
EVT_SHUTDOWN = 0x1000

gEventHandlers = {}
gCmdHandlers = {}

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

gInfo = {"msg": 0, "prs": 0, "iq": 0, "cmd": 0, "thr": 0, "err": 0, "tmr": 0}

gDebug = debug.Debug([debug.DBG_ALWAYS], showFlags=False)
gDebug.colors[FLAG_ERROR] = debug.colorBrightRed
gDebug.colors[FLAG_WARNING] = debug.colorYellow
gDebug.colors[FLAG_SUCCESS] = debug.colorBrightCyan

THR_SEMAPHORE = threading.BoundedSemaphore(30)

def registerCommand(function, command, access, desc, syntax, examples, cmdType=CMD_ANY):
	gCmdHandlers[command] = function
	gCommands[command] = {
		CMD_ACCESS: access, 
		CMD_DESC: desc, 
		CMD_SYNTAX: syntax, 
		CMD_EXAMPLE: examples, 
		CMD_TYPE: cmdType
	}

def registerEventHandler(function, evtType):
	if evtType not in gEventHandlers:
		gEventHandlers[evtType] = []
	gEventHandlers[evtType].append(function)

def callEventHandlers(evtType, mode, *args):
	if evtType in gEventHandlers:
		if MODE_ASYNC == mode:
			for function in gEventHandlers[evtType]:
				startThread(function, *args)
		else:
			for function in gEventHandlers[evtType]:
				function(*args)

def clearEventHandlers(evtType):
	del gEventHandlers[evtType]

def startThread(function, *args):
	gInfo["thr"] += 1
	threading.Thread(None, execute, function.__name__, (function, args)).start()

def startTimer(timeout, function, *args):
	gInfo["tmr"] += 1
	timer = threading.Timer(timeout, execute, (function, args))
	timer.setName(function.__name__)
	timer.start()
	return timer

def execute(function, args):
	try:
		with THR_SEMAPHORE:
			function(*args)
	except Exception:
		printf("Exception in %s function" % (function.__name__), FLAG_ERROR)
		addTextToSysLog(traceback.format_exc(), LOG_ERRORS)

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
	callEventHandlers(EVT_ADDCONFERENCE, MODE_SYNC, conference)

def delConference(conference):
	callEventHandlers(EVT_DELCONFERENCE, MODE_SYNC, conference)
	del gIsJoined[conference]
	del gConferenceConfig[conference]
	del gConferences[conference]

def joinConference(conference, nick, password):
	setConferenceConfigKey(conference, "nick", nick)
	setConferenceConfigKey(conference, "password", password)

	status = getConferenceConfigKey(conference, "status")
	show = getConferenceConfigKey(conference, "show")
	prs = getPresenceNode(show, status, gConfig.PRIORITY)
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
	return getConferenceConfigKey(conference, "nick") or gConfig.NICK

def isCommand(command):
	return command in gCommands

def isCommandType(command, cmdType):
	return gCommands[command][CMD_TYPE] & cmdType

def isAvailableCommand(conference, command):
	return command not in gCmdOff[conference]

def getNicks(conference):
	return gConferences[conference].keys()

def getOnlineNicks(conference):
	return [x for x in gConferences[conference] if getNickKey(conference, x, NICK_HERE)]
	
def getTrueJID(jid, resource=None):
	if jid in gConferences:
		if isNickInConference(jid, resource):
			jid = getNickKey(jid, resource, NICK_JID)
	return jid

def getNickByJID(conference, truejid, offline=False):
	nicks = offline and getNicks(conference) or getOnlineNicks(conference)
	for nick in nicks:
		if getNickKey(conference, nick, NICK_JID) == truejid:
			return nick
	return None

def getNickKey(conference, nick, key):
	return gConferences[conference][nick].get(key)

def setNickKey(conference, nick, key, value):
	gConferences[conference][nick][key] = value

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
	prs.setAttr("ver", gVerInfo.getVersion())
	if status:
		prs.setStatus(status)
	if show:
		prs.setShow(show)

	caps = protocol.Node("c")
	caps.setNamespace(protocol.NS_CAPS)
	caps.setAttr("node", version.CAPS)
	caps.setAttr("ver", gVerInfo.getFeaturesHash())
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
	callEventHandlers(EVT_SELFMSG, MODE_ASYNC, msgType, jid, text)

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
				sendMsg(msgType, conference, nick, u"Смотри в привате (ограничение в %d символов)" % (msgLimit), True)
				msgType = protocol.TYPE_PRIVATE
	if protocol.TYPE_PUBLIC == msgType:
		text = u"%s: %s" % (nick, text)
		jid = conference
	else:
		jid = u"%s/%s" % (conference, nick)
	sendTo(msgType, jid, text)

def messageHandler(session, stanza):
	# TODO сделать из этой сотни строк что-то хорошее
	gInfo["msg"] += 1
	msgType = stanza.getType()
	if stanza.getTimestamp() or msgType in FORBIDDEN_TYPES:
		return
	fulljid = stanza.getFrom()
	jid = fulljid.getBareJID()
	isConference = jid in gConferences
	if protocol.TYPE_PUBLIC == msgType and not isConference:
		return
	if isConference:
		conference = jid
		nick = fulljid.getResource()
		truejid = getTrueJID(conference, nick)
		userAccess = getAccess(conference, truejid)
	else:
		userAccess = getAccess(None, jid)
		resource = fulljid.getResource()
	if -100 == userAccess:
		return
	message = stanza.getBody() or ""
	message = message.strip()
	if protocol.TYPE_ERROR == msgType:
		errorCode = stanza.getErrorCode()
		if errorCode == "500":
			time.sleep(1)
		elif errorCode == "406":
			addConference(conference)
			joinConference(conference, gConfig.NICK, getConferenceConfigKey(conference, "password"))
			time.sleep(0.5)
		else:
			return
		stanza = stanza.buildReply(message)
		stanza.setType(protocol.TYPE_PUBLIC)
		gClient.send(stanza)
		return
	if not message:
		return
	if protocol.TYPE_PUBLIC == msgType:
		if conference != truejid:
			setNickKey(conference, nick, NICK_IDLE, time.time())
	else:
		if stanza.getTag("request"):
			reportMsg = protocol.Message(fulljid)
			reportMsg.setID(stanza.getID())
			reportMsg.addChild("received", None, None, protocol.NS_RECEIPTS)
			gClient.send(reportMsg)
	if isConference:
		callEventHandlers(EVT_MSG | H_CONFERENCE, MODE_ASYNC, stanza, msgType, conference, nick, truejid, message)
	else:
		callEventHandlers(EVT_MSG | H_ROSTER, MODE_ASYNC, stanza, msgType, jid, resource, message)
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
	rawbody = message.split(None, 1)
	command = rawbody[0].lower()
	if isConference:
		if isCommand(command):
			if isAvailableCommand(conference, command):
				cmdAccess = gCommands[command][CMD_ACCESS]
				cmdType = CMD_CONFERENCE
			else:
				return
		else:
			if gMacros.hasMacros(command):
				cmdAccess = gMacros.getAccess(command)
			elif gMacros.hasMacros(command, conference):
				cmdAccess = gMacros.getAccess(command, conference)
			else:
				return
			message = gMacros.expand(message, (conference, nick), conference)
			rawbody = message.split(None, 1)
			command = rawbody[0].lower()
			if not isCommand or not isAvailableCommand(conference, command):
				return
		cmdType = CMD_CONFERENCE
	else:
		if isCommand(command):
			cmdAccess = gCommands[command][CMD_ACCESS]
		elif gMacros.hasMacros(command):
			cmdAccess = gMacros.getAccess(command)
			message = gMacros.expand(message, (jid, resource))
			rawbody = message.split(None, 1)
			command = rawbody[0].lower()
			if not isCommand:
				return
		cmdType = CMD_ROSTER
	if isCommandType(command, cmdType):
		if userAccess >= cmdAccess:
			param = (len(rawbody) == 2) and rawbody[1] or None
			if param and isCommandType(command, CMD_NONPARAM):
				return
			if not param and isCommandType(command, CMD_PARAM):
				return
			gInfo["cmd"] += 1
			if isConference:
				startThread(gCmdHandlers[command], msgType, conference, nick, param)
			else:
				startThread(gCmdHandlers[command], msgType, jid, resource, param)
		else:
			if isConference:
				sendMsg(msgType, conference, nick, u"Недостаточно прав")
			else:
				sendMsg(msgType, jid, resource, u"Недостаточно прав")

def presenceHandler(session, stanza):
	gInfo["prs"] += 1
	fulljid = stanza.getFrom()
	jid = fulljid.getBareJID()
	if jid in gConferences:
		conference = jid
		truejid = stanza.getJID()
		nick = fulljid.getResource()
		prsType = stanza.getType()
		if truejid:
			truejid = protocol.UserJID(truejid).getBareJID()
		if not prsType:
			if not truejid:
				leaveConference(conference, u"Без прав модератора работа невозможна!")
				return
			aff = stanza.getAffiliation()
			role = stanza.getRole()
			if not isNickOnline(conference, nick):
				if not isNickInConference(conference, nick):
					gConferences[conference][nick] = {}
				setNickKey(conference, nick, NICK_JID, truejid)
				setNickKey(conference, nick, NICK_IDLE, time.time())
				setNickKey(conference, nick, NICK_HERE, True)
				setNickKey(conference, nick, NICK_JOINED, time.time())
				if gIsJoined[conference]:
					callEventHandlers(EVT_USERJOIN, MODE_ASYNC, conference, nick, truejid, aff, role)
				else:
					if nick == getBotNick(conference):
						gIsJoined[conference] = True
			roleAccess = ROLES[role]
			affAccess = AFFILIATIONS[aff]
			setTempAccess(conference, truejid, roleAccess + affAccess)
			setNickKey(conference, nick, NICK_AFF, aff)
			setNickKey(conference, nick, NICK_ROLE, role)
		elif protocol.PRS_OFFLINE == prsType:
			if isNickOnline(conference, nick):
				code = stanza.getStatusCode()
				reason = stanza.getReason() or stanza.getStatus()
				setNickKey(conference, nick, NICK_HERE, False)
				if not getNickByJID(conference, truejid):
					setTempAccess(conference, truejid)
				for key in (NICK_IDLE, NICK_AFF, NICK_ROLE, NICK_STATUS, NICK_SHOW):
					if key in gConferences[conference][nick]:
						del gConferences[conference][nick][key]
				callEventHandlers(EVT_USERLEAVE, MODE_ASYNC, conference, nick, truejid, reason, code)
		elif protocol.TYPE_ERROR == prsType:
			errorCode = stanza.getErrorCode()
			if errorCode == "409":
				newNick = getBotNick(conference) + "."
				password = getConferenceConfigKey(conference, "password")
				joinConference(conference, newNick, password)
			elif errorCode == "404":
				delConference(conference)
				saveConferences()
				addTextToSysLog(u"%s is deleted (%s)" % (conference, errorCode), LOG_WARNINGS, True)
			elif errorCode == "503":
				botNick = getBotNick(conference)
				password = getConferenceConfigKey(conference, "password")
				startTimer(REJOIN_DELAY, joinConference, conference, botNick, password)
			elif errorCode in ("401", "403", "405"):
				leaveConference(conference, u"got %s error code" % errorCode)
				addTextToSysLog(u"Got error in %s (%s)" % (conference, errorCode), LOG_WARNINGS, True)
		callEventHandlers(EVT_PRS | H_CONFERENCE, MODE_ASYNC, stanza, conference, nick, truejid)
	else:
		resource = fulljid.getResource()
		callEventHandlers(EVT_PRS | H_ROSTER, MODE_ASYNC, stanza, jid, resource)

def iqHandler(session, stanza):
	gInfo["iq"] += 1
	fulljid = stanza.getFrom()
	jid = fulljid.getBareJID()
	isConference = jid in gConferences
	if isConference:
		conference = jid
		nick = fulljid.getResource()
		truejid = getTrueJID(conference, nick)
		if getAccess(conference, truejid) == -100:
			return
	else:
		if getAccess(None, jid) == -100:
			return
		resource = fulljid.getResource()
	if protocol.TYPE_GET == stanza.getType():
		if stanza.getTags("query", {}, protocol.NS_VERSION):
			iq = stanza.buildReply(protocol.TYPE_RESULT)
			query = iq.getTag("query")
			query.setTagData("name", version.APP_NAME)
			query.setTagData("version", gVerInfo.getVersion())
			query.setTagData("os", gVerInfo.getOSName())
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
			attrs = {
				"category": version.IDENTITY_CAT, 
				"type": version.IDENTITY_TYPE, 
				"name": version.IDENTITY_NAME
			}
			query.addChild("identity", attrs)
			for feat in BOT_FEATURES:
				query.addChild("feature", {"var": feat})
		else:
			iq = stanza.buildReply(protocol.TYPE_ERROR)
			error = iq.addChild("error", {"type": "cancel"})
			error.addChild("feature-not-implemented", {}, [], protocol.NS_STANZAS)
		gClient.send(iq)
	if isConference:
		callEventHandlers(EVT_IQ | H_CONFERENCE, MODE_ASYNC, stanza, conference, nick, truejid)
	else:
		callEventHandlers(EVT_IQ | H_ROSTER, MODE_ASYNC, stanza, jid, resource)

def addTextToSysLog(text, logtype, show=False):
	path = getFilePath(SYSLOG_DIR, time.strftime(LOG_TYPES[logtype]))
	if isinstance(text, unicode):
		text = text.encode("utf-8") 
	utils.writeFile(path, text + "\n", "a")
	if LOG_ERRORS == logtype:
		gInfo["err"] += 1
	if show:
		if LOG_WARNINGS == logtype:
			printf(text, FLAG_WARNING)
		else:
			printf(text, FLAG_ERROR)

def loadPlugins():
	validPlugins = 0
	invalidPlugins = 0
	plugins = os.listdir(PLUGIN_DIR)
	for plugin in plugins:
		try:
			path = os.path.join(PLUGIN_DIR, plugin)
			if os.path.isfile(path):
				execfile(path, globals())
				validPlugins += 1
		except (SyntaxError, NameError):
			printf("Exception in loadPlugins function", FLAG_ERROR)
			addTextToSysLog(traceback.format_exc(), LOG_ERRORS)
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
	if gClient.isConnected():
		callEventHandlers(EVT_SHUTDOWN, MODE_SYNC)
		gClient.disconnected()
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
	currentDir = os.path.dirname(sys.argv[0])
	if currentDir:
		os.chdir(currentDir)

	pid = findAnotherInstance()
	if not pid:
		global gConfig, gClient, gRoster

		gInfo["start"] = time.time()

		try:
			gConfig = config.Config(BOTCONFIG_FILE)

			gClient = client.Client(server=gConfig.SERVER, port=gConfig.PORT)

			gVerInfo = version.VersionInfo()
			gVerInfo.createFeaturesHash(BOT_FEATURES)

			printf("Loading plugins...")
			loadPlugins()

			printf("Connecting...")
			if gClient.connect(secureMode=gConfig.SECURE, useResolver=gConfig.USE_RESOLVER):
				printf("Connection established (%s)" % gClient.connectType, FLAG_SUCCESS)
			else:
				printf("Unable to connect", FLAG_ERROR)
				if gConfig.RESTART_IF_ERROR:
					printf("Sleeping for %d seconds..." % RECONNECT_DELAY)
					time.sleep(RECONNECT_DELAY)
					shutdown(True)
				else:
					shutdown()

			printf("Waiting for authentication...")
			if gClient.auth(gConfig.USERNAME, gConfig.PASSWORD, gConfig.RESOURCE):
				printf("Connected", FLAG_SUCCESS)
			else:
				printf("Incorrect login/password", FLAG_ERROR)
				shutdown()

			callEventHandlers(EVT_STARTUP, MODE_ASYNC)
			clearEventHandlers(EVT_STARTUP)

			gClient.registerHandler("message", messageHandler)
			gClient.registerHandler("presence", presenceHandler)
			gClient.registerHandler("iq", iqHandler)

			gRoster = gClient.getRoster()
			gClient.setStatus = setStatus
			gClient.setStatus(None, None, gConfig.PRIORITY)

			path = getConfigPath(CONF_FILE)
			utils.createFile(path, "[]")
			conferences = eval(utils.readFile(path))
			if conferences:
				for conference in conferences:
					addConference(conference)
					joinConference(conference, getBotNick(conference), getConferenceConfigKey(conference, "password"))
					saveConferenceConfig(conference)
				printf("Entered in %d rooms" % (len(conferences)), FLAG_SUCCESS)

			callEventHandlers(EVT_READY, MODE_ASYNC)
			clearEventHandlers(EVT_READY)
			
			printf("Now I am ready to work :)")
			while True:
				gClient.process(10)
		except KeyboardInterrupt:
			if gClient.isConnected():
				prs = protocol.Presence(typ=protocol.PRS_OFFLINE)
				prs.setStatus(u"Выключаюсь... (CTRL+C)")
				gClient.send(prs)
			shutdown()
		except protocol.SystemShutdown:
			printf("%s has been switched off" % (gConfig.SERVER), FLAG_WARNING)
			shutdown()
		except protocol.Conflict:
			printf("Resource conflict", FLAG_WARNING)
			shutdown()
		except Exception:
			printf("Exception in main thread", FLAG_ERROR)
			addTextToSysLog(traceback.format_exc(), LOG_CRASHES)
			if gClient.isConnected():
				prs = protocol.Presence(typ=protocol.PRS_OFFLINE)
				prs.setStatus(u"Что-то сломано...")
				gClient.send(prs)
			shutdown(gConfig.RESTART_IF_ERROR)
	else:
		printf("Another instance is running (pid: %s)" % (pid), FLAG_ERROR)
