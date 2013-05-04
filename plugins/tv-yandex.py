# coding: utf-8

# tv-yandex.py
# Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

TV_CHANNELS_FILE = 'tv-yandex.txt'
TV_CATEGORIES_FILE = 'tv-categories.dat'
TV_CATEGORIES = (
	(4, u'сериалы'), 
	(5, u'фильмы'), 
	(7, u'спорт'), 
	(4, u'детям'), 	
)
YANDEX_TV_URL = 'http://m.tv.yandex.ru/5'
FLAG_ALL = 2
FLAG_MORNING = 4
FLAG_DAY = 5
FLAG_EVENING = 3
FLAG_NOW = 1
TV_FLAGS = {
	u"утром": FLAG_MORNING,
	u"днем": FLAG_DAY,
	u"днём": FLAG_DAY,
	u"сейчас": FLAG_NOW,
	u"вечером": FLAG_EVENING,
}

# User category:
# category = (
# 	category flag (int), category channels (list)
# )
#
# User categories:
# categories = {
# 	u'Category 1': User category,
#	u'Category 2': User category,
#	...
# }
#
# Categories:
# categories = {
#	u'userjid1@server.tld': categories,
#	u'userjid2@server.tld': categories,
#

def loadTVData():
	global TV_CHANNELS, gUserCategories
	TV_CHANNELS = eval(io.read(getFilePath(RESOURCE_DIR, TV_CHANNELS_FILE)))
	gUserCategories = database.DataBase((getFilePath(CONFIG_DIR, TV_CATEGORIES_FILE)))

def getCategoryInfoByName(name):
	for info in TV_CATEGORIES:
		if info[1].lower() == name.lower():
			return info
	return None

def getChannelInfoByNumber(number):
	for info in TV_CHANNELS:
		if number == str(info[0]):
			return info
	return None

def getChannelInfoByName(name):
	for info in TV_CHANNELS:
		if info[1].lower() == name.lower():
			return info
	return None
	
def getUserCategory(userjid, name):
	if userjid in gUserCategories:
		if name in gUserCategories[userjid]:
			return gUserCategories[userjid][name]
	return None

def getCategoryProgramFromData(data):
	if data:
		entries = re.findall(r'<table class="b-schedule__list" cellpadding="0" cellspacing="0">.+?<a href=.+?>(.+?)</a></th>(.+?)</table>', data)
		program = []
		for entry in entries:
			cname = entry[0]
			cdata = getChannelProgramFromData(entry[1])
			program.append(u'%s:\n%s\n' % (cname, cdata))
		return "\n".join(program)
	return None
		
def getChannelProgramFromData(data):
	if data:
		entries = re.findall(r'<td class="time"><a href=.+?>(.+?)</a></td><td>(.+?)</td>', data)
		program = []
		for entry in entries:
			ptime = entry[0]
			pname = entry[1]
			# 1:53 -> 01:53
			if len(ptime) == 4:
				ptime = '0' + ptime
			program.append(u'%s: %s' % (ptime, pname))
		return "\n".join(program)
	return None
	
def getTVProgramByUserCategory(category, when, day):
	flag = category[0]
	query = {
		'day': day,
		'when': when,
		'flag': flag if flag else '',
		'channel': ",".join(category[1])
	}
	data = netutil.getURLResponseData(YANDEX_TV_URL, query, encoding='utf-8')
	return getCategoryProgramFromData(data)

def getTVProgramByCategory(number, when, day):
	query = {
		'day': day,
		'when': 2,
		'flag': number,
	}
	data = netutil.getURLResponseData(YANDEX_TV_URL, query, encoding='utf-8')
	return getCategoryProgramFromData(data)
	
def getTVProgramByChannel(number, when, day):
	query = {
		'day': day,
		'when': when,
		'channel': number,
	}
	data = netutil.getURLResponseData(YANDEX_TV_URL, query, encoding='utf-8')
	return getChannelProgramFromData(data)
	
def parseParameters(param):
	param = param.lower()
	channel = param
	when = FLAG_ALL
	day = ''
	args = param.rsplit(' ', 1)
	if len(args) == 2:
		arg1, arg2 = args
		if arg2 in TV_FLAGS:
			channel = arg1
			when = TV_FLAGS[arg2]
		else:
			# current day since 1 Jan 1970
			day = int(time.mktime(time.localtime()) / 86400)
			days = {
				u'завтра': day + 1,
				u'послезавтра': day + 2,
				u'вчера': day - 1,
				u'позавчера': day - 2,
			}
			if arg2 in days:
				channel = arg1
				day = days[arg2]
	return channel, when, day
	
def showTVCategory(msgType, conference, nick, param):
	param = param.lower()
	userjid = getTrueJID(conference, nick)
	category = getUserCategory(userjid, param)
	if category:
		channels = []
		for number in category[1]:
			info = getChannelInfoByNumber(number)
			if info:
				channels.append(info[1])
		if channels:
			chlist = "\n".join(["%d) %s" % (i + 1, item) for i, item in enumerate(channels)])
			sendMsg(msgType, conference, nick, u'Категория "%s":\n%s' % (param, chlist))
		else:
			sendMsg(msgType, conference, nick, u'Категория "%s" не содержит каналов по техническим причинам. Удалите её.' % param)
	else:
		sendMsg(msgType, conference, nick, u'Категория "%s" не существует.' % param)

