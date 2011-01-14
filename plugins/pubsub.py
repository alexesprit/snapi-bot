# coding: utf-8

# pubsub.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def getMoodStanza(name=None, text=None):
	stanza = protocol.Iq(protocol.TYPE_SET)
	pubsub = stanza.addChild("pubsub", {}, [], protocol.NS_PUBSUB)
	pubNode = protocol.Node("publish", {"node": protocol.NS_MOOD})
	moodNode = protocol.Node("mood", {"xmlns": protocol.NS_MOOD})
	if name:
		moodNode.addChild(node=protocol.Node(name))
		if text: 
			moodNode.setTagData("text", text)
	pubNode.addChild("item", {}, [moodNode], "")
	pubsub.addChild(node=pubNode)
	return stanza

def setBotMood(msgType, jid, resource, param):
	if param != u"reset":
		args = param.split(None, 1)
		name = args[0]
		if len(args) == 2:
			text = args[1]
		else:
			text = None
		gClient.send(getMoodStanza(name, text))
		sendMsg(msgType, jid, resource, u"Запомнила")
	else:
		gClient.send(getMoodStanza())
		sendMsg(msgType, jid, resource, u"Сбросила")

def getActivityStanza(name=None, exname=None, text=None):
	stanza = protocol.Iq(protocol.TYPE_SET)
	pubsub = stanza.addChild("pubsub", {}, [], protocol.NS_PUBSUB)
	pubNode = protocol.Node("publish", {"node": protocol.NS_ACTIVITY})
	actNode = protocol.Node("activity", {"xmlns": protocol.NS_ACTIVITY})
	if name:
		act = actNode.addChild(node=protocol.Node(name))
		if exname:
			act.addChild(node=protocol.Node(exname))
		if text:
			actNode.setTagData("text", text)
	pubNode.addChild("item", {}, [actNode], "")
	pubsub.addChild(node = pubNode)
	return stanza

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
			gClient.send(getActivityStanza(name, exname, text))
			sendMsg(msgType, jid, resource, u"Запомнила")
		else:
			sendMsg(msgType, jid, resource, u"Читай помощь по команде")
	else:
		gClient.send(getActivityStanza())
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
