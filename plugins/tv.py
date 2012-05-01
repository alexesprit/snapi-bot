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
	u"новости": "old/tv/-/%Y-%m-%d/Инфо/",
	u"фильмы": "old/tv/-/%Y-%m-%d/Фильм/",
	u"сериалы": "old/tv/-/%Y-%m-%d/Сериал/",
	u"спорт": "old/tv/-/%Y-%m-%d/Спорт/",
	u"детям": "old/tv/-/%Y-%m-%d/Детям/",
	u"досуг": "old/tv/-/%Y-%m-%d/Досуг/",
}

def loadTVChannels():
	global TV_CHANNELS
	path = getFilePath(RESOURCE_DIR, TVCODES_FILE)
	TV_CHANNELS = eval(utils.readFile(path, encoding="utf-8"))

def getTVChannelInfo(channelName):
	reqname = channelName.lower()
	for ch in TV_CHANNELS:
		name = ch[0].lower()
		if name.startswith(reqname):
			return ch
	return None

def getTVChannelByURL(channelURL):
	for ch in TV_CHANNELS:
		if ch[1] == channelURL:
			return ch[0]
	return channelURL

def getTVProgramFromContent(rawdata):
	elements = re.findall(r"item_time\">(.+?)</span>.+?<(?:a href|span).+?>(.+?)</(?:a|span)>", rawdata, re.DOTALL)
	if elements:
		buf = []			
		for element in elements:
			time = element[0].strip()
			name = element[1].strip()
			buf.append("%s: %s" % (time, name))
		return unicode("\n".join(buf), "utf-8")
	return None
	
def getTVForCategory(categoryURL):
	expurl = time.strftime(categoryURL)
	url = "http://s-tv.ru/%s" % (expurl)
	response = getURL(url)
	if response:
		rawdata = response.read()
		rawchannels = re.findall("<table class=\"item_table\">(.+?)</table>", rawdata, re.DOTALL)
		if rawchannels:
			buf = []
			for ch in rawchannels:
				chURL = re.search("<td class=\"channel\">.+?<a href=\"(.+?)\">", ch, re.DOTALL).group(1)
				chName = getTVChannelByURL(chURL)
				program = getTVProgramFromContent(ch)
				
				buf.append(chName)
				buf.append(program + "\n")
			return "\n".join(buf)
	return None
	
def getTVForChannel(channelURL):
	url = "http://s-tv.ru/%s" % (channelURL)
	response = getURL(url)
	if response:
		rawdata = response.read()
		return getTVProgramFromContent(rawdata)
	return None
	
def showTVProgram(msgType, conference, nick, param):
	param = param.lower()
	if u"каналы" == param:
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Ушли")
		tvList = ["%d) %s" % (i + 1, item[0]) for i, item in enumerate(TV_CHANNELS)]
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Список каналов:\n%s" % ("\n".join(tvList)))
	elif u"категории" == param:
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Ушли")
		tvCats = [cat for cat in TV_CATEGORIES]
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Список категорий:\n%s" % (", ".join(tvCats)))
	elif param not in TV_CATEGORIES:
		chInfo = getTVChannelInfo(param)
		if chInfo:
			program = getTVForChannel(chInfo[1])
			if program:
				if protocol.TYPE_PUBLIC == msgType:
					sendMsg(msgType, conference, nick, u"Ушло")
				sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Телепрограмма для канала \"%s\":\n%s" % (chInfo[0], program))
			else:
				sendMsg(msgType, conference, nick, u"На сегодня программы нет")
		else:
			sendMsg(msgType, conference, nick, u"Не знаю такого канала/категории")
	else:
		category = TV_CATEGORIES[param]
		program = getTVForCategory(category)
		if program:
			if protocol.TYPE_PUBLIC == msgType:
				sendMsg(msgType, conference, nick, u"Ушло") 
			sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Программа для категории \"%s\":\n%s" % (param, program))
		else:
			sendMsg(msgType, conference, nick, u"На сегодня программы для этой категории нет")

registerEventHandler(loadTVChannels, EVT_STARTUP)

registerCommand(showTVProgram, u"тв", 10, 
				u"Показывает телепрограму для определённого канала/категории. Параметр \"каналы\" - список каналов, параметр \"категории\" - список категорий",
				u"<канал|номер|категория>", 
				(u"101", u"первый", u"каналы", u"категории"), 
				CMD_ANY | CMD_PARAM)
