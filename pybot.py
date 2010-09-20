#!/usr/bin/python
# coding: utf-8;

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

from __future__ import with_statement;

import codecs;
import math;
import os;
import random;
import re;
import sys;
import threading;
import time;
import traceback;
import urllib;

import database;
import macros;
import simplejson;
import xmpp;

CSS_DIR = 'css';
CONFIG_DIR = 'config';
PLUGIN_DIR = 'plugins';
SYSLOG_DIR = 'syslogs';
RESOURCE_DIR = 'resource';

PID_FILE = 'pid.txt';
BOTCONFIG_FILE = 'config.py';

ACCESS_FILE = 'access.txt';
CONFIG_FILE = 'config.txt';
CONF_FILE = 'conferences.txt';
ERROR_FILE = '%Y.%m.%d_error.txt';
CRASH_FILE = '%Y.%m.%d_crash.txt';

FLAG_INFO = 'info';
FLAG_READ = 'read';
FLAG_WRITE = 'write';
FLAG_ERROR = 'error';
FLAG_WARNING = 'warning';
FLAG_SUCCESS = 'success';

ADDCONF = 0x1;
DELCONF = 0x2;
STARTUP = 0x3;
INIT_2 = 0x4;

CHAT = 1 << 1;
ROSTER = 1 << 2;
FROZEN = 1 << 3;
NONPARAM = 1 << 4;
PARAM = 1 << 5;
ANY = CHAT | ROSTER;

PRIVATE = 'chat';
PUBLIC = 'groupchat';
ERROR = 'error';
HEADLINE = 'headline';
NORMAL = 'normal';
RESULT = 'result';
UNAVAILABLE = 'unavailable';

NICK_JID = 'jid';
NICK_IDLE = 'idle';
NICK_HERE = 'here';
NICK_MODER = 'moder';
NICK_JOINED = 'joined';
NICK_SHOW = 'show';
NICK_STATUS = 'status';

ROLE_NONE = 'none';
ROLE_VISITOR = 'visitor';
ROLE_PARTICIPANT = 'participant';
ROLE_MODERATOR = 'moderator';

AFF_OUTCAST = 'outcast';
AFF_NONE = 'none';
AFF_MEMBER = 'member';
AFF_ADMIN = 'admin';
AFF_OWNER = 'owner';

ROLES = {
	ROLE_NONE: 0, 
	ROLE_VISITOR: 0, 
	ROLE_PARTICIPANT: 10, 
	ROLE_MODERATOR: 15
};

AFFILIATIONS = {
	AFF_OUTCAST: 0, 
	AFF_NONE: 0, 
	AFF_MEMBER: 1, 
	AFF_ADMIN: 5, 
	AFF_OWNER: 15
};

ESCAPE_MAP = {
	'&apos;': '\'',
	'&gt;': '>',
	'&lt;': '<',
	'&amp;': '&',
	'&quot;': '"',
	'&nbsp;': ' ',
	'&mdash;': '-'	
};

IDLE_TIMEOUT = 600;
JOIN_TIMEOUT = 5;
REJOIN_TIMEOUT = 120;
RETRY_TIMEOUT = 15;
RECONNECT_DELAY = 5;

CMD_DESC = 0x1;
CMD_ACCESS = 0x2;
CMD_SYNTAX = 0x3;
CMD_EXAMPLE = 0x4;
CMD_TYPE = 0x5;

os.chdir(os.path.dirname(sys.argv[0]));
execfile(BOTCONFIG_FILE) in globals();

gUserName, gServer = gJid.split('@');
gClient = xmpp.Client(server = gServer, port = gPort, debugFlags = gXmppDebug);
gRoster = None;
gDebug = xmpp.debug.Debug(gCoreDebug, validateFlags=False, prefix='', showFlags=False, welcomeMsg=False);
gTagPattern = re.compile('<(.*?)>');

gSemaphore = threading.BoundedSemaphore(30);

gInfo = {'start': 0, 'msg': 0, 'prs': 0, 'iq': 0, 'cmd': 0, 'thr': 0, 'err': 0, 'tmr': 0};
gVersion = ('Jimm', '0.6.4v [06.07.2010]', 'NokiaE51-1/0.34.011');

