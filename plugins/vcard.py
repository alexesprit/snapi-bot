# coding: utf-8;

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

VCARD_ID = 'vcard_id';
		
TAGS = ('NICKNAME', 'FN', 'GENDER', 'BDAY', 'LOCALITY', 'CTRY', u'ORGNAME', 'ROLE', 'TITLE', 'NUMBER', 'URL', 'EMAIL', 'DESC')
DESC = (u'Ник', u'Имя', u'Пол', u'Д/р', u'Город', u'Страна', u'Огранизация', u'Профессия', u'Должность', u'Телефон', u'Сайт', u'E-mail', u'Заметки')

def showVCard(msgType, conference, nick, param):
	if(param):
		if(conferenceInList(conference) and nickIsOnline(conference, param)):
			userJid = conference + '/' + param;
		else:
			sendMsg(msgType, conference, nick, u'а это кто?');
			return;
	else:
		userJid = conferenceInList(conference) and (conference + '/' + nick) or conference;
	iq = xmpp.Iq('get');
	iq.addChild('vCard', {}, [], xmpp.NS_VCARD);
	iq.setTo(userJid);
	vcardID = getUniqueID(VCARD_ID);
	iq.setID(vcardID);
	gClient.SendAndCallForResponse(iq, _showVCard, (vcardID, msgType, conference, nick, param, ));

def _showVCard(stanza, vcardID, msgType, conference, nick, param):
	if(vcardID == stanza.getID()):
		if(stanza.getType() == 'result'):
			queryNode = stanza.getChildren();
			if(queryNode):
				vcard = {};
				for tag in queryNode[0].getChildren():
					pName = tag.getName();
					pData = tag.getData();
					if(not pData):
						for tag in tag.getChildren():
							pName = tag.getName();
							pData = tag.getData();
							vcard[pName] = pData;
					else:
						vcard[pName] = pData;
				message = fillVCard(vcard);
				if(message):
					if(not param):
						sendMsg(msgType, conference, nick, u'про тебя я знаю следующее:\n%s' % (message));
					else:
						sendMsg(msgType, conference, nick, u'про %s я знаю следующее:\n%s' % (param, message));
				else:
					sendMsg(msgType, conference, nick, u'пустой вкард');
			else:
				if(not param):
					sendMsg(msgType, conference, nick, u'вкард заполни сначала');
				else:
					sendMsg(msgType, conference, nick, u'передай ему, чтобы он свой вкард сначала заполнил');
		elif(stanza.getType() == 'error'):
			if(not param):
				sendMsg(msgType, conference, nick, u'хехе, твой клиент ничего не знает про вкарды');
			else:
				sendMsg(msgType, conference, nick, u'хехе, его клиент ничего не знает про вкарды');
				
def fillVCard(vcard):
	name = '';
	text = '';
	for tag in ('GIVEN', 'MIDDLE', 'FAMILY'):
		tagData = vcard.get(tag);
		if(tagData):
			name += tagData + ' ';
	if(name):
		vcard['FN'] = name;
	
	items = ['%s: %s' % (DESC[i], vcard[TAGS[i]]) for i in range(0, len(TAGS)) if(TAGS[i] in vcard and vcard[TAGS[i]])];
	return('\n'.join(items));

registerCommand(showVCard, u'визитка', 10, u'Показывает vCard указанного пользователя', u'визитка [ник]', (u'визитка', u'визитка Nick'));
