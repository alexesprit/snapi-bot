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

def writeHeader(fp, jid, (year, month, day)):
	date = "%.2i.%.2i.%.2i" % (day, month, year)
	cssData = utils.readFile(getFilePath(CSS_DIR, LOGCSS_FILE))
	header = """<!DOCTYPE html protocol.TYPE_PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\"
\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dt\">
<head>
<title>%s</title>
<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />
<style msgType=\"text/css\">
<!--%s-->
</style>
</head>
<body>
<h1>%s<br>%s</h1>
<tt>
""" % (" - ".join([jid, date]), cssData, jid, date)
	fp.write(header.encode("utf-8"))

def getLogFile(msgType, jid, (year, month, day)):
	path = u"%s/%s/%d/%02d/%02d.html" % (gLogDir, jid, year, month, day)
	path = path.encode("utf-8")
	if os.path.exists(path):
		f = file(path, "a")
	else:
		dirName = os.path.dirname(path)
		if not os.path.exists(dirName):
			os.makedirs(dirName)
		f = file(path, "w")
		writeHeader(f, jid, (year, month, day))
	return f

def regexUrl(matchobj):
	url = matchobj.group(0)
	if LOGS_URL_NOINDEX:
		return "<noindex><a href=\"%s\">%s</a></noindex>" % (url, url)
	else:
		return "<a href=\"%s\">%s</a>" % (url, url)
	
def writeLog(msgType, jid, nick, body, aff = 0):
	decimal = str(int(math.modf(time.time())[0] * 100000))
	(year, month, day, hour, minute, second, weekday, yearday, daylightsavings) = time.localtime()
	body = utils.escapeXML(body)
	body = gURLPtrn.sub(regexUrl, body)
	body = body.replace("\n", "<br/>")
	body = body.encode("utf-8")
	nick = nick.encode("utf-8")
	timestamp = "%02d:%02d:%02d" % (hour, minute, second)
	link = timestamp + "." + decimal
	fp = getLogFile(msgType, jid, (year, month, day, ))
	fp.write("<span class=\"timestamp\"><a id=\"t%s\" href=\"#t%s\">[%s]</a></span>" % (link, link, timestamp))
	if not nick:
		fp.write("<span class=\"system\"> %s</span><br />\n" % (body))
	elif body.startswith("/me"):
		fp.write("<span class=\"emote\"> * %s%s</span><br />\n" % (nick, body[3:]))
	else:
		if nick.startswith("@$$"):
			className = nick[3:-3]
			fp.write("<span class=\"%s\"> %s</span><br />\n" % (className, body))
		else:
			if aff == 2:
				fp.write("<span class=\"owner\"> &lt;%s&gt;</span> %s<br />\n" % (nick, body))
			elif aff == 1:
				fp.write("<span class=\"admin\"> &lt;%s&gt;</span> %s<br />\n" % (nick, body))
			else:
				fp.write("<span class=\"self\"> &lt;%s&gt;</span> %s<br />\n" % (nick, body))
	fp.close()

def writeMessage(stanza, msgType, conference, nick, trueJid, text):
	if protocol.TYPE_PUBLIC == msgType and getConferenceConfigKey(conference, "log"):
		aff = 0
		if nick and getNickKey(conference, nick, NICK_MODER):
			level = getAccess(conference, trueJid)
			aff = (level >= 30) and 2 or 1
		writeLog(msgType, conference, nick, text, aff)

def writeUserJoin(conference, nick, trueJid, aff, role):
	if getConferenceConfigKey(conference, "log"):
		writeLog(protocol.TYPE_PUBLIC, conference, "@$$join$$@", u"%s заходит в комнату как %s и %s" % (nick, role, aff))

def writeUserLeave(conference, nick, trueJid, reason, code):
	if getConferenceConfigKey(conference, "log"):
		if "307" == code:
			if reason:
				writeLog(protocol.TYPE_PUBLIC, conference, "@$$kick$$@", u"%s выгнали из комнаты: %s" % (nick, reason))
			else:
				writeLog(protocol.TYPE_PUBLIC, conference, "@$$kick$$@", u"%s выгнали из комнаты" % (nick));		
		elif "301" == code:
			if reason:
				writeLog(protocol.TYPE_PUBLIC, conference, "@$$ban$$@", u"%s забанили: %s" % (nick, reason))
			else:
				writeLog(protocol.TYPE_PUBLIC, conference, "@$$ban$$@", u"%s забанили" % (nick));	
		else:
			if reason:
				writeLog(protocol.TYPE_PUBLIC, conference, "@$$leave$$@", u"%s выходит из комнаты: %s" % (nick, reason))
			else:
				writeLog(protocol.TYPE_PUBLIC, conference, "@$$leave$$@", u"%s выходит из комнаты" % (nick))

def writePresence(stanza, conference, nick, trueJid):
	if getConferenceConfigKey(conference, "log"):
		code = stanza.getStatusCode()
		prsType = stanza.getType()
		if code == "303":
			newnick = stanza.getNick()
			writeLog(protocol.TYPE_PUBLIC, conference, "@$$nick$$@", u"%s меняет ник на %s" % (nick, newnick))

def manageLoggingValue(msgType, conference, nick, param):
	if param:
		param = param.split()
		if len(param) == 2:
			conf, value = param
		elif len(param) == 1:
			conf, value = conference, param[0]
		else:
			sendMsg(msgType, conference, nick, u"Читай помощь по команде")
			return
		if not conferenceInList(conf):
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
		message = [u"%d) %s [%d]" % (i + 1, c, getConferenceConfigKey(c, "log")) 
					for i, c in enumerate(getConferences())]
		if message:
			sendMsg(msgType, conference, nick, "\n".join(message))
		else:
			sendMsg(msgType, conference, nick, u"Я пока нигде не сижу")

def setDefLoggingValue(conference):
	if getConferenceConfigKey(conference, "log") is None:
		setConferenceConfigKey(conference, "log", 1)

if gLogDir:
	registerJoinHandler(writeUserJoin)
	registerLeaveHandler(writeUserLeave)
	registerPresenceHandler(writePresence, CHAT)
	registerMessageHandler(writeMessage, CHAT)
registerEvent(setDefLoggingValue, ADDCONF);		
registerCommand(manageLoggingValue, u"логирование", 100, 
				u"Отключает (0) или включает (1) ведение логов для указанной/текущей конференции. Без параметра покажет значения для всех конференций, в которых сидит бот", 
				u"[<комната> <0|1>]", 
				(None, u"0", u"room@conference.server.tld 0"))