gBotMsgHandlers = [];
gJoinHandlers = [];
gLeaveHandlers = [];
gIqHandlers = [];
gCmdHandlers = {};

gEventHandlers = {ADDCONF: [], DELCONF: [], STARTUP: [], INIT_2: []};
gPresenceHandlers = {ROSTER: [], CHAT: []};
gMessageHandlers = {ROSTER: [], CHAT: []};

gGlobalAccess = {};
gTempAccess = {};
gPermAccess = {};

gCommands = {};
gCmdOff = {};
gMacros = macros.Macros();

gConferences = {};
gIsJoined = {};
gConfig = {};

gJokes = [];

gID = 0;

gDebug.debugFlags = (FLAG_INFO, FLAG_READ, FLAG_WRITE, FLAG_WARNING, FLAG_SUCCESS);
gDebug.colors[FLAG_INFO] = xmpp.debug.colorWhite;
gDebug.colors[FLAG_READ] = xmpp.debug.colorBrightBlue;
gDebug.colors[FLAG_WRITE] = xmpp.debug.colorPurple;
gDebug.colors[FLAG_ERROR] = xmpp.debug.colorBrightRed;
gDebug.colors[FLAG_WARNING] = xmpp.debug.colorYellow;
gDebug.colors[FLAG_SUCCESS] = xmpp.debug.colorBrightCyan;

def registerMessageHandler(function, msgType):
	gMessageHandlers[msgType].append(function);
	
def registerBotMessageHandler(function):
	gBotMsgHandlers.append(function);

def registerJoinHandler(function):
	gJoinHandlers.append(function);

def registerLeaveHandler(function):
	gLeaveHandlers.append(function);

def registerIqHandler(function):
	gIqHandlers.append(function);

def registerPresenceHandler(function, prsType):
	gPresenceHandlers[prsType].append(function);

def registerEvent(function, evtType):
	gEventHandlers[evtType].append(function);

def registerCommand(function, command, access, desc, syntax, examples, cmdType = ANY):
	gCmdHandlers[command] = function;
	gCommands[command] = {CMD_ACCESS: access, CMD_DESC: desc, CMD_SYNTAX: syntax, CMD_EXAMPLE: examples, CMD_TYPE: cmdType};

def callBotMessageHandlers(msgType, jid, text):
	for handler in gBotMsgHandlers:
		startThread(handler, (msgType, jid, text, ));

def callJoinHandlers(conference, nick, trueJid, aff, role):
	for handler in gJoinHandlers:
		startThread(handler, (conference, nick, trueJid, aff, role));

def callLeaveHandlers(conference, nick, trueJid, reason, code):
	for handler in gLeaveHandlers:
		startThread(handler, (conference, nick, trueJid, reason, code));

def callMessageHandlers(msgType, stanza, evtType, conference, nick, trueJid, body):
	gInfo['msg'] += 1;
	for handler in gMessageHandlers[evtType]:
		startThread(handler, (stanza, msgType, conference, nick, trueJid, body));

def callIqHandlers(stanza, jid, resource):
	gInfo['iq'] += 1;
	for handler in gIqHandlers:
		startThread(handler, (stanza, jid, resource));

def callPresenceHandlers(stanza, prsType, jid, resource, trueJid):
	gInfo['prs'] += 1;
	for handler in gPresenceHandlers[prsType]:
		startThread(handler, (stanza, jid, resource, trueJid));

def callEventHandlers(evtType, param = None):
	if(param):
		for function in gEventHandlers[evtType]:
			function(*param);
	else:
		for function in gEventHandlers[evtType]:
			function();		

def callCommandHandlers(command, cmdType, jid, resource, param):
	gInfo['cmd'] += 1;
	if(command in gCmdHandlers):
		startThread(gCmdHandlers[command], (cmdType, jid, resource, param));

def startThread(func, param = None):
	gInfo['thr'] += 1;
	if(param):
		threading.Thread(None, execute, func.__name__, (func, param)).start();
	else:
		threading.Thread(None, execute, func.__name__, (func, )).start();

def execute(function, param = None):
	try:
		if(param):
			with(gSemaphore):
				function(*param);
		else:
			with(gSemaphore):
				function();
	except(Exception):
		saveException(function.__name__);
		
