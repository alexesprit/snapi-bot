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

def showServiceDiscoveryResults(msgType, conference, nick, param):
	param = param or Config.SERVER
	args = param.split(None, 2)
	jid = args[0]
	searchKey = None
	maxCount = (protocol.TYPE_PUBLIC == msgType) and 10 or 50
	if len(args) > 1:
		count = args[1]
		if count.isdigit():
			count = int(count)
			if protocol.TYPE_PUBLIC == msgType:
				maxCount = min(50, count)
			else:
				maxCount = min(250, count);
			if len(args) > 2:
				searchKey = args[2]
		else:
			args = param.split(None, 1)
			searchKey = args[1]
	iq = protocol.Iq(protocol.TYPE_GET)
	query = iq.addChild("query", None, None, protocol.NS_DISCO_ITEMS)
	args = jid.split("#")
	if len(args) == 2:
		jid, node = args
		iq.setTo(jid)
		query.setAttr("node", node)
	else:
		iq.setTo(jid)
	iq.setID(getUniqueID("disco_id"))
	gClient.sendAndCallForResponse(iq, showServiceDiscoveryResults_, (msgType, conference, nick, jid, maxCount, searchKey))

def showServiceDiscoveryResults_(stanza, msgType, conference, nick, jid, maxCount, searchKey):
	if protocol.TYPE_RESULT == stanza.getType():
		discoList = []
		itemCount = 0
		for x in stanza.getQueryChildren():
			itemCount += 1
			attrs = x.getAttrs()
			elements = []
			if "name" in attrs:
				elements.append(attrs["name"])
				if not isJID(jid) and "jid" in attrs:
					elements.append(attrs["jid"])
				if "node" in attrs:
					elements.append(attrs["node"])
			else:
				elements.append(attrs["jid"])
			if len(elements) == 3:
				if searchKey:
					if not elements[0].count(searchKey):
						continue
				discoList.append(u"%d) %s (%s)" % (itemCount, elements[0], elements[2]))
			elif len(elements) == 2:
				if searchKey:
					if searchKey.endswith("@"):
						if not elements[1].startswith(searchKey):
							continue
						discoList.append(u"%d) %s\n%s" % (itemCount, elements[1], elements[0]))
						break
					else:
						if not elements[0].count(searchKey):
							continue
						discoList.append(u"%d) %s\n%s" % (itemCount, elements[1], elements[0]))
				else:
					discoList.append(u"%d) %s\n%s" % (itemCount, elements[1], elements[0]))
			elif len(elements) == 1:
				if searchKey:
					if not elements[0].count(searchKey):
						continue
				discoList.append(u"%d) %s" % (itemCount, elements[0]))
		if discoList:
			if 0 == maxCount:
				sendMsg(msgType, conference, nick, u"Всего %d пунктов" % (itemCount))
			else:
				if itemCount > maxCount:
					discoList = discoList[:maxCount]
					discoList.append(u"Всего %d пунктов" % (itemCount))
				sendMsg(msgType, conference, nick, u"Надискаверила:\n%s" % (u"\n".join(discoList)))
		else:
			if searchKey and itemCount:
				message = u"Текст \"%s\" не найден (всего %d пунктов)" % (searchKey, itemCount)
				sendMsg(msgType, conference, nick, message)
			else:
				sendMsg(msgType, conference, nick, u"Пустое диско")
	else:
		sendMsg(msgType, conference, nick, u"Не могу")

registerCommand(showServiceDiscoveryResults, u"диско", 10,
				u"Показывает результаты обзора сервисов для указанного жида. Также можно выполнить запрос по узлу (\"жид#узел\") Второй или третий (если даётся ограничитель кол-ва) параметр - поиск (ищет заданное слово в жиде и описании элемента диско). Если поисковым словом задать имя конференции до названия сервера (например qwerty@), то покажет место этой конференции в общем рейтинге. В общий чат может дать до 50 результатов (10 - без указания кол-ва), в приват - 250 (50 - без указания кол-ва)",
				u"<жид> [кол-во результатов] [поисковая строка]",
				(u"server.tld", u"conference.server.tld qwerty", u"conference.server.tld 5 qwerty", u"conference.server.tld qwerty@"))
