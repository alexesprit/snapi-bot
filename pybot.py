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
import codecs, math, os, random, re, sys, threading, time, traceback, types, urllib;
import database, macros, simplejson, xmpp;

PLUGIN_DIR = 'plugins';
PID_FILE = 'pid.txt';
CONFIG_FILE = 'config.py';
CHATLIST_FILE = 'config/conferences.txt';
GLOBACCESS_FILE = 'config/access.txt';
PERMACCESS_FILE = 'config/%s/access.txt';
CHATCONFIG_FILE = 'config/%s/config.txt';
ERRORLOG_FILE = 'syslogs/%Y.%m.%d_error.txt';
CRASHLOG_FILE = 'syslogs/%Y.%m.%d_crash.txt';

FLAG_INFO = 'info';
FLAG_READ = 'read';
FLAG_WRITE = 'write';
FLAG_DEBUG = 'debug';
FLAG_ERROR = 'error';
FLAG_WARNING = 'warning';
FLAG_SUCCESS = 'success';

ADD_CHAT = 1 << 1;
DEL_CHAT = 1 << 2;
STARTUP = 1 << 3;
# TODO сделать норм. название
INIT_2 = 1 << 4;

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
RESULT = 'result';
UNAVAILABLE = 'unavailable';

NICK_JID = 'jid';
NICK_IDLE = 'idle';
NICK_HERE = 'here';
NICK_MODER = 'moder';
NICK_LEAVED = 'leaved';
NICK_JOINED = 'joined';

IDLE_TIMEOUT = 600;
JOIN_TIMEOUT = 5;
REJOIN_TIMEOUT = 120;
RETRY_TIMEOUT = 15;
RECONNECT_DELAY = 5;

os.chdir(os.path.dirname(sys.argv[0]));
execfile(CONFIG_FILE) in globals();

gUserName, gServer = gJid.split('@');
gClient = xmpp.Client(server = gServer, port = gPort, debug = gXmppDebug);
gRoster = None;
gDebug = xmpp.debug.Debug(gCoreDebug, validateFlags = False, prefix = '', showFlags = False, welcomeMsg = False);
gTagPattern = re.compile('<(.*?)>');

gSemaphore = threading.BoundedSemaphore();

gInfo = {'start': 0, 'msg': 0, 'prs': 0, 'iq': 0, 'cmd': 0, 'thr': 0, 'err': 0, 'tmr': 0};
gVersion = ('Jimm', '0.6.4v [06.07.2010]', 'NokiaE51-1/0.34.011');

gBotMsgHandlers = [];
gJoinHandlers = [];
gLeaveHandlers = [];
gIqHandlers = [];
gCmdHandlers = {};

gPluginHandlers = {ADD_CHAT: [], DEL_CHAT: [], STARTUP: [], INIT_2: []};
gPresenceHandlers = {ROSTER: [], CHAT: []};
gMsgHandlers = {ROSTER: [], CHAT: []};

gGlobalAccess = {};
gTempAccess = {};
gPermAccess = {};

gCommands = {};
gCmdOff = {};
gMacros = macros.Macros();

gChats = {};
gIsJoined = {};
gConfig = {};
gAutoAway = {};
gJokes = [];

gID = 0;

gDebug.debugFlags = (FLAG_INFO, FLAG_READ, FLAG_WRITE, FLAG_WARNING, FLAG_SUCCESS);
gDebug.colors[FLAG_INFO] = xmpp.Debug.colorWhite;
gDebug.colors[FLAG_READ] = xmpp.Debug.colorBrightBlue;
gDebug.colors[FLAG_WRITE] = xmpp.Debug.colorPurple;
gDebug.colors[FLAG_DEBUG] = xmpp.Debug.colorBrown;
gDebug.colors[FLAG_ERROR] = xmpp.Debug.colorBrightRed;
gDebug.colors[FLAG_WARNING] = xmpp.Debug.colorYellow;
gDebug.colors[FLAG_SUCCESS] = xmpp.Debug.colorBrightCyan;

