# coding: utf-8;

# botstatus.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def changeStatus(type, conference, nick, param):
	args = param.split(' ', 1);
	show, status = '', '';
	if(args[0] in ('away', 'xa', 'dnd', 'chat')):
		show = args[0];
		if(len(args) > 1):
			status = args[1];
	else:
		status = param;
	setBotStatus(conference, status, show);
	setConfigKey(conference, 'status', status);
	setConfigKey(conference, 'show', show);
	saveChatConfig(conference);

registerCommand(changeStatus, u'ботстатус', 30, u'Меняет статус бота', u'ботстатус <[статус] [сообщение]>', (u'ботстатус away', u'ботстатус away сплю'), CHAT | PARAM);

def setDefaultStatus(conference):
	if(not getConfigKey(conference, 'show')):
		setConfigKey(conference, 'show', u'online');
		setConfigKey(conference, 'status', None);

registerEvent(setDefaultStatus, ADDCONF);
