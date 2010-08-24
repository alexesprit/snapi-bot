# coding: utf-8;

# tv.py
# Initial Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def getChannelCode(channelName):
	if(channelName.isdigit()):
		return(channelName);
	else:
		channelName = channelName.lower();
		for x in gChannels:
			if(x.lower() in channelName):
				return(gChannels[x]);

def showTvProgramm(type, conference, nick, param):
	channelCode = getChannelCode(param);
	program = '';
	if(channelCode):
		lines = urllib.urlopen('http://tv.yandex.ru/?mode=print&channel=%s' % (channelCode)).readlines();
		for x in lines:
			if(x.startswith('<div>')):
				program += decode(x);
	if(program):
		sendMsg(type, conference, nick, program);
	else:
		sendMsg(type, conference, nick, u'нету на сегодня программы');

registerCommandHandler(showTvProgramm, u'тв', 10, u'Показать телепрограму для определённого канала', u'тв <название>', (u'тв первый'), ANY | PARAM);

def showTvList(type, conference, nick, parameters):
	if(PUBLIC == type):
		sendMsg(type, conference, nick, u'скинула в приват');
	tvList = [u'%s - %s' % (gChannels[x], x) for x in gChannels];
	tvList.sort();
	sendMsg(PRIVATE, conference, nick, u'список каналов:\n' + '\n'.join(tvList));
	
registerCommandHandler(showTvList, u'твлист', 10, u'Просмотреть список каналов, доступных для просмотра программы', None, (u'твлист'), ANY | NONPARAM);

def loadChannels():
	global gChannels;
	gChannels = eval(readFile('resource/channels.txt', 'utf-8'));

registerPluginHandler(loadChannels, STARTUP);