def registerMessageHandler(instance, type):
	gMsgHandlers[type].append(instance);
	
def registerBotMessageHandler(instance):
	gBotMsgHandlers.append(instance);

def registerJoinHandler(instance):
	gJoinHandlers.append(instance);

def registerLeaveHandler(instance):
	gLeaveHandlers.append(instance);

def registerIqHandler(instance):
	gIqHandlers.append(instance);

def registerPresenceHandler(instance, type):
	gPresenceHandlers[type].append(instance);

def registerPluginHandler(instance, type):
	gPluginHandlers[type].append(instance);

def registerCommandHandler(instance, command, access, desc, syntax, examples, cmdType = ANY):
	printf(command, FLAG_ERROR);

def registerCommandHandler(instance, command, access, desc, syntax, examples, cmdType = ANY):
	gCmdHandlers[command] = instance;
	gCommands[command] = {'access': access, 'desc': desc, 'syntax': syntax, 'examples': examples, 'type': cmdType};

def callBotMessageHandlers(type, jid, text):
	for handler in gBotMsgHandlers:
		startThread(handler, (type, jid, text, ));

def callJoinHandlers(conference, nick, trueJid, aff, role):
	for handler in gJoinHandlers:
		startThread(handler, (conference, nick, trueJid, aff, role));

def callLeaveHandlers(conference, nick, trueJid, reason, code):
	for handler in gLeaveHandlers:
		startThread(handler, (conference, nick, trueJid, reason, code, ));

def callMessageHandlers(msgType, stanza, type, conference, nick, trueJid, body):
	gInfo['msg'] += 1;
	for handler in gMsgHandlers[msgType]:
		startThread(handler, (stanza, type, conference, nick, trueJid, body, ));

def callIqHandlers(stanza, jid, resource):
	gInfo['iq'] += 1;
	for handler in gIqHandlers:
		startThread(handler, (stanza, jid, resource, ));

def callPresenceHandlers(stanza, type, jid, resource, trueJid):
	gInfo['prs'] += 1;
	for handler in gPresenceHandlers[type]:
		startThread(handler, (stanza, jid, resource, trueJid, ));
	
def callCommandHandlers(command, type, jid, resource, param):
	gInfo['cmd'] += 1;
	if(command in gCmdHandlers):
		startThread(gCmdHandlers[command], (type, jid, resource, param, ));

def startThread(func, param = None):
	gInfo['thr'] += 1;
	if(param):
		threading.Thread(None, execute, func.__name__, (func, param)).start();
	else:
		threading.Thread(None, execute, func.__name__, (func, )).start();

def execute(instance, param = None):
	try:
		if(param):
			with(gSemaphore):
				instance(*param);
		else:
			with(gSemaphore):
				instance();
	except(Exception):
		errorHandler(instance.__name__);
		
def startTimer(timeout, func, param = None):
	gInfo['tmr'] += 1;
	if(param):
		timer = threading.Timer(timeout, func, param);
	else:
		timer = threading.Timer(timeout, func);
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
	s = s.replace('&apos;', '\'');
	s = s.replace('&gt;', '>');
	s = s.replace('&lt;', '<');
	s = s.replace('&amp;', '&');
	s = s.replace('&quot;', '"');
	return(s);

def decode(text):
	text = gTagPattern.sub('', text.replace('<br />','\n').replace('<br>','\n'));
	return(XMLUnescape(text));

def createFile(path, data):
	path = path.encode('utf-8');
	if(not os.access(path, os.F_OK)):
		dir = os.path.dirname(path);
		if(not os.path.exists(dir)):
			os.makedirs(dir);
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

def loadChatConfig(conference):
	fileName = CHATCONFIG_FILE % (conference);
	createFile(fileName, '{}');
	gConfig[conference] = eval(readFile(fileName));

