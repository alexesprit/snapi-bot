# coding: utf-8;

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

DISCO_ID = 'disco_id';

def serviceDiscovery(type, conference, nick, param):
	param = param or gHost;
	args = param.split(' ', 2);
	searchKey, jid = None, args[0];
	maxCount = (PUBLIC == type) and 10 or 50;
	if(len(args) > 1):
		try:
			maxCount = int(args[1]);
			if(PUBLIC == type):
				maxCount = min(50, maxCount);
			else:
				maxCount = min(250, maxCount);
			try:
				searchKey = args[2];
			except(KeyError):
				pass;
		except(ValueError):
			searchKey = args[1];
	iq = xmpp.Iq('get');
	query = iq.addChild('query', {}, [], xmpp.NS_DISCO_ITEMS);
	if(jid.count('#')):
		query.setAttr('node', jid.split('#')[1]);
		iq.setTo(jid.split('#')[0]);
	else:
		iq.setTo(jid);
	discoID = getUniqueID(DISCO_ID);
	iq.setID(discoID);
	gClient.SendAndCallForResponse(iq, _serviceDiscovery, (discoID, type, conference, nick, maxCount, searchKey, jid, ));

def _serviceDiscovery(stanza, discoID, type, conference, nick, maxCount, searchKey, jid):
	if(discoID == stanza.getID()):
		if(stanza.getType() == 'result'):
			discoList = [];
			itemCount = 0;
			for x in stanza.getQueryChildren():
				itemCount += 1;
				attr = x.getAttrs();
				if('name' in attr):
					item.append(attr['name']);
					if(not jid.count('@') and 'jid' in attr):
						item.append(attr['jid']);
					if('node' in attr):
						item.append(attr['node']);
					if(len(item) == 3):
						if(searchKey):
							if(searchKey.endswith('@')):
								if(item[1].startswith(searchKey)):
									discoList.append(u'%d) %s [%s]: %s' % (itemCount, item[0], item[1], item[2]))
									break;
							else:
								if(not(item[0].count(searchKey) and item[1].count(searchKey))):
									continue;
						else:
							discoList.append(u'%d) %s [%s]: %s' % (itemCount, item[0], item[1], item[2]));
					elif(len(item) == 2):
						if(searchKey):
							if(not(item[0].count(searchKey) and item[1].count(searchKey))):
								continue;
						discoList.append(u'%d) %s [%s]' % (itemCount, item[0], item[1]));
				else:
					if(searchKey):
						if(not item[0].count(searchKey)):
							continue;
					discoList.append(u'%d) %s' % (itemCount, attr['jid']));
			if(discoList):
				if(0 == maxCount):
					sendMsg(type, conference, nick, u'всего %d пунктов' % (itemCount));
				else:
					if(itemCount != len(discoList)):
						discoList.append(u'всего %d пунктов' % (itemCount));
					sendMsg(type, conference, nick, u'надискаверила:\n' + u'\n'.join(discoList));
			else:
				sendMsg(type, conference, nick, u'пустое диско');
		else:
			sendMsg(type, conference, nick, u'не могу');

registerCommand(serviceDiscovery, u'диско', 10, u'Показывает результаты обзора сервисов для указанного жида. Также можно запросить обзор по узлу (формат запроса jid#node). Второй или третий (если даётся ограничитель кол-ва) параметр - поиск (ищет заданное слово в жиде и описании элемента диско). Если поисковым словом задать имя конференции до названия сервера (например qwerty@), то покажет место этой конференции в общем рейтинге. В общий чат может дать до 50 результатов, без указания кол-ва - 10. В приват может дать до 250, без указания кол-ва 50.', u'диско <сервер> [кол-во результатов] [поисковая строка]', (u'диско jabber.aq', u'диско conference.jabber.aq 5', u'диско conference.jabber.aq qwerty', u'диско conference.jabber.aq 5 qwerty', u'диско conference.jabber.aq qwerty@', u'диско jabber.aq#services'));
