# coding: utf-8

# tv.py
# Initial Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>
# Modification Copyright (c) 2010-2011 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

TVCODES_FILE = "tvchannels.txt"

TV_CATEGORIES = {
	u"новости": "4",
	u"фильмы": "1,1011",
	u"сериалы": "2,1021",
	u"спорт": "3,30,130,1032",
	u"детям": "5,1051",
	u"досуг": "10,11001",
}

def loadTVChannels():
	global TV_CHANNELS
	path = getFilePath(RESOURCE_DIR, TVCODES_FILE)
	TV_CHANNELS = eval(utils.readFile(path, encoding="utf-8"))

def getTVQueryParam(channel, flag=None, short=False):
	param = {
		"mode": "print",
		"channel": channel
	}
	if flag:
		param["flag"] = flag
	if not short:
		param["period"] = "24"
	return param

def getTVChannelCode(channelName):
	if channelName.isdigit():
		return channelName
	else:
		for x in TV_CHANNELS:
			if channelName == x.lower():
				return TV_CHANNELS[x]

def getTVForChannel(channelCode, short):
	url = "http://tv.yandex.ru/"
	qparam = getTVQueryParam(channelCode, short)
	response = getURL(url, qparam)
	if response:
		rawHTML = response.read()
		elements = re.findall(r"<div>(.+?)\n", rawHTML)
		if elements:
			rawtext = "\n".join(elements)
			return decode(rawtext, "utf-8")
	return None

def getTVForCategory(category, short):
	channels = ",".join(TV_CHANNELS.values())
	url = "http://tv.yandex.ru/"
	qparam = getTVQueryParam(channels, category)

	response = getURL(url, qparam)
	if response:
		rawhtml = unicode(response.read(), "utf-8")
		pattern = re.compile(r"<table.+?class=\"channel\".+?>(.+?)</table>", re.DOTALL)
		nameptrn = re.compile(r"<br><b>(.+?)</b><br><br>")
		itemptrn = re.compile(r"<div>(.+?)\n")
		
		program = {}
		channels = []
		message = []

		tables = pattern.findall(rawhtml)
		for table in tables:
			channel = nameptrn.search(table).group(1)
			if channel not in program:
				program[channel] = []
				channels.append(channel)
				program[channel] = "\n".join(itemptrn.findall(table))

		for channel in channels:
			message.append(u"%s:\n%s" % (channel, decode(program[channel])))
		if message:
			return "\n".join(message)
	return None

def showTVProgramMore(msgType, conference, nick, param):
	processCommand(msgType, conference, nick, param, True)
	
def showTVProgram(msgType, conference, nick, param):
	processCommand(msgType, conference, nick, param, False)

def processCommand(msgType, conference, nick, param, short=False):
	param = param.lower()
	if u"каналы" == param:
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Ушли")
		tvList = [u"%s - %s" % (code, name) for name, code in TV_CHANNELS.items()]
		tvList.sort()
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Список каналов:\n%s" % ("\n".join(tvList)))		
	elif u"категории" == param:
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Ушли")
		tvCats = [cat for cat in TV_CATEGORIES]
		tvCats.sort()
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Список категорий:\n%s" % (", ".join(tvCats)))
	elif param not in TV_CATEGORIES:
		channelCode = getTVChannelCode(param)
		if channelCode:
			program = getTVForChannel(channelCode, short)
			if program:
				sendMsg(msgType, conference, nick, u"Вот, что я нашла:\n%s" % (program))
			else:
				sendMsg(msgType, conference, nick, u"На сегодня программы нет")
		else:
			sendMsg(msgType, conference, nick, u"Не знаю такого канала/категории")
	else:
		category = TV_CATEGORIES[param]
		program = getTVForCategory(category)
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Ушло")	
		if program:
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, 
				u"Программа для категории \"%s\":\n%s" % (param, program))
		else:
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"На сегодня программы для этой категории нет")

registerEventHandler(loadTVChannels, EVT_STARTUP)

registerCommand(showTVProgram, u"тв", 10, 
				u"Показывает телепрограму для определённого канала/категории. Параметр \"каналы\" - список каналов, параметр \"категории\" - список категорий",
				u"<канал|номер|категория>", 
				(u"101", u"первый", u"каналы", u"категории"), 
				CMD_ANY | CMD_PARAM)
registerCommand(showTVProgramMore, u"тв+", 10, 
				u"Показывает телепрограму для определённого канала/категории на 24 часа. Параметр \"каналы\" - список каналов, параметр \"категории\" - список категорий",
				u"<канал|номер|категория>", 
				(u"101", u"первый", u"каналы", u"категории"), 
				CMD_ANY | CMD_PARAM)
