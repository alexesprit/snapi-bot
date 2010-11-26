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

gConferenceStats = {}
gStatsJoined = {}
gStatsLeaved = {}
gStatsKicked = {}
gStatsBanned = {}

def showConferenceStats(msgType, conference, nick, param):
	text = u"За время, проведённое мной в конфе, вы запостили %(groupchat)d мессаг в чат и %(chat)d мессаг мне в личку, "
	text += u"я же запостила %(mymsg)d сообщений. Всего сюда заходили %(join)d человек, из них %(moderator)d модеров, "
	text += u"%(participant)d участников и %(visitor)d посетителей. Вышло же %(leave)d человек; модеры выгнали %(kick)d человек и "
	text += u"забанили %(ban)d. Также ники сменили %(nick)d раз, статусами нафлудили %(status)d раз."
	sendMsg(msgType, conference, nick, text % (gConferenceStats[conference]))

def updateBotMessageStats(msgType, conference, text):
	if protocol.TYPE_PUBLIC == msgType and text:
		gConferenceStats[conference]["mymsg"] += 1

def updateMessageStats(stanza, msgType, conference, nick, trueJid, text):
	if nick != getBotNick(conference):
		gConferenceStats[conference][msgType] += 1

def updateJoinStats(conference, nick, trueJid, aff, role):
	if not trueJid in gStatsJoined[conference]:
		gStatsJoined[conference].append(trueJid)
		gConferenceStats[conference]["join"] += 1
		gConferenceStats[conference][role] += 1

def updateLeaveStats(conference, nick, trueJid, reason, code):
	if not trueJid in gStatsLeaved[conference]:
		gStatsLeaved[conference].append(trueJid)
		gConferenceStats[conference]["leave"] += 1
	if code == "307" and not trueJid in gStatsKicked[conference]:
		gConferenceStats[conference]["kick"] += 1
		gStatsKicked[conference].append(trueJid)
	elif code == "301" and not trueJid in gStatsBanned[conference]:
		gConferenceStats[conference]["ban"] += 1
		gStatsBanned[conference].append(trueJid)

def updatePresenceStats(stanza, conference, nick, trueJid):
	if protocol.TYPE_ERROR != stanza.getType():
		if "303" == stanza.getStatusCode():
			gConferenceStats[conference]["nick"] += 1
		else:
			msgType = stanza.getType()
			if msgType and msgType != protocol.PRS_OFFLINE:
				gConferenceStats[conference]["status"] += 1
	
def initConferenceStats(conference):
	gConferenceStats[conference] = {
			"nick": 0, 
			"status": 0, 
			"kick": 0, 
			"ban": 0, 
			"join": 0, 
			"leave": 0, 
			"mymsg": 0, 
			protocol.TYPE_PRIVATE: 0, 
			protocol.TYPE_PUBLIC: 0, 
			protocol.ROLE_MODERATOR: 0, 
			protocol.ROLE_PARTICIPANT: 0, 
			protocol.ROLE_VISITOR: 0
	}
	gStatsJoined[conference] = []
	gStatsLeaved[conference] = []
	gStatsKicked[conference] = []
	gStatsBanned[conference] = []

def freeConferenceStats(conference):
	del gConferenceStats[conference]
	del gStatsJoined[conference]
	del gStatsLeaved[conference]
	del gStatsKicked[conference]
	del gStatsBanned[conference]

registerEvent(initConferenceStats, EVT_ADDCONFERENCE)
registerEvent(freeConferenceStats, EVT_DELCONFERENCE)

registerJoinHandler(updateJoinStats)
registerLeaveHandler(updateLeaveStats)

registerPresenceHandler(updatePresenceStats, H_CONFERENCE)
registerMessageHandler(updateMessageStats, H_CONFERENCE)

registerBotMessageHandler(updateBotMessageStats)

registerCommand(showConferenceStats, u"статистика", 10, 
				u"Статистика текущей конференции", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
