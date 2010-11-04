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

TVCODES_FILE = "tvchannels.txt"

def getTVChannelCode(channelName):
	if channelName.isdigit():
		return channelName
	else:
		channelName = channelName.lower()
		for x in gTVChannels:
			if channelName == x.lower():
				return gTVChannels[x]

def loadTVChannels():
	global gTVChannels
	fileName = getFilePath(RESOURCE_DIR, TVCODES_FILE)
	gTVChannels = eval(utils.readFile(fileName, "utf-8"))

def showTVProgram(msgType, conference, nick, param):
	channelCode = getTVChannelCode(param)
	program = ""
	if channelCode:
		url = "http://tv.yandex.ru/?mode=print&channel=%s" % (channelCode)
		rawHTML = urllib.urlopen(url).read()
		items = re.findall(r"<div>(.+?)</div>", rawHTML, re.DOTALL)
		if items:
			rawtext = "\n".join(items)
			message = u"вот, что я нашла:\n%s" % (decode(rawtext, "utf-8"))
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"На сегодня программы нет")
	else:
		sendMsg(msgType, conference, nick, u"Не знаю такого канала")

def showTVList(msgType, conference, nick, parameters):
	if(protocol.TYPE_PUBLIC == msgType):
		sendMsg(msgType, conference, nick, u"Скинула в приват")
	tvList = [u"%s - %s" % (code, name) for name, code in gTVChannels.items()]
	tvList.sort()
	sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Список каналов:\n%s" % ("\n".join(tvList)))

registerEvent(loadTVChannels, STARTUP)

registerCommand(showTVProgram, u"тв", 10, 
				u"Показать телепрограму для определённого канала", 
				u"тв <название>", 
				(u"тв первый", ), 
				ANY | PARAM)
registerCommand(showTVList, u"твлист", 10, 
				u"Просмотреть список каналов, доступных для просмотра программы", 
				None, 
				(u"твлист", ), 
				ANY | NONPARAM)
