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

LOGHEADER_FILE = "logheader.txt"

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

gLastLogDir = {}

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
		lastLogDir = gLastLogDir.get(conference)
		if lastLogDir:
			writeLogFooter(lastLogDir)		
		dirName = os.path.dirname(path)
		if not os.path.exists(dirName):
			os.makedirs(dirName)
		f = file(path, "w")
		writeLogHeader(f, conference, year, month, day)
	gLastLogDir[conference] = path
	return f

def regexUrl(matchobj):
	url = matchobj.group(0)
	return "<noindex><a href=\"%s\">%s</a></noindex>" % (url, url)

def writeLogFooter(logDir):
	if os.path.isfile(logDir):
		f = open(logDir, "a")
		f.write(u"</body>\n</html>")
		f.close()

def writeLogHeader(f, conference, year, month, day):
	date = "%02d.%02d.%2d" % (day, month, year)
	header = utils.readFile(getFilePath(RESOURCE_DIR, LOGHEADER_FILE))
	header = header.replace("%ROOM%", conference)
	header = header.replace("%DATE%", date)
	f.write(header.encode("utf-8"))

def addTextToLog(conference, nick, text, logtype=LOGTYPE_MSG):
	year, month, day, hour, minute, second = time.localtime()[:6]

	text = utils.escapeXML(text)
	text = URL_RE.sub(regexUrl, text)
	text = text.replace("\n", "<br/>")

	if text.startswith("/me"):
		rawtext = u"<span class=\"me\"> *%s%s</span><br/>" % (nick, text[3:])
	else:
		if logtype == LOGTYPE_MSG:
			aff = getNickKey(conference, nick, NICK_AFF)
			rawtext = u"<span class=\"%s\"> &lt;%s&gt;</span> %s<br/>" % (aff, nick, text)
		else:
			rawtext = u"<span class=\"%s\"> %s</span><br/>" % (logtype, text)

	timestamp = "%02d:%02d:%02d" % (hour, minute, second)

	fp = getLogFile(conference, year, month, day)
	fp.write("<span class=\"time\">[%s]</span>" % (timestamp))
	fp.write(rawtext.encode("utf-8"))
	fp.write("\n")
	fp.close()

def addMessageToLog(stanza, msgType, conference, nick, truejid, text):
	if protocol.TYPE_PUBLIC == msgType and getConferenceConfigKey(conference, "log"):
		if nick:
			addTextToLog(conference, nick, text)
		else:
			addTextToLog(conference, None, text, LOGTYPE_SYSTEM)

def addUserJoinToLog(conference, nick, truejid, aff, role):
	if getConferenceConfigKey(conference, "log"):
		addTextToLog(conference, None, u"*** %s заходит в комнату как %s и %s" % (nick, role, aff), LOGTYPE_JOIN)

def addUserLeaveToLog(conference, nick, truejid, reason, code):
	if getConferenceConfigKey(conference, "log"):
		if not code:
			if reason:
				addTextToLog(conference, None, u"*** %s выходит из комнаты: %s" % (nick, reason), LOGTYPE_LEAVE)
			else:
				addTextToLog(conference, None, u"*** %s выходит из комнаты" % (nick), LOGTYPE_LEAVE)
		elif "307" == code:
			if reason:
				addTextToLog(conference, None, u"*** %s выгнали из комнаты: %s" % (nick, reason), LOGTYPE_KICK)
			else:
				addTextToLog(conference, None, u"*** %s выгнали из комнаты" % (nick), LOGTYPE_KICK)
		elif "301" == code:
			if reason:
				addTextToLog(conference, None, u"*** %s забанили: %s" % (nick, reason), LOGTYPE_BAN)
			else:
				addTextToLog(conference, None, u"*** %s забанили" % (nick), LOGTYPE_BAN);

def addPresenceToLog(stanza, conference, nick, truejid):
	if protocol.TYPE_ERROR != stanza.getType():
		if getConferenceConfigKey(conference, "log"):
			code = stanza.getStatusCode()
			if code == "303":
				newnick = stanza.getNick()
				addTextToLog(conference, None, u"*** %s меняет ник на %s" % (nick, newnick), LOGTYPE_NICK)

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