def saveChatConfig(conference):
	fileName = CHATCONFIG_FILE % (conference);
	writeFile(fileName, str(gConfig[conference]));

def getConfigKey(conference, key):
	return(gConfig[conference].get(key));

def setConfigKey(conference, key, value):
	gConfig[conference][key] = value;

def joinConferences(conferences):
	for conference in conferences:
		addConference(conference);
		joinConference(conference, getBotNick(conference), getConfigKey(conference, 'password'));
		saveChatConfig(conference);
		time.sleep(JOIN_TIMEOUT);
	printf('Entered in %d rooms' % (len(conferences)), FLAG_SUCCESS);

def addConference(conference):
	gChats[conference] = {};
	gIsJoined[conference] = False;
	writeFile(CHATLIST_FILE, str(gChats.keys()));
	loadChatConfig(conference);
	for process in gPluginHandlers[ADD_CHAT]:
		process(conference);

def delConference(conference):
	if(getConfigKey(conference, CFG_AUTOAWAY)):
		stopAwayTimer(conference);
	for instance in gPluginHandlers[DEL_CHAT]:
		instance(conference);
	del(gIsJoined[conference]);
	del(gConfig[conference]);
	del(gChats[conference]);
	writeFile(CHATLIST_FILE, str(gChats.keys()));

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

def leaveconference(conference, status = None):
	prs = xmpp.Presence(conference, UNAVAILABLE);
	if(status):
		prs.setStatus(status);
	gClient.send(prs);
	delConference(conference);

def getBotNick(conference):
	if(conference in gChats):
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

def setBotStatus(conference, status, show, away = 0):
	prs = xmpp.Presence(conference, priority = gPriority);
	if(status):
		prs.setStatus(status);
	if(show):
		prs.setShow(show);
	prs.addChild(node = getCapsNode());
	gClient.send(prs);
	if(getConfigKey(conference, CFG_AUTOAWAY)):
		gAutoAway[conference]['away'] = away;
		
def hasAwayTimer(conference):
	return(conference in gAutoAway);
		
def createAwayTimer(conference):
	gAutoAway[conference] = {'away': 0, 'thr': None};
	resetAwayTimer(conference, False);
		
def resetAwayTimer(conference, cancel = True):
	if(cancel):
		gAutoAway[conference]['thr'].cancel();
	gAutoAway[conference]['thr'] = startTimer(IDLE_TIMEOUT, setBotStatus, (conference, time.strftime(u'I\'ve been away since %H:%M'), 'away', 1));
	
def stopAwayTimer(conference):
	gAutoAway[conference]['thr'].cancel();
	del(gAutoAway[conference]);	

def setRole(conference, nick, role, reason):
	iq = xmpp.Iq('set');
	iq.setTo(conference);
	query = xmpp.Node('query', {'xmlns': xmpp.NS_MUC_ADMIN});
	if(nick.count('@')):
		role = query.addChild('item', {'jid': nick, 'role': role});
	else:
		role = query.addChild('item', {'nick': nick, 'role': role});
	role.setTagData('reason', reason);
	iq.addChild(node = query);
	gClient.send(iq);

def setAffiliation(conference, nick, aff, reason):
	iq = xmpp.Iq('set');
	iq.setTo(conference);
	query = xmpp.Node('query', {'xmlns': xmpp.NS_MUC_ADMIN});
	if(nick.count('@')):
		aff = query.addChild('item', {'jid': nick, 'affiliation': aff});
	else:
		aff = query.addChild('item', {'nick': nick, 'affiliation': aff});
	aff.setTagData('reason', reason);
	iq.addChild(node = query);
	gClient.send(iq);

def isAdmin(jid):
	return(jid in gAdmins);

def isCommand(command):
	return(command in gCommands);

def isCommandType(command, type):
	return(gCommands[command]['type'] & type);