def startTimer(timeout, func, param = None):
	gInfo['tmr'] += 1;
	if(param):
		timer = threading.Timer(timeout, func, param);
	else:
		timer = threading.Timer(timeout, func);
	timer.setName(func.__name__);
	timer.start();
	return(timer);

def getUsedMemory():
	if(os.name == 'posix'):
		try:
			pr = os.popen('ps -o rss -p %s' % os.getpid());
			pr.readline();
			return(float(pr.readline().strip()) / 1024);
		except(ValueError):
			pass;
	return(0);

def printf(text, flag = FLAG_INFO):
	gDebug.show(text, flag, flag);

def time2str(time):
	minutes, seconds = divmod(time, 60);
	hours, minutes = divmod(minutes, 60);
	days, hours = divmod(hours, 24);
	rep = '';
	if(seconds):
		rep = u'%d сек.' % (seconds);
	if(minutes):
		rep = u'%d мин. %s' % (minutes, rep);
	if(hours):
		rep = u'%d ч. %s' % (hours, rep);
	if(days):
		rep = u'%d дн. %s' % (days, rep);
	return(rep);

def XMLUnescape(s):
	for char in ESCAPE_MAP:
		s = s.replace(char, ESCAPE_MAP[char]);
	return(s);

def decode(text):
	text = gTagPattern.sub('', text.replace('<br />','\n').replace('<br>','\n'));
	return(XMLUnescape(text));

def createFile(path, data):
	path = path.encode('utf-8');
	if(not os.access(path, os.F_OK)):
		dirName = os.path.dirname(path);
		if(not os.path.exists(dirName)):
			os.makedirs(dirName);
		printf('Create: %s' % path, FLAG_WRITE);
		f = file(path, 'w');
		f.write(data);
		f.close();

def readFile(path, encoding = None):
	path = path.encode('utf-8');
	printf('Read: %s' % (path), FLAG_READ);
	f = file(path);
	data = f.read();
	f.close();
	if(encoding):
		data = data.decode(encoding);
	return(data);

def writeFile(path, data, mode = 'w'):
	path = path.encode('utf-8');
	printf('Write: %s' % (path), FLAG_WRITE);
	f = file(path, mode);
	f.write(data);
	f.close();

def getConfigPath(*param):
	return(os.path.join(CONFIG_DIR, *param));

def getFilePath(*param):
	return(os.path.join(*param));

def loadChatConfig(conference):
	fileName = getConfigPath(conference, CONFIG_FILE);
	createFile(fileName, '{}');
	gConfig[conference] = eval(readFile(fileName));

def saveChatConfig(conference):
	fileName = getConfigPath(conference, CONFIG_FILE);
	writeFile(fileName, str(gConfig[conference]));

def getConfigKey(conference, key):
	return(gConfig[conference].get(key));

def setConfigKey(conference, key, value):
	gConfig[conference][key] = value;

def joinConferences(conferences):
	for conference in conferences:
		joinConference(conference, getBotNick(conference), getConfigKey(conference, 'password'));
		saveChatConfig(conference);
	printf('Entered in %d rooms' % (len(conferences)), FLAG_SUCCESS);

def addConference(conference):
	gConferences[conference] = {};
	gIsJoined[conference] = False;
	writeFile(getConfigPath(CONF_FILE), str(gConferences.keys()));
	loadChatConfig(conference);
	for process in gEventHandlers[ADDCONF]:
		process(conference);

def delConference(conference):
	for function in gEventHandlers[DELCONF]:
		function(conference);
	del(gIsJoined[conference]);
	del(gConfig[conference]);
	del(gConferences[conference]);
	writeFile(getConfigPath(CONF_FILE), str(gConferences.keys()));

def joinConference(conference, nick, password):
	setConfigKey(conference, 'nick', nick);
	setConfigKey(conference, 'password', password);
	prs = xmpp.Presence(conference + '/' + nick, priority = gPriority);
	status = getConfigKey(conference, 'status');
	show = getConfigKey(conference, 'show');
	if(status):
		prs.setStatus(status);
	if(show):
		prs.setShow(show);
	prs.addChild(node = getCapsNode());
	mucTag = prs.setTag('x', namespace = xmpp.NS_MUC);
	mucTag.addChild('history', {'maxchars':'0'});
	if(password):
		mucTag.setTagData('password', password);
	gClient.send(prs);

