# coding: utf-8

# vcard.py
# Initial Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def showVCard(msgType, conference, nick, param):
	if param:
		usernick = param
		if isConferenceInList(conference) and \
			isNickOnline(conference, usernick):
				jid = u"%s/%s" % (conference, usernick)
		else:
			jid = param
	else:
		jid = isConferenceInList(conference) and (u"%s/%s" % (conference, nick)) or conference
	iq = protocol.Iq(protocol.TYPE_GET, to=jid)
	iq.addChild("vCard", xmlns=protocol.NS_VCARD)
	gClient.sendAndCallForResponse(iq, showVCard_, (msgType, conference, nick, param))

def showVCard_(stanza, msgType, conference, nick, param):
	if protocol.TYPE_RESULT == stanza.getType():
		vCardNode = stanza.getTag("vCard")
		if vCardNode:
			rawVCard = {}
			loadRawVCard(vCardNode, rawVCard)
			vcardstr = getVCard(rawVCard)
			if vcardstr:
				if not param:
					sendMsg(msgType, conference, nick, u"Про тебя я знаю следующее:\n%s" % (vcardstr))
				else:
					sendMsg(msgType, conference, nick, u"Про %s я знаю следующее:\n%s" % (param, vcardstr))
			else:
				sendMsg(msgType, conference, nick, u"Пустой вкард")
		else:
			if not param:
				sendMsg(msgType, conference, nick, u"Вкард заполни сначала")
			else:
				sendMsg(msgType, conference, nick, u"Пусть %s сначала вкард заполнит" % (param))
	else:
		sendMsg(msgType, conference, nick, u"Не получается :(")

def loadRawVCard(node, rawVCard):
	for child in node.getChildren():
		tagData = child.getData()
		if tagData:
			tagName = child.getName()
			rawVCard[tagName] = tagData
		else:
			loadRawVCard(child, rawVCard)
			
def getVCard(rawVCard):
	buf = []
	for tag in ("GIVEN", "MIDDLE", "FAMILY"):
		tagData = rawVCard.get(tag)
		if tagData:
			buf.append(tagData)
	if buf:
		rawVCard["FN"] = "".join(buf)
	vCardElements = []
	tags = (
		("NICKNAME", u"Ник"),
		("FN", u"Имя"),
		("GENDER", u"Пол"),
		("BDAY", u"Д/р"),
		("CTRY", u"Страна"),
		("REGION", u"Район/Штат"),
		("LOCALITY", u"Город"),
		("PCODE", u"Индекс"),
		("STREET", u"Улица"),
		("ORGNAME", u"Огранизация"),
		("ORGUNIT", u"Отдел"),
		("ROLE", u"Профессия"),
		("TITLE", u"Должность"),
		("NUMBER", u"Телефон"),
		("URL", u"Сайт"),
		("EMAIL", u"E-mail"),
		("DESC", u"Заметки"),
	)
	for i in xrange(len(tags)):
		tagName, tagDesc = tags[i]
		tagData = rawVCard.get(tagName)
		if tagData:
			vCardElements.append(u"%s: %s" % (tagDesc, tagData))
	return "\n".join(vCardElements)

registerCommand(showVCard, u"визитка", 10, 
				u"Показывает vCard указанного пользователя или jabber-сервера", 
				u"[ник|жид|сервер]", 
				(None, u"Nick", u"server.tld", u"user@server.tld"))
