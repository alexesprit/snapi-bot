# coding: utf-8;

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

LOGCSS_FILE = "logger.css";

def writeHeader(fp, jid, (year, month, day)):
	date = u'%.2i.%.2i.%.2i' % (day, month, year);
	cssData = readFile(getFilePath(CSS_DIR, LOGCSS_FILE));
	fp.write(u'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dt">
<head>
<title>%s</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style msgType="text/css">
<!--%s-->
</style>
</head>
<body>
<h1>%s<br>%s</h1>
<tt>
''' % (u' - '.join([jid, date]), cssData, jid, date));

def getLogFile(msgType, jid, (year, month, day)):
	fileName = u'%s/%s/%d/%02d/%02d.html' % (gLogDir, jid, year, month, day);
	fileName = fileName.encode('utf-8');
	if(os.path.exists(fileName)):
		fp = file(fileName, 'a');
	else:
		createFile(fileName, '');
		fp = file(fileName, 'w');
		writeHeader(fp, jid, (year, month, day));
	return(fp);

def regexUrl(matchobj):
	return('<a href="' + matchobj.group(0) + '">' + matchobj.group(0) + '</a>');
	
def writeLog(msgType, jid, nick, body, aff = 0):
	decimal = str(int(math.modf(time.time())[0] * 100000));
	(year, month, day, hour, minute, second, weekday, yearday, daylightsavings) = time.localtime();
	body = xmpp.simplexml.XMLescape(body);
	body = re.sub('(http|ftp)(\:\/\/[^\s<]+)', regexUrl, body);
	body = body.replace('\n', '<br/>');
	body = body.encode('utf-8');
	nick = nick.encode('utf-8');
	timestamp = '%02d:%02d:%02d' % (hour, minute, second);
	link = timestamp + '.' + decimal;
	fp = getLogFile(msgType, jid, (year, month, day, ));
	fp.write('<span class="timestamp"><a id="t%s" href="#t%s">[%s]</a></span>' % (link, link, timestamp));
	if(not nick):
		fp.write('<span class="system"> ' + body + '</span><br />\n')
	elif(body.startswith('/me')):
		fp.write('<span class="emote"> * %s%s</span><br />\n' % (nick, body[3:]));
	else:
		if(nick.startswith('@$$')):
			className = nick[3:-3];
			fp.write('<span class="%s"> %s</span><br />\n' % (className, body));
		else:
			if(aff == 2):
				fp.write('<span class="owner"> &lt;%s&gt;</span> %s<br />\n' % (nick, body));
			elif(aff == 1):
				fp.write('<span class="admin"> &lt;%s&gt;</span> %s<br />\n' % (nick, body));
			else:
				fp.write('<span class="self"> &lt;%s&gt;</span> %s<br />\n' % (nick, body));
	fp.close();

def writeMessage(stanza, msgType, conference, nick, trueJid, text):
	if(PUBLIC == msgType and getConfigKey(conference, "log")):
		aff = 0;
		if(nick and getNickKey(conference, nick, NICK_MODER)):
			level = getAccess(conference, trueJid);
			aff = (level >= 30) and 2 or 1;
		writeLog(msgType, conference, nick, text, aff);

def writeUserJoin(conference, nick, trueJid, aff, role):
	if(getConfigKey(conference, "log")):
		writeLog(PUBLIC, conference, '@$$join$$@', u'%s зашёл в комнату как %s и %s' % (nick, role, aff));

def writeUserLeave(conference, nick, trueJid, reason, code):
	if(getConfigKey(conference, "log")):
		if('307' == code):
			if(reason):
				writeLog(PUBLIC, conference, '@$$kick$$@', u'%s выгнали из комнаты (%s)' % (nick, reason));
			else:
				writeLog(PUBLIC, conference, '@$$kick$$@', u'%s выгнали из комнаты' % (nick));		
		elif('301' == code ):
			if(reason):
				writeLog(PUBLIC, conference, '@$$ban$$@', u'%s забанили (%s)' % (nick, reason));
			else:
				writeLog(PUBLIC, conference, '@$$ban$$@', '@$$userban$$@');	
		elif('303' != code):
			if(reason):
				writeLog(PUBLIC, conference, '@$$leave$$@', u'%s вышел из комнаты (%s)' % (nick, reason));
			else:
				writeLog(PUBLIC, conference, '@$$leave$$@', u'%s вышел из комнаты' % (nick));

def writePresence(stanza, conference, nick, trueJid):
	if(getConfigKey(conference, "log")):
		code = stanza.getStatusCode();
		prsType = stanza.getType();
		if(code == '303'):
			newnick = stanza.getNick();
			writeLog(PUBLIC, conference, '@$$nick$$@', u'%s сменил ник на %s' % (nick, newnick));

def loggingControl(msgType, conference, nick, param):
	if(param):
		if(param.isdigit()):
			param = int(param);
			if(param == 1):
				setConfigKey(conference, "log", 1);
				sendMsg(msgType, conference, nick, u'логирование включено');
			else:
				setConfigKey(conference, "log", 0);
				sendMsg(msgType, conference, nick, u'логирование отключено');
			saveChatConfig(conference);
		else:
			sendMsg(msgType, conference, nick, u'прочитай помощь по команде');
	else:
		loggerValue = getConfigKey(conference, "log");
		sendMsg(msgType, conference, nick, u'текущее значение: %d' % (loggerValue));

def setLoggingState(conference):
	if(getConfigKey(conference, "log") is None):
		setConfigKey(conference, "log", 1);

if(gLogDir):
	registerJoinHandler(writeUserJoin);
	registerLeaveHandler(writeUserLeave);
	registerPresenceHandler(writePresence, CHAT);
	registerMessageHandler(writeMessage, CHAT);
registerEvent(setLoggingState, ADDCONF);		
registerCommand(loggingControl, u'логирование', 30, 'Отключает (0) или включает (1) ведение логов. Без параметра покажет текущее значение','логирование [0/1]', ('логирование', 'логирование 0'), CHAT);
