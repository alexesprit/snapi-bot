# coding: utf-8

# pubsub.py
# Initial Copyright (с) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def getMoodNode(name=None, text=None):
	iq = protocol.Iq(protocol.TYPE_SET)
	pubsub = iq.addChild("pubsub", xmlns=protocol.NS_PUBSUB)
	pubNode = pubsub.addChild("publish", {"node": protocol.NS_MOOD})
	moodNode = pubNode.addChild("item", {"id": "mood"}).addChild("mood", xmlns=protocol.NS_MOOD)
	if name:
		moodNode.addChild(name)
		if text:
			moodNode.setTagData("text", text)
	return iq

def setBotMood(msgType, jid, resource, param):
	if param != u"reset":
		args = param.split(None, 1)
		name = args[0]
		if len(args) == 2:
			text = args[1]
		else:
			text = None
		gClient.send(getMoodNode(name, text))
		sendMsg(msgType, jid, resource, u"Запомнила")
	else:
		gClient.send(getMoodNode())
		sendMsg(msgType, jid, resource, u"Сбросила")

def getActivityNode(name=None, exname=None, text=None):
	iq = protocol.Iq(protocol.TYPE_SET)
	pubsub = iq.addChild("pubsub", xmlns=protocol.NS_PUBSUB)
	pubNode = pubsub.addChild("publish", {"node": protocol.NS_ACTIVITY})
	actNode = pubNode.addChild("item").addChild("activity", xmlns=protocol.NS_ACTIVITY)
	if name:
		act = actNode.addChild(name)
		if exname:
			act.addChild(exname)
		if text:
			actNode.setTagData("text", text)
	return iq

def setBoAtctivity(msgType, jid, resource, param):
	if param != u"reset":
		args = param.split(None, 2)
		arglen = len(args)
		if arglen >= 2:
			name = args[0]
			exname = args[1]
			if arglen == 3:
				text = args[2]
			else:
				text = None
			gClient.send(getActivityNode(name, exname, text))
			sendMsg(msgType, jid, resource, u"Запомнила")
		else:
			sendMsg(msgType, jid, resource, u"Читай помощь по команде")
	else:
		gClient.send(getActivityNode())
		sendMsg(msgType, jid, resource, u"Сбросила")		

registerCommand(setBoAtctivity, u"activity", 100, 
				u"Устанавливает активность для бота. \"reset\" в кач-ве параметра сбрасывает активность", 
				u"<осн.> <доп.> [текст]", 
				(u"doing_chores doing_maintenance ололо", ), 
				CMD_ROSTER | CMD_PARAM)
registerCommand(setBotMood, u"mood", 100, 
				u"Устанавливает настроение для бота. \"reset\" в кач-ве параметра сбрасывает настроение", 
				u"<название> [текст]", 
				(u"calm ололо", ), 
				CMD_ROSTER | CMD_PARAM)