def addTVCategory(msgType, conference, nick, param):
	args = param.split('\n')
	if len(args) > 1:
		name = args[0].lower()
		userjid = getTrueJID(conference, nick)
		if not userjid in gUserCategories:
			gUserCategories[userjid] = {}
		filter = None
		if name not in gUserCategories[userjid]:
			channels = []
			chnames = []
			for arg in args[1:]:
				if arg.isdigit():
					info = getChannelInfoByNumber(arg)
				else:
					info = getChannelInfoByName(arg)					
				if info:
					channels.append(str(info[0]))
					chnames.append(info[1])
				else:
					info = getCategoryInfoByName(arg)
					if info:
						filter = info
			if channels:
				flag = filter[0] if filter else 0
				gUserCategories[userjid][name] = (flag, channels)
				gUserCategories.save()
				chlist = ', '.join(chnames)				
				sendMsg(msgType, conference, nick, u'Добавлена категория "%s" с каналами %s.' % (name, chlist))
			else:
				sendMsg(msgType, conference, nick, u'Указанные каналы неверны. Отправьте "тв каналы", чтобы получить список каналов.')
		else:
			sendMsg(msgType, conference, nick, u'Категория "%s" уже существует.' % name)
	else:
		sendMsg(msgType, conference, nick, u"Ошибка при выполнении команды. Прочитайте справку по команде.")
	
def delTVCategory(msgType, conference, nick, param):
	param = param.lower()
	userjid = getTrueJID(conference, nick)
	if userjid in gUserCategories:
		if param in gUserCategories[userjid]:
			del gUserCategories[userjid][param]
			gUserCategories.save()
			sendMsg(msgType, conference, nick, u'Категория "%s" удалена.' % param)
		else:
			sendMsg(msgType, conference, nick, u'Вы не добавляли категорию "%s".' % param)
	else:
		sendMsg(msgType, conference, nick, u"Вы не добавляли ни одной категории.")

def showTVProgram(msgType, conference, nick, param):
	param, when, day = parseParameters(param)
	if u"каналы" == param:
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Ушли.")
		tvList = ["%d) %s [%d]" % (i + 1, item[1], item[0]) for i, item in enumerate(TV_CHANNELS)]
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Список каналов:\n%s" % ("\n".join(tvList)))
	elif u"категории" == param:
		if protocol.TYPE_PUBLIC == msgType:
			sendMsg(msgType, conference, nick, u"Ушли.")
		catlist = ", ".join((info[1] for info in TV_CATEGORIES))
		message = u"Список категорий: %s." % (catlist)
		userjid = getTrueJID(conference, nick)
		if userjid in gUserCategories:
			categories = gUserCategories[userjid]
			if categories:
				catlist = ", ".join(categories.keys())
				message += u"\nВаши категории: %s." % (catlist)
		sendMsg(protocol.TYPE_PRIVATE, conference, nick, message)
	else:
		if param.isdigit():
			info = getChannelInfoByNumber(param)
		else:
			info = getChannelInfoByName(param)
		if info:
			program = getTVProgramByChannel(info[0], when, day)
			if program:
				if protocol.TYPE_PUBLIC == msgType:
					sendMsg(msgType, conference, nick, u"В привате.")
				sendMsg(protocol.TYPE_PRIVATE, conference, nick, u"Телепрограмма для канала \"%s\":\n%s" % (info[1], program))
			else:
				sendMsg(msgType, conference, nick, u"На сегодня программы нет.")
		else:
			userjid = getTrueJID(conference, nick)
			program = None
			category = getUserCategory(userjid, param)
			if category:
				program = getTVProgramByUserCategory(category, when, day)
			else:
				info = getCategoryInfoByName(param)
				if info:
					program = getTVProgramByCategory(info[0], when, day)
				else:
					sendMsg(msgType, conference, nick, u"Не знаю такого канала/категории.")
					return
			if program:
				if protocol.TYPE_PUBLIC == msgType:
					sendMsg(msgType, conference, nick, u"В привате") 
				sendMsg(protocol.TYPE_PRIVATE, conference, nick, u'Программа для категории "%s":\n%s' % (param, program))
			else:
				sendMsg(msgType, conference, nick, u"На сегодня программы для этой категории нет.")

registerEventHandler(loadTVData, EVT_CONNECTED)
registerCommand(showTVProgram, u"тв", 10, 
				u'Показывает телепрограму для определённого канала/категории. Параметр "каналы" - список каналов, параметр "категории" - список категорий. Для получения программы на определённый день/время суток укажите в конце этот день (позавчера, вчера, завтра, послезавтра), либо время суток (утром, днем, вечером, сейчас). Для управления собственными категориями используйте команды "тв+", "тв-", "тв*".',
				u"<канал|категория> [день|время суток]", 
				(u'каналы', u'категории', u'первый', u'первый утром', u'первый завтра'), 
				CMD_ANY | CMD_PARAM)
registerCommand(addTVCategory, u"тв+", 10, 
				u'Добавляет пользовательскую категорию. Категории хранятся отдельно для каждого пользователя. В качестве параметра принимается список, разделённый переводом строки; первый элемент списка - имя категории, остальные элементы - имена каналов, которые можно узнать, отправив боту "тв каналы".',
				u"<список>", 
				None, 
				CMD_ANY | CMD_PARAM)
registerCommand(delTVCategory, u"тв-", 10, 
				u"Удаляет пользовательскую категорию.",
				u"<категория>", 
				(u"новости", ), 
				CMD_ANY | CMD_PARAM)
registerCommand(showTVCategory, u"тв*", 10, 
				u"Просмотр пользовательской категории.",
				u"<категория>", 
				(u"новости", ), 
				CMD_ANY | CMD_PARAM)