def leaveConference(conference, status = None):
	prs = xmpp.Presence(conference, UNAVAILABLE);
	if(status):
		prs.setStatus(status);
	gClient.send(prs);
	delConference(conference);

def getBotNick(conference):
	if(conference in gConferences):
		return(getConfigKey(conference, 'nick') or gBotNick);
	return(gBotNick);
	
def getCapsNode():
	caps = xmpp.Node('c')
	caps.setNamespace(xmpp.NS_CAPS)
	caps.setAttr('node', 'http://jimm.net.ru/caps')
	caps.setAttr('ver', 'Nz009boXYEIrmRWk1N/Vsw==')
	caps.setAttr('hash', 'md5')
	return(caps);

def getUniqueID(text):
	global gID;
	gID += 1;
	return('%s_%d' % (text, gID));

def setRosterStatus(status, show, priority):
	prs = xmpp.Presence(priority = gPriority);
	if(status):
		prs.setStatus(status);
	if(show):
		prs.setShow(show);
	prs.addChild(node = getCapsNode());
	gClient.send(prs);

def setBotStatus(conference, status, show):
	prs = xmpp.Presence(conference, priority = gPriority);
	if(status):
		prs.setStatus(status);
	if(show):
		prs.setShow(show);
	prs.addChild(node = getCapsNode());
	gClient.send(prs);

def setRole(conference, nick, role, reason = None):
	iq = xmpp.Iq('set');
	iq.setTo(conference);
	query = xmpp.Node('query', {'xmlns': xmpp.NS_MUC_ADMIN});
	if(nick.count('@')):
		role = query.addChild('item', {'jid': nick, 'role': role});
	else:
		role = query.addChild('item', {'nick': nick, 'role': role});
	if(reason):
		role.setTagData('reason', reason);
	iq.addChild(node = query);
	gClient.send(iq);

def setAffiliation(conference, nick, aff, reason = None):
	iq = xmpp.Iq('set');
	iq.setTo(conference);
	query = xmpp.Node('query', {'xmlns': xmpp.NS_MUC_ADMIN});
	if(nick.count('@')):
		aff = query.addChild('item', {'jid': nick, 'affiliation': aff});
	else:
		aff = query.addChild('item', {'nick': nick, 'affiliation': aff});
	if(reason):
		aff.setTagData('reason', reason);
	iq.addChild(node = query);
	gClient.send(iq);

def isAdmin(jid):
	return(jid in gAdmins);

def isCommand(command):
	return(command in gCommands);

def isCommandType(command, cmdType):
	return(gCommands[command][CMD_TYPE] & cmdType);

def isAvailableCommand(conference, command):
	return(not(conference in gCmdOff and command in gCmdOff[conference]));

def getNicks(conference):
	return(gConferences[conference].keys());

def getOnlineNicks(conference):
	return([x for x in gConferences[conference] if(getNickKey(conference, x, NICK_HERE))]);

def getJidList(conference, offline = False):
	nicks = offline and getNicks(conference) or getOnlineNicks(conference);
	jidList = tuple(set([getTrueJid(conference,  nick) for nick in nicks]));
	return(jidList);
	
def getTrueJid(jid, resource = None):
	if(isinstance(jid, xmpp.JID)):
		jid = unicode(jid);
	if(not resource):
		if(jid.find('/') > -1):
			jid, resource = jid.split('/', 1);
	if(conferenceInList(jid)):
		if(nickInConference(jid, resource)):
			jid = getNickKey(jid, resource, 'jid');
	return(jid);

def getNickByJid(conference, trueJid, offline = False):
	nicks = offline and getNicks(conference) or getOnlineNicks(conference);
	for nick in nicks:
		if(getNickKey(conference, nick, NICK_JID) == trueJid):
			return(nick);
	return(None);

def getConferences():
	return(gConferences.keys());

def getNickKey(conference, nick, key):
	return(gConferences[conference][nick].get(key));

def setNickKey(conference, nick, key, value):
	gConferences[conference][nick][key] = value;

def conferenceInList(conference):
	return(conference in gConferences);

def nickInConference(conference, nick):
	return(nick in gConferences[conference]);

def nickIsOnline(conference, nick):
	return(nickInConference(conference, nick) and getNickKey(conference, nick, NICK_HERE));

