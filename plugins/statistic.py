# coding: utf-8

# statistic.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

gStats = {}
gJoined = {}
gLeaved = {}
gKicked = {}
gBanned = {}

def showStatistic(msgType, conference, nick, param):
	text = u"за время, проведённое мной в конфе, вы запостили %(groupchat)d мессаг в чат и %(chat)d мессаг мне в личку, "
	text += u"я же запостила %(mymsg)d сообщений. Всего сюда заходили %(join)d человек, из них %(moderator)d модеров, "
	text += u"%(participant)d участников и %(visitor)d посетителей. Вышло же %(leave)d человек; модеры выгнали %(kick)d человек и "
	text += u"забанили %(ban)d. Также ники сменили %(nick)d раз, статусами нафлудили %(status)d раз."
	sendMsg(msgType, conference, nick, text % (gStats[conference]))

def botMessageUpdate(msgType, conference, text):
	if(xmpp.TYPE_PUBLIC == msgType and text):
		gStats[conference]["mymsg"] += 1

def messageUpdate(stanza, msgType, conference, nick, trueJid, text):
	if(nick != getBotNick(conference)):
		gStats[conference][msgType] += 1
		if conference is None or msgType is None:
			print conference
			print msgType
			print text

def joinUpdate(conference, nick, trueJid, aff, role):
	if(not trueJid in gJoined[conference]):
		gJoined[conference].append(trueJid)
		gStats[conference]["join"] += 1
		gStats[conference][role] += 1

def leaveUpdate(conference, nick, trueJid, reason, code):
	if(not trueJid in gLeaved[conference]):
		gLeaved[conference].append(trueJid)
		gStats[conference]["leave"] += 1
	if(code == "307" and not trueJid in gKicked[conference]):
		gStats[conference]["kick"] += 1
		gKicked[conference].append(trueJid)
	elif(code == "301" and not trueJid in gBanned[conference]):
		gStats[conference]["ban"] += 1
		gBanned[conference].append(trueJid)

def presenceUpdate(stanza, conference, nick, trueJid):
	if("303" == stanza.getStatusCode()):
		gStats[conference]["nick"] += 1
	else:
		msgType = stanza.getType()
		if(msgType != xmpp.PRS_OFFLINE):
			gStats[conference]["status"] += 1
	
def initStatistic(conference):
	gStats[conference] = {
			"nick": 0, 
			"status": 0, 
			"kick": 0, 
			"ban": 0, 
			"join": 0, 
			"leave": 0, 
			"mymsg": 0, 
			xmpp.TYPE_PRIVATE: 0, 
			xmpp.TYPE_PUBLIC: 0, 
			xmpp.ROLE_MODERATOR: 0, 
			xmpp.ROLE_PARTICIPANT: 0, 
			xmpp.ROLE_VISITOR: 0
	}
	gJoined[conference] = []
	gLeaved[conference] = []
	gKicked[conference] = []
	gBanned[conference] = []

def freeStatistic(conference):
	del(gStats[conference])
	del(gJoined[conference])
	del(gLeaved[conference])
	del(gKicked[conference])
	del(gBanned[conference])

registerEvent(initStatistic, ADDCONF)
registerEvent(freeStatistic, DELCONF)
registerLeaveHandler(leaveUpdate)
registerJoinHandler(joinUpdate)
registerPresenceHandler(presenceUpdate, CHAT)
registerMessageHandler(messageUpdate, CHAT)
registerBotMessageHandler(botMessageUpdate)

registerCommand(showStatistic, u"статистика", 10, 
				u"Статистика текущей конференции", 
				None, 
				(u"статистика", ), 
				CHAT | NONPARAM)