def isAvailableCommand(conference, command):
	return(not(conference in gCmdOff and command in gCmdOff[conference]));

def getNicks(conference):
	return(gChats[conference].keys());

def getOnlineNicks(conference):
	return([x for x in gChats[conference] if(getNickKey(conference, x, NICK_HERE))]);

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
	if(chatInList(jid)):
		if(nickInChat(jid, resource)):
			jid = getNickKey(jid, resource, 'jid');
	return(jid);

def getChatList():
	return(gChats.keys());

def getNickKey(conference, nick, key):
	return(gChats[conference][nick].get(key));

def setNickKey(conference, nick, key, value):
	gChats[conference][nick][key] = value;

def chatInList(conference):
	return(conference in gChats);

def nickInChat(conference, nick):
	return(nick in gChats[conference]);

def nickOnlineInChat(conference, nick):
	return(nickInChat(conference, nick) and getNickKey(conference, nick, NICK_HERE));

def setTempAccess(conference, jid, level = 0):
	gTempAccess[conference][jid] = None;	
	if(level):
		gTempAccess[conference][jid] = level;
	else:
		del(gTempAccess[conference][jid]);

def setPermAccess(conference, jid, level = 0):
	gPermAccess[conference][jid] = None;
	if(level):
		gPermAccess[conference][jid] = level;
	else:
		del(gPermAccess[conference][jid]);
	writeFile(PERMACCESS_FILE % conference, str(gPermAccess[conference]));

def setPermGlobalAccess(jid, level = 0):
	tempAccess = eval(readFile(GLOBACCESS_FILE));
	tempAccess[jid] = None;
	gGlobalAccess[jid] = None;
	if(level):
		tempAccess[jid] = level;
		gGlobalAccess[jid] = level;
	else:
		del(tempAccess[jid]);
		del(gGlobalAccess[jid]);
	writeFile(GLOBACCESS_FILE, str(tempAccess));

def setTempGlobalAccess(jid, level = 0):
	gGlobalAccess[jid] = None;
	if(level):
		gGlobalAccess[jid] = level;
	else:
		del(gGlobalAccess[jid]);

def getAccess(conference, jid):
	if(jid in gGlobalAccess):
		return(gGlobalAccess[jid]);
	if(conference in gChats):
		if(jid in gPermAccess[conference]):
			return(gPermAccess[conference][jid]);
		if(jid in gTempAccess[conference]):
			return(gTempAccess[conference][jid]);	
	else:
		return(11);
	return(0);

def sendTo(type, jid, text):
	message = xmpp.Message(jid);
	message.setType(type);
	text = text.strip();
	if(text):
		message.setBody(text);
	gClient.send(message);
	callBotMessageHandlers(type, jid, text);

def sendToConference(conference, text):
	sendTo(PUBLIC, conference, text);
		
def sendMsg(type, conference, nick, text, force = False):
	if(type == PUBLIC):
		fools = getConfigKey(conference, 'fools');
		if(fools and not random.randrange(0, 30)):
			text = random.choice(gJokes);
		elif(not force):
			msgLimit = getConfigKey(conference, 'msg');
			if(msgLimit and len(text) > msgLimit):
				sendMsg(type, conference, nick, u'смотри в привате (лимит %d символов)' % (msgLimit), True);
				type = PRIVATE;
	if(type == PUBLIC):
		text = u'%s: %s' % (nick, text);
		jid = conference;
	else:
		jid = u'%s/%s' % (conference, nick);
	sendTo(type, jid, text);