def setTempAccess(conference, jid, level = 0):
	gTempAccess[conference][jid] = None;	
	if(level):
		gTempAccess[conference][jid] = level;
	else:
		del(gTempAccess[conference][jid]);

def setPermAccess(conference, jid, level = 0):
	fileName = getConfigPath(conference, ACCESS_FILE);
	gPermAccess[conference][jid] = None;
	if(level):
		gPermAccess[conference][jid] = level;
	else:
		del(gPermAccess[conference][jid]);
	writeFile(fileName, str(gPermAccess[conference]));

def setPermGlobalAccess(jid, level = 0):
	fileName = getConfigPath(ACCESS_FILE);
	tempAccess = eval(readFile(fileName));
	tempAccess[jid] = None;
	gGlobalAccess[jid] = None;
	if(level):
		tempAccess[jid] = level;
		gGlobalAccess[jid] = level;
	else:
		del(tempAccess[jid]);
		del(gGlobalAccess[jid]);
	writeFile(fileName, str(tempAccess));

def setTempGlobalAccess(jid, level = 0):
	gGlobalAccess[jid] = None;
	if(level):
		gGlobalAccess[jid] = level;
	else:
		del(gGlobalAccess[jid]);

def getAccess(conference, jid):
	if(jid in gGlobalAccess):
		return(gGlobalAccess[jid]);
	if(conference in gConferences):
		if(jid in gPermAccess[conference]):
			return(gPermAccess[conference][jid]);
		if(jid in gTempAccess[conference]):
			return(gTempAccess[conference][jid]);	
	else:
		return(11);
	return(0);

def sendTo(msgType, jid, text):
	message = xmpp.Message(jid);
	message.setType(msgType);
	text = text.strip();
	if(text):
		message.setBody(text);
	gClient.send(message);
	callBotMessageHandlers(msgType, jid, text);

def sendToConference(conference, text):
	sendTo(PUBLIC, conference, text);
		
def sendMsg(msgType, conference, nick, text, force = False):
	if(msgType == PUBLIC):
		fools = getConfigKey(conference, 'fools');
		if(fools and not random.randrange(0, 30)):
			text = random.choice(gJokes);
		elif(not force):
			msgLimit = getConfigKey(conference, 'msg');
			if(msgLimit and len(text) > msgLimit):
				sendMsg(msgType, conference, nick, u'смотри в привате (лимит %d символов)' % (msgLimit), True);
				msgType = PRIVATE;
	if(msgType == PUBLIC):
		text = u'%s: %s' % (nick, text);
		jid = conference;
	else:
		jid = u'%s/%s' % (conference, nick);
	sendTo(msgType, jid, text);

def messageHandler(session, stanza):
	msgType = stanza.getType();
	if(stanza.timestamp or HEADLINE == msgType or NORMAL == msgType):
		return;
	fullJid = stanza.getFrom();
	conference = fullJid.getStripped();
	isConference = conferenceInList(conference);
	if(PUBLIC == msgType and not isConference):
		return;
	trueJid = getTrueJid(fullJid);
	if(getAccess(conference, trueJid) == -100):
		return;
	message = stanza.getBody() or '';
	message = message.strip();
	if(ERROR == msgType):
		errorCode = stanza.getErrorCode();
		if(errorCode == u'500'):
			time.sleep(1);
			sendTo(PUBLIC, fullJid, message);
		elif(errorCode == '406'):
			joinConference(conference, gBotNick, getConfigKey(conference, 'password'));
			time.sleep(0.5);
			sendTo(PUBLIC, fullJid, message);
		return;
	if(not message):
		return;
	nick = fullJid.getResource();
	if(msgType == PUBLIC):
		if(nickInConference(conference, nick)):
			setNickKey(conference, nick, NICK_IDLE, time.time());
	else:
		if(stanza.getTags('request')):
			reportMsg = xmpp.Message(fullJid);
			reportMsg.setID(stanza.getID());
			reportMsg.addChild('received', {}, [], xmpp.NS_RECEIPTS);
			gClient.send(reportMsg);
	cmdType = isConference and CHAT or ROSTER;
	callMessageHandlers(msgType, stanza, cmdType, conference, nick, trueJid, message);
	if(isConference):
		botNick = getBotNick(conference);
		if(botNick == nick):
			return;
		if(message.startswith(botNick)):
			for x in [botNick + x for x in (':', ',')]:
				if(message.startswith(x)):
					message = message.replace(x, '').strip();
					break;
		prefix = getConfigKey(conference, 'prefix');
		if(prefix):
			if(message.startswith(prefix)):
				message = message[len(prefix):].strip();
			elif(msgType == PUBLIC):
				return;
		if(not message):
			return;
	rawBody = message.split(None, 1);
	command = rawBody[0].lower();
	if(isCommand(command)):
		access = gCommands[command][CMD_ACCESS];
	else:
		if(gMacros.hasMacros(command)):
			access = gMacros.getAccess(command);
		elif(isConference and gMacros.hasMacros(command, conference)):
			access = gMacros.getAccess(command, conference);
		else:
			return;
		message = gMacros.expand(message, (conference, nick, ), conference);
		rawBody = message.split(None, 1);
		command = rawBody[0].lower();
	if(isCommand(command) and isAvailableCommand(conference, command)):
		if(isCommandType(command, cmdType)):
			if(getAccess(conference, trueJid) >= access):
				param = (len(rawBody) == 2) and rawBody[1] or None;
				if(param and isCommandType(command, NONPARAM)):
					return;
				if(not param and isCommandType(command, PARAM)):
					return;
				callCommandHandlers(command, msgType, conference, nick, param);
			else:
				sendMsg(msgType, conference, nick, u'недостаточно прав');

