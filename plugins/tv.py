# coding: utf-8

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

TVCODES_FILE = "channels.txt"

def getChannelCode(channelName):
	if(channelName.isdigit()):
		return(channelName)
	else:
		channelName = channelName.lower()
		for x in gChannels:
			if(x.lower() in channelName):
				return(gChannels[x])

def loadChannels():
	global gChannels
	fileName = getFilePath(RESOURCE_DIR, TVCODES_FILE)
	gChannels = eval(readFile(fileName, "utf-8"))

def showTvProgramm(msgType, conference, nick, param):
	channelCode = getChannelCode(param)
	program = ""
	if(channelCode):
		url = "http://tv.yandex.ru/?mode=print&channel=%s" % (channelCode)
		lines = urllib.urlopen(url).readlines()
		for x in lines:
			if(x.startswith("<div>")):
				program += decode(x)
	if(program):
		sendMsg(msgType, conference, nick, unicode(program, "utf-8"))
	else:
		sendMsg(msgType, conference, nick, u"нету на сегодня программы")

def showTvList(msgType, conference, nick, parameters):
	if(xmpp.TYPE_PUBLIC == msgType):
		sendMsg(msgType, conference, nick, u"скинула в приват")
	tvList = [u"%s - %s" % (gChannels[x], x) for x in gChannels]
	tvList.sort()
	sendMsg(xmpp.TYPE_PRIVATE, conference, nick, u"список каналов:\n%s" % ("\n".join(tvList)))

registerEvent(loadChannels, STARTUP)

registerCommand(showTvProgramm, u"тв", 10, 
				u"Показать телепрограму для определённого канала", 
				u"тв <название>", 
				(u"тв первый", ), 
				ANY | PARAM)
registerCommand(showTvList, u"твлист", 10, 
				u"Просмотреть список каналов, доступных для просмотра программы", 
				None, 
				(u"твлист", ), 
				ANY | NONPARAM)
