# coding: utf-8

# vcard.py
# Initial Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>
# Modification Copyright (c) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

VCARD_ID = "vcard_id"

VCARD_TAGS = (
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

def showVCard(msgType, conference, nick, param):
	if(param):
		if(conferenceInList(conference) and nickIsOnline(conference, param)):
			jid = conference + "/" + param
		else:
			jid = param
	else:
		jid = conferenceInList(conference) and (conference + "/" + nick) or conference
	iq = xmpp.Iq(xmpp.TYPE_GET)
	iq.addChild("vCard", {}, [], xmpp.NS_VCARD)
	iq.setTo(jid)
	iq.setID(getUniqueID(VCARD_ID))
	gClient.sendAndCallForResponse(iq, _showVCard, (msgType, conference, nick, param, ))

def _showVCard(stanza, msgType, conference, nick, param):
	if(xmpp.TYPE_RESULT == stanza.getType()):
		queryNode = stanza.getChildren()
		if(queryNode):
			rawVCard = {}
			loadRawVCard(queryNode[0], rawVCard)
			message = getVCard(rawVCard)
			if(message):
				if(not param):
					sendMsg(msgType, conference, nick, u"про тебя я знаю следующее:\n%s" % (message))
				else:
					sendMsg(msgType, conference, nick, u"про %s я знаю следующее:\n%s" % (param, message))
			else:
				sendMsg(msgType, conference, nick, u"пустой вкард")
		else:
			if(not param):
				sendMsg(msgType, conference, nick, u"вкард заполни сначала")
			else:
				sendMsg(msgType, conference, nick, u"пусть %s сначала вкард заполнит" % (param))
	else:
		sendMsg(msgType, conference, nick, u"не получается :(")

def loadRawVCard(node, rawVCard):
	for child in node.getChildren():
		tagData = child.getData()
		if(tagData):
			tagName = child.getName()
			rawVCard[tagName] = tagData
		else:
			loadRawVCard(child, rawVCard)
			
def getVCard(rawVCard):
	name = ""
	for tag in ("GIVEN", "MIDDLE", "FAMILY"):
		tagData = rawVCard.get(tag)
		if tagData:
			name += tagData + " "
	if(name):
		rawVCard["FN"] = name
	vCardItems = []
	for i in xrange(len(VCARD_TAGS)):
		tagName, tagDesc = VCARD_TAGS[i]
		tagData = rawVCard.get(tagName)
		if tagData:
			vCardItems.append(u"%s: %s" % (tagDesc, tagData))
	return("\n".join(vCardItems))

registerCommand(showVCard, u"визитка", 10, 
				u"Показывает vCard указанного пользователя или сервера", 
				u"визитка [ник|сервер]", 
				(u"визитка", u"визитка Nick", u"визитка server.tld"))