def presenceHandler(session, stanza):
	fullJid = stanza.getFrom();
	prsType =  stanza.getType();
	jid = fullJid.getStripped();
	if(conferenceInList(jid)):
		conference = jid;
		trueJid = stanza.getJid();
		nick = fullJid.getResource();
		if(trueJid):
			trueJid = xmpp.JID(trueJid).getStripped();
		if(not prsType):
			if(not trueJid):
				sendToConference(conference, u'Без прав модератора работа невозможна!');
				leaveConference(conference);
				return;
			aff = stanza.getAffiliation();
			role = stanza.getRole();
			if(not nickIsOnline(conference, nick)):
				if(not nickInConference(conference, nick)):
					gConferences[conference][nick] = {};
				setNickKey(conference, nick, NICK_JID, trueJid);
				setNickKey(conference, nick, NICK_IDLE, time.time());
				setNickKey(conference, nick, NICK_HERE, True);
				setNickKey(conference, nick, NICK_JOINED, time.time());
				if(gIsJoined[conference]):
					callJoinHandlers(conference, nick, trueJid, aff, role);
				else:
					if(nick == getBotNick(conference)):
						gIsJoined[conference] = True;
			roleAccess = ROLES[role];
			affAccess = AFFILIATIONS[aff];
			setTempAccess(conference, trueJid, roleAccess + affAccess);
			setNickKey(conference, nick, NICK_MODER, role == ROLE_MODERATOR);
		elif(prsType == UNAVAILABLE):
			code = stanza.getStatusCode();
			reason = stanza.getReason() or stanza.getStatus();
			setNickKey(conference, nick, NICK_HERE, False);
			if(not getNickByJid(conference, trueJid)):
				setTempAccess(conference, trueJid);
			for key in (NICK_IDLE, NICK_MODER, NICK_STATUS, NICK_SHOW):
				if(key in gConferences[conference][nick]):
					del(gConferences[conference][nick][key]);
			callLeaveHandlers(conference, nick, trueJid, reason, code);
		elif(prsType == ERROR):
			errorCode = stanza.getErrorCode();
			if(errorCode == '409'):
				joinConference(conference, getBotNick(conference) + '.', getConfigKey(conference, 'password'));
			elif(errorCode == '404'):
				delConference(conference);
			elif(errorCode == '503'):
				startTimer(REJOIN_TIMEOUT, conference, (conference, getBotNick(conference), getConfigKey(conference, 'password'), ));
			elif(errorCode in ('401', '403', '405')):
				leaveConference(conference, u'got %s error code' % errorCode);
		callPresenceHandlers(stanza, CHAT, conference, nick, trueJid);
	else:
		resource = fullJid.getResource();
		callPresenceHandlers(stanza, ROSTER, jid, resource, None);