def messageHandler(session, stanza):
	type = stanza.getType();
	# FIXME check 'headline' type
	if(stanza.timestamp or HEADLINE == type or 'normal' == type):
		return;
	fullJid = stanza.getFrom();
	trueJid = getTrueJid(fullJid);
	conference = fullJid.getStripped();
	if(getAccess(conference, trueJid) == -100):
		return;
	message = stanza.getBody() or '';
	message = message.strip();
	if(not message):
		return;
	isConference = chatInList(conference);
	nick = fullJid.getResource();
	msgType = isConference and CHAT or ROSTER;
	if(type == PUBLIC and nick):
		setNickKey(conference, nick, 'idle', time.time());
	elif(type == ERROR):
		errorCode = stanza.getErrorCode();
		if(errorCode == '500'):
			time.sleep(0.5);
			gClient.send(xmpp.Message(fullJid, message, PUBLIC));
		elif(errorCode == '406'):
			joinConference(conference, gBotNick, getConfigKey(conference, 'password'));
			time.sleep(0.5);
			gClient.send(xmpp.Message(fullJid, message, PUBLIC));
		return;
	else:
		if(stanza.getTags('request')):
			reportMsg = xmpp.Message(fullJid);
			reportMsg.setID(stanza.getID());
			reportMsg.addChild('received', {}, [], xmpp.NS_RECEIPTS);
			gClient.send(reportMsg);
	callMessageHandlers(msgType, stanza, type, conference, nick, trueJid, message);
	if(isConference):
		botNick = getBotNick(conference);
		if(botNick == nick):
			return;
		if(message.startswith(botNick)):
			for x in [botNick + x for x in (':', ',')]:
				if(message.startswith(x)):
					message = message.replace(x, '').strip();
		prefix = getConfigKey(conference, 'prefix');
		if(prefix):
			if(message.startswith(prefix)):
				message = message[len(prefix):].strip();
				if(not message):
					return;
			elif(type == PUBLIC):
				return;
	body = message.split();
	command = body[0].lower();
	if(isCommand(command)):
		access = gCommands[command]['access'];
	else:
		if(gMacros.hasMacros(command)):
			access = gMacros.getAccess(command);
		elif(isConference and gMacros.hasMacros(command, conference)):
			access = gMacros.getAccess(command, conference);
		else:
			return;
		body = gMacros.expand(message, (conference, nick, ), conference).split();
		command = body[0].lower();
		if(not isAvailableCommand(conference, command)):
			return;
	if(isAvailableCommand(conference, command)):
		if(isCommandType(command, msgType)):
			if(getAccess(conference, trueJid) >= access):
				param = (len(body) > 1) and ' '.join(body[1:]) or None;
				if(param and isCommandType(command, NONPARAM)):
					return;
				if(not param and isCommandType(command, PARAM)):
					return;
				if(isConference):
					if(getConfigKey(conference, 'autoaway')):
						if(gAutoAway[conference]['away']):
							setBotStatus(conference, getConfigKey(conference, 'status'), getConfigKey(conference, 'show'));
						resetAwayTimer(conference);
				callCommandHandlers(command, type, conference, nick, param);
			else:
				sendMsg(type, conference, nick, u'недостаточно прав');

