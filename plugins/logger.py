# coding: utf-8

# logger.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

LOGCSS_FILE = "logger.css"

LOGS_URL_NOINDEX = True

LOGTYPE_MSG = "msg"
LOGTYPE_SYSTEM = "system"
LOGTYPE_JOIN = "join"
LOGTYPE_LEAVE = "leave"
LOGTYPE_NICK = "nick"
LOGTYPE_KICK = "kick"
LOGTYPE_BAN = "ban"

LOGTYPES = (
	LOGTYPE_SYSTEM,
	LOGTYPE_JOIN,
	LOGTYPE_LEAVE,
	LOGTYPE_NICK,
	LOGTYPE_KICK,
	LOGTYPE_BAN
)

def setDefaultLoggingValue(conference):
	if getConferenceConfigKey(conference, "log") is None:
		setConferenceConfigKey(conference, "log", 1)

def manageLoggingValue(msgType, conference, nick, param):
	if param:
		args = param.split()
		if len(args) == 2:
			conf, value = args
		elif len(args) == 1:
			conf, value = conference, args[0]
		else:
			sendMsg(msgType, conference, nick, u"Читай помощь по команде")
			return
		if not isConferenceInList(conf):
			sendMsg(msgType, conference, nick, u"Я не сижу в этой конференции!")
			return
		if value.isdigit():
			value = int(value)
			if value == 1:
				setConferenceConfigKey(conf, "log", 1)
				if conf != conference:
					sendMsg(msgType, conference, nick, u"Логирование в %s включено" % (conf))
				else:
					sendMsg(msgType, conference, nick, u"Логирование включено")
			else:
				setConferenceConfigKey(conf, "log", 0)
				if conf != conference:
					sendMsg(msgType, conference, nick, u"Логирование в %s отключено" % (conf))
				else:
					sendMsg(msgType, conference, nick, u"Логирование отключено")
			saveConferenceConfig(conf)
		else:
			sendMsg(msgType, conference, nick, u"читай помощь по команде")
	else:
		conferences = getConferences()
		if conferences:
			elements = [u"%d) %s [%d]" % (i + 1, c, getConferenceConfigKey(c, "log"))
						for i, c in enumerate(sorted(conferences))]
			sendMsg(msgType, conference, nick, u"Список конференций:\n%s" % ("\n".join(elements)))
		else:
			sendMsg(msgType, conference, nick, u"Сейчас меня нет ни в одной конференции")

def getLogFile(conference, year, month, day):
	path = u"%s/%s/%d/%02d/%02d.html" % (Config.LOGGER_DIR, conference, year, month, day)
	path = path.encode("utf-8")
	if os.path.exists(path):
		f = file(path, "a")
	else:
		dirName = os.path.dirname(path)
		if not os.path.exists(dirName):
			os.makedirs(dirName)
		f = file(path, "w")
		writeLogHeader(f, conference, year, month, day)
	return f

def regexUrl(matchobj):
	url = matchobj.group(0)
	if LOGS_URL_NOINDEX:
		return "<noindex><a href=\"%s\">%s</a></noindex>" % (url, url)
	else:
		return "<a href=\"%s\">%s</a>" % (url, url)

def writeLogHeader(f, conference, year, month, day):
	date = "%.2i.%.2i.%.2i" % (day, month, year)
	cssdata = utils.readFile(getFilePath(RESOURCE_DIR, LOGCSS_FILE))
	header = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>%s</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style type="text/css">
<!--%s-->
</style>
</head>
<body>
<h1>%s<br/>%s</h1>
<div>
<tt>
""" % (" - ".join([conference, date]), cssdata, conference, date)
	f.write(header.encode("utf-8"))

def addTextToLog(logtype, conference, nick, text, aff=None):
	year, month, day, hour, minute, second = time.localtime()[:6]

	text = utils.escapeXML(text)
	text = URL_RE.sub(regexUrl, text)
	text = text.replace("\n", "<br/>")

	if text.startswith("/me"):
		rawtext = u"<span class=\"me\"> *%s%s</span><br/>" % (nick, text[3:])
	else:
		if logtype in LOGTYPES:
			rawtext = u"<span class=\"%s\"> %s</span><br/>" % (logtype, text)
		else:
			rawtext = u"<span class=\"%s\"> &lt;%s&gt;</span> %s<br/>" % (aff, nick, text)

	timestamp = "%02d:%02d:%02d" % (hour, minute, second)

	fp = getLogFile(conference, year, month, day)
	fp.write("<span class=\"time\">[%s]</span>" % (timestamp))
	fp.write(rawtext.encode("utf-8"))
	fp.write("\n")
	fp.close()

def addMessageToLog(stanza, msgType, conference, nick, truejid, text):
	if protocol.TYPE_PUBLIC == msgType and getConferenceConfigKey(conference, "log"):
		if truejid != conference:
			aff = getNickKey(conference, nick, NICK_AFF)
			addTextToLog(LOGTYPE_MSG, conference, nick, text, aff)
		else:
			addTextToLog(LOGTYPE_SYSTEM, conference, None, text)

def addUserJoinToLog(conference, nick, truejid, aff, role):
	if getConferenceConfigKey(conference, "log"):
		addTextToLog(LOGTYPE_JOIN, conference, None, u"*** %s заходит в комнату как %s и %s" % (nick, role, aff))

def addUserLeaveToLog(conference, nick, truejid, reason, code):
	if getConferenceConfigKey(conference, "log"):
		if not code:
			if reason:
				addTextToLog(LOGTYPE_LEAVE, conference, None, u"*** %s выходит из комнаты: %s" % (nick, reason))
			else:
				addTextToLog(LOGTYPE_LEAVE, conference, None, u"*** %s выходит из комнаты" % (nick))
		elif "307" == code:
			if reason:
				addTextToLog(LOGTYPE_KICK, conference, None, u"*** %s выгнали из комнаты: %s" % (nick, reason))
			else:
				addTextToLog(LOGTYPE_KICK, conference, None, u"*** %s выгнали из комнаты" % (nick));
		elif "301" == code:
			if reason:
				addTextToLog(LOGTYPE_BAN, conference, None, u"*** %s забанили: %s" % (nick, reason))
			else:
				addTextToLog(LOGTYPE_BAN, conference, None, u"*** %s забанили" % (nick));

def addPresenceToLog(stanza, conference, nick, truejid):
	if protocol.TYPE_ERROR != stanza.getType():
		if getConferenceConfigKey(conference, "log"):
			code = stanza.getStatusCode()
			if code == "303":
				newnick = stanza.getNick()
				addTextToLog(LOGTYPE_NICK, conference, None, u"*** %s меняет ник на %s" % (nick, newnick))

if Config.LOGGER_DIR:
	registerEventHandler(addUserJoinToLog, EVT_USERJOIN)
	registerEventHandler(addUserLeaveToLog, EVT_USERLEAVE)

	registerEventHandler(addMessageToLog, EVT_MSG | H_CONFERENCE)
	registerEventHandler(addPresenceToLog, EVT_PRS | H_CONFERENCE)

	registerEventHandler(setDefaultLoggingValue, EVT_ADDCONFERENCE)

	registerCommand(manageLoggingValue, u"логирование", 100,
				u"Отключает (0) или включает (1) ведение логов для указанной/текущей конференции. Без параметра покажет значения для всех конференций, в которых находится бот",
				u"[<конференция> <0|1>]",
				(None, u"0", u"room@conference.server.tld 0"))