def iqHandler(session, stanza):
	fullJid = stanza.getFrom();
	bareJid = fullJid.getStripped();
	trueJid = getTrueJid(fullJid);
	if(getAccess(bareJid, trueJid) == -100):
		return;
	resource = fullJid.getResource();
	callIqHandlers(stanza, bareJid, resource);

def saveException(funcName):
	gInfo['err'] += 1;
	printf('Exception in %s function' % (funcName), FLAG_ERROR);
	fileName = getFilePath(SYSLOG_DIR, time.strftime(ERROR_FILE));
	writeFile(fileName, traceback.format_exc() + '\n', 'a');

def loadPlugins():
	printf('Loading plugins...');
	validPlugins = 0;
	invalidPlugins = 0;
	plugins = os.listdir(PLUGIN_DIR);
	for plugin in plugins:
		try:
			path = os.path.join(PLUGIN_DIR, plugin);
			if(os.path.isfile(path)):
				exec(file(path)) in globals();
				validPlugins += 1;
		except(SyntaxError, NameError):
			saveException('loadPlugins');
			invalidPlugins += 1;
	if(not invalidPlugins):
		printf('Loaded %d plugins' % (validPlugins), FLAG_SUCCESS);
	else:
		printf('Loaded %d plugins (%d with errors)' % (validPlugins, invalidPlugins), FLAG_WARNING);

def detectMultiLaunch():
	if(os.name == 'posix'):
		try:
			pid = int(readFile(PID_FILE));
			os.getsid(pid);
			return(pid);
		except(OSError, IOError):
			writeFile(PID_FILE, str(os.getpid()));
	return(None);

def restart():
	printf('Restarting...');
	time.sleep(RECONNECT_DELAY);
	if(os.path.exists(PID_FILE)):
		os.remove(PID_FILE);
	os.execl(sys.executable, sys.executable, sys.argv[0]);

def start():
	global gRoster;
	loadPlugins();

	printf('Connecting...');
	if(gClient.connect(server = (gHost, gPort), secure = 0, use_srv = True)):
		printf('Connection established (%s)' % gClient.isConnected().upper(), FLAG_SUCCESS);
	else:
		printf('Unable to connect', FLAG_ERROR);
		if(gRestart):
			printf('Sleeping for %d seconds...' % RETRY_TIMEOUT);
			time.sleep(RETRY_TIMEOUT);
			restart();
		else:
			os.abort();

	printf('Waiting For Authentication...');
	if(gClient.auth(gUserName, gPassword, gResource)):
		printf('Connected', FLAG_SUCCESS);
	else:
		printf('Incorrect login/password', FLAG_ERROR);
		os.abort();

	callEventHandlers(STARTUP);		
	gClient.RegisterHandler('message', messageHandler);
	gClient.RegisterHandler('presence', presenceHandler);
	gClient.RegisterHandler('iq', iqHandler);
	printf('Handlers Registered', FLAG_SUCCESS);

	gRoster = gClient.getRoster();
	setRosterStatus(None, None, gPriority);

	printf('Now I am ready to work :)');

	fileName = getConfigPath(CONF_FILE);
	createFile(fileName, '[]');
	conferences = eval(readFile(fileName));
	if(conferences):
		for conference in conferences:
			addConference(conference);
		startThread(joinConferences, (conferences, ));

	callEventHandlers(INIT_2);
	while(1):
		gClient.Process(10);

if(__name__ == '__main__'):
	try:
		pid = detectMultiLaunch();
		if(not pid):
			gInfo['start'] = time.time();
			start();
		else:
			printf('Another instance is running (pid: %s)' % (pid), FLAG_ERROR);
	except(KeyboardInterrupt):
		if(gClient.isConnected()):
			prs = xmpp.Presence(typ = UNAVAILABLE);
			prs.setStatus(u'выключаюсь (CTRL+C)');
			gClient.send(prs);
		os.abort();
	except(Exception):
		printf('Exception in main thread', FLAG_ERROR);
		fileName = getFilePath(SYSLOG_DIR, time.strftime(CRASH_FILE));
		writeFile(fileName, traceback.format_exc() + '\n', 'a');		
		if(gClient.isConnected()):
			prs = xmpp.Presence(typ = UNAVAILABLE);
			prs.setStatus(u'что-то сломалось...');
			gClient.send(prs);
		if(gRestart):
			restart();
		else:
			os.abort();
