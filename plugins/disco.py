# coding: utf-8

# disco.py
# Initial Copyright (c) 2007 Als <Als@exploit.in>
# Help Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

DISCO_ID = "disco_id"

def serviceDiscovery(msgType, conference, nick, param):
	param = param or gHost
	param = param.split(None, 2)
	jid = param[0]
	searchKey = None
	maxCount = (protocol.TYPE_PUBLIC == msgType) and 10 or 50
	if(len(param) > 1):
		count = param[1]
		if(count.isdigit()):
			count = int(count)
			if(protocol.TYPE_PUBLIC == msgType):
				maxCount = min(50, count)
			else:
				maxCount = min(250, count);	
			if(len(param) > 2):
				searchKey = param[2]
		else:		
			searchKey = param[1]
	iq = protocol.Iq(protocol.TYPE_GET)
	query = iq.addChild("query", None, None, protocol.NS_DISCO_ITEMS)
	param = jid.split("#")
	if(len(param) == 2):
		jid, node = param
		iq.setTo(jid)
		query.setAttr("node", node)
	else:
		iq.setTo(jid)
	iq.setID(getUniqueID(DISCO_ID))
	gClient.sendAndCallForResponse(iq, _serviceDiscovery, (msgType, conference, nick, jid, maxCount, searchKey))

def _serviceDiscovery(stanza, msgType, conference, nick, jid, maxCount, searchKey):
	if(protocol.TYPE_RESULT == stanza.getType()):
		discoList = []
		itemCount = 0
		for x in stanza.getQueryChildren():
			itemCount += 1
			attrs = x.getAttrs()
			items = []
			if("name" in attrs):
				items.append(attrs["name"])
			if(not isJid(jid) and "jid" in attrs):
				items.append(attrs["jid"])
			if("node" in attrs):
				items.append(attrs["node"])
			if(len(items) == 3):
				if(searchKey):
					if(not items[0].count(searchKey)):
						continue
				discoList.append(u"%d) %s (%s)" % (itemCount, items[0], items[2]))
			elif(len(items) == 2):
				if(searchKey):
					if(searchKey.endswith("@")):
						if(not items[1].startswith(searchKey)):
							continue
						discoList.append(u"%d) %s\n%s" % (itemCount, items[1], items[0]))
						break
					else:
						if(not items[0].count(searchKey)):
							continue
						discoList.append(u"%d) %s\n%s" % (itemCount, items[1], items[0]))
				else:
					discoList.append(u"%d) %s\n%s" % (itemCount, items[1], items[0]))
			else:
				if(searchKey):
					if(not items[0].count(searchKey)):
						continue
				discoList.append(u"%d) %s" % (itemCount, items[0]))
		if(discoList):
			if(0 == maxCount):
				sendMsg(msgType, conference, nick, u"всего %d пунктов" % (itemCount))
			else:
				if(itemCount > maxCount):
					discoList = discoList[:maxCount]
					discoList.append(u"всего %d пунктов" % (itemCount))
				sendMsg(msgType, conference, nick, u"надискаверила:\n" + u"\n".join(discoList))
		else:
			sendMsg(msgType, conference, nick, u"пустое диско")
	else:
		sendMsg(msgType, conference, nick, u"не могу")

registerCommand(serviceDiscovery, u"диско", 10, 
				u"Показывает результаты обзора сервисов для указанного жида. Также можно выполнить запрос по узлу (\"жид#узел\") Второй или третий (если даётся ограничитель кол-ва) параметр - поиск (ищет заданное слово в жиде и описании элемента диско). Если поисковым словом задать имя конференции до названия сервера (например qwerty@), то покажет место этой конференции в общем рейтинге. В общий чат может дать до 50 результатов (10 - без указания кол-ва), в приват - 250 (50 - без указания кол-ва)", 
				u"диско <жид> [кол-во результатов] [поисковая строка]", 
				(u"диско jabber.aq", u"диско conference.jabber.aq qwerty", u"диско conference.jabber.aq 5 qwerty", u"диско conference.jabber.aq qwerty@"))