def presenceHandler(session, stanza):
	fullJid = stanza.getFrom();
	trueJid = getTrueJid(fullJid);
	conference = fullJid.getStripped();
	if(getAccess(conference, trueJid) == -100):
		return;
	nick = fullJid.getResource();
	prsType =  stanza.getType();
	if(chatInList(conference)):
		trueJid = stanza.getJid();
		if(trueJid):
			trueJid = xmpp.JID(trueJid).getStripped();
		# FIXME check for type;
		if(not prsType):
			if(not trueJid):
				sendToConference(conference, u'Без прав модератора работа невозможна!');
				leaveconference(conference);
				return;
			if(not nickOnlineInChat(conference, nick)):
				aff = stanza.getAffiliation();
				role = stanza.getRole();
				if(not nickInChat(conference, nick)):
					gChats[conference][nick] = {};
				setNickKey(conference, nick, NICK_JID, trueJid);
				setNickKey(conference, nick, NICK_IDLE, time.time());
				setNickKey(conference, nick, NICK_HERE, True);
				setNickKey(conference, nick, NICK_JOINED, time.time());
				if(gIsJoined[conference]):
					callJoinHandlers(conference, nick, trueJid, aff, role);
				else:
					if(nick == getBotNick(conference)):
						gIsJoined[conference] = True;
			role = stanza.getRole();
			setNickKey(conference, nick, NICK_MODER, role == ROLE_MODERATOR);
		elif(prsType == 'unavailable'):
			code = stanza.getStatusCode();
			reason = stanza.getReason() or stanza.getStatus();
			if(code == '303'):
				newNick = stanza.getNick();
				nickData = gChats[conference][nick];
				gChats[conference][newNick] = nickData;
				setNickKey(conference, newNick, NICK_IDLE, time.time());
			setNickKey(conference, nick, NICK_HERE, False);
			setNickKey(conference, nick, NICK_LEAVED, time.time());
			for key in (NICK_IDLE, NICK_MODER, 'status', 'stmsg',):
				if(key in gChats[conference][nick]):
					del(gChats[conference][nick][key]);
			callLeaveHandlers(conference, nick, trueJid, reason, code);
		elif(prsType == ERROR):
			errorCode = stanza.getErrorCode();
			if(errorCode == '409'):
				joinConference(conference, getBotNick(conference) + '.', getConfigKey(conference, 'password'));
			elif(errorCode == '404'):
				delConference(conference);
			elif(errorCode == '503'):
				startTimer(REJOIN_TIMEOUT, conference, (conference, getBotNick(conference), getConfigKey(conference, 'password')));
			elif(errorCode in ('401', '403', '405')):
				leaveconference(conference, u'got %s error code' % errorCode);
		callPresenceHandlers(stanza, CHAT, conference, nick, trueJid);
	else:
		callPresenceHandlers(stanza, ROSTER, conference, nick, trueJid);

def iqHandler(session, stanza):
	fullJid = stanza.getFrom();
	trueJid = getTrueJid(fullJid);
	bareJid = fullJid.getStripped();
	resource = fullJid.getResource()
	if(getAccess(bareJid, trueJid) == -100):
		return;
	callIqHandlers(stanza, bareJid, resource);

def errorHandler(funcName):
	gInfo['err'] += 1;
	printf('Exception in %s function' % (funcName), FLAG_ERROR);
	fileName = time.strftime(ERRORLOG_FILE);
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
			errorHandler('loadPlugins');
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
		sys.exit(1);

	printf('Waiting For Authentication...');
	if(gClient.auth(gUserName, gPassword, gResource)):
		printf('Connected', FLAG_SUCCESS);
	else:
		printf('Incorrect login/password', FLAG_ERROR);
		os.abort();

	for process in gPluginHandlers[STARTUP]:
		startThread(process);
		
	gClient.RegisterHandler('message', messageHandler);
	gClient.RegisterHandler('presence', presenceHandler);
	gClient.RegisterHandler('iq', iqHandler);
	printf('Handlers Registered', FLAG_SUCCESS);

	setRosterStatus(None, None, gPriority);
	gRoster = gClient.getRoster();

	printf('Now I am ready to work :)');

	createFile(CHATLIST_FILE, '[]');
	conferences = eval(readFile(CHATLIST_FILE));
	if(conferences):
		startThread(joinConferences, (conferences, ));

	for process in gPluginHandlers[INIT_2]:
		startThread(process);
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
	except(SystemExit):
		if(gRestart):
			restart();
	except(Exception):
		printf('Exception in main thread', FLAG_ERROR);
		fileName = time.strftime(CRASHLOG_FILE);
		writeFile(fileName, traceback.format_exc() + '\n', 'a');		
		if(gRestart):
			if(gClient.isConnected()):
				prs = xmpp.Presence(typ = UNAVAILABLE);
				prs.setStatus(u'что-то сломалось...');
				gClient.send(prs);
			restart();
