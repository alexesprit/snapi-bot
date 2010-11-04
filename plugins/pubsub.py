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

def setBotMood(msgType, jid, resource, param):
	if(param == u"сброс" or param.count("|")):
		iq = protocol.Iq(protocol.TYPE_SET)
		iq.setType(protocol.TYPE_HEADLINE)
		pubsub = iq.addChild("pubsub", {}, [], protocol.NS_PUBSUB)
		pubNode = protocol.Node("publish", {"node": protocol.NS_MOOD})
		moodNode = protocol.Node("mood", {"xmlns": protocol.NS_MOOD})
		if(param.count("|")):
			param = param.split("|")
			moodNode.addChild(node = protocol.Node(param[0]))
			moodNode.setTagData("text", param[1])
		pubNode.addChild("item", {}, [moodNode], "")
		pubsub.addChild(node = pubNode)
		gClient.send(iq)
		if(param == u"сброс"):
			sendMsg(msgType, jid, resource, u"Сбросила")
		else:
			sendMsg(msgType, jid, resource, u"Поставила")
	else:
		sendMsg(msgType, jid, resource, u"Читай помощь по команде")

def setBoAtctivity(msgType, jid, resource, param):
	if(param == u"сброс" or param.count("|")):
		iq = protocol.Iq(protocol.TYPE_SET)
		iq.setType(protocol.TYPE_HEADLINE)
		pubsub = iq.addChild("pubsub", {}, [], protocol.NS_PUBSUB)
		pubNode = protocol.Node("publish", {"node": protocol.NS_ACTIVITY})
		actNode = protocol.Node("activity", {"xmlns": protocol.NS_ACTIVITY})
		if(param.count("|")):
			param = param.split("|")
			act = actNode.addChild(node = protocol.Node(param[0]))
			if(param[1]):
				act.addChild(node = protocol.Node(param[1]))
			actNode.setTagData("text", param[2])
		pubNode.addChild("item", {}, [actNode], "")
		pubsub.addChild(node = pubNode)
		gClient.send(iq)
		if(param == u"сброс"):
			sendMsg(msgType, jid, resource, u"Сбросила")
		else:
			sendMsg(msgType, jid, resource, u"Поставила")
	else:
		sendMsg(msgType, jid, resource, u"Читай помощь по команде")

registerCommand(setBoAtctivity, u"активность", 100, 
				u"Устанавливает активность для бота. \"Cброс\" в кач-ве параметра сбрасывает активность", 
				u"активность <осн.|доп.|текст>", 
				(u"активность doing_chores|doing_maintenance|ололо", ), 
				ROSTER | PARAM)
registerCommand(setBotMood, u"настроение", 100, 
				u"Устанавливает настроение для бота. \"Cброс\" в кач-ве параметра сбрасывает настроение", 
				u"настроение <название|текст>", 
				(u"настроение calm|ололо", ), 
				ROSTER | PARAM)
