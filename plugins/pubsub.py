# coding: utf-8;

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

'''
	Установка активностей и настроений. Для ростера. Написано от нежелания
	заняться чем-то полезным :)
'''

def setMood(type, jid, resource, param):
	if(param == u'сброс' or param.count('|') == 1):
		iq = xmpp.Iq('set');
		pubsub = iq.addChild('pubsub', {}, [], xmpp.NS_PUBSUB);
		pubNode = xmpp.Node('publish', {'node': xmpp.NS_MOOD});
		moodNode = xmpp.Node('mood', {'xmlns': xmpp.NS_MOOD});
		if(param.count('|')):
			param = param.split('|');
			moodNode.addChild(node = xmpp.Node(param[0]));
			moodNode.setTagData('text', param[1]);
		pubNode.addChild('item', {}, [moodNode], '');
		pubsub.addChild(node = pubNode);
		gClient.send(iq);
		if(param == u'сброс'):
			sendMsg(type, jid, resource, u'сбросила');
		else:
			sendMsg(type, jid, resource, u'поставила');

def setActivity(type, jid, resource, param):
	if(param == u'сброс' or param.count('|') == 1):
		iq = xmpp.Iq('set');
		pubsub = iq.addChild('pubsub', {}, [], xmpp.NS_PUBSUB);
		pubNode = xmpp.Node('publish', {'node': xmpp.NS_ACTIVITY});
		actNode = xmpp.Node('activity', {'xmlns': xmpp.NS_ACTIVITY});
		if(param.count('|')):
			param = param.split('|');
			act = actNode.addChild(node = xmpp.Node(param[0]));
			act.addChild(node = xmpp.Node(param[1]));
			actNode.setTagData('text', param[2]);
		pubNode.addChild('item', {}, [actNode], '');
		pubsub.addChild(node = pubNode);
		gClient.send(iq);
		if(param == u'сброс'):
			sendMsg(type, jid, resource, u'сбросила');
		else:
			sendMsg(type, jid, resource, u'поставила');

registerCommand(setActivity, u'активность', 100, u'Устанавливает активность для бота. "Cброс" в кач-ве параметра сбрасывает активность', u'активность <осн.|доп.|текст>', (u'активность doing_chores|doing_maintenance|ололо', ), ROSTER | PARAM);
registerCommand(setMood, u'настроение', 100, u'Устанавливает настроение для бота. "Cброс" в кач-ве параметра сбрасывает настроение', u'настроение <название|текст>', (u'настроение calm|ололо', ), ROSTER | PARAM);
