# coding: utf-8

# notices.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def noticeControl(msgType, conference, nick, param):
	if(param):
		if(param.isdigit()):
			param = int(param)
			if(param == 1):
				setConfigKey(conference, "notices", 1)
				sendMsg(msgType, conference, nick, u"оповещения включены")
			else:
				setConfigKey(conference, "notices", 0)
				sendMsg(msgType, conference, nick, u"оповещения выключены")
			saveConferenceConfig(conference)
		else:
			sendMsg(msgType, conference, nick, u"прочитай помощь по команде")
	else:
		sendMsg(msgType, conference, nick, u"текущее значение: %s" % (getConfigKey(conference, "popups")))

def sendNotices(msgType, conference, nick, param):
	conferences = getConferences()
	count = 0
	for conf in conferences:
		if(getConfigKey(conf, "notices")):
			sendToConference(conf, u"Новости от администрации:\n%s" % param)
			count += 1
	sendMsg(msgType, conference, nick, "сообщение ушло в %d конференций из %d" % (count, len(conferences)))

def setDefNoticeValue(conference):
	if(getConfigKey(conference, "notices") is None):
		setConfigKey(conference, "notices", 1)

registerEvent(setDefNoticeValue, ADDCONF)
registerCommand(noticeControl, u"оповещения", 30, 
				u"Отключает (0) или включает (1) сообщения о новостях. Без параметра покажет текущее значение", 
				u"оповещения [0|1]", 
				(u"оповещения", u"оповещения 0"), 
				CHAT)
registerCommand(sendNotices, u"оповещение", 100, 
				u"Отправляет сообщение по всем конференциям, в которых сидит бот", 
				u"оповещение <сообщение>", 
				(u"оповещение привет!11", ), 
				ANY | PARAM)
