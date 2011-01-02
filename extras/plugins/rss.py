# coding: utf-8
# coding: utf-8

# rss.py
# Initial Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import hashlib
from xmpp import simplexml

RSSITEMS_FILE = 'rssitems.txt'
RSSCACHE_FILE = 'rsscache.txt'

gRSSItems = {}
gRSSCache = {}

TYPE_RSS = 0x1
TYPE_ATOM = 0x2

RSS_UPDATE_TIME = 1800
RSS_CACHE_SIZE = 30

RSS_SEND_INTERVAL = 10

def loadRSSChannels(conference):
	path = getConfigPath(conference, RSSITEMS_FILE)
	utils.createFile(path, '{}')
	gRSSItems[conference] = eval(utils.readFile(path))

	path = getConfigPath(conference, RSSCACHE_FILE)
	utils.createFile(path, '{}')
	gRSSCache[conference] = eval(utils.readFile(path))

def freeRSSChannels(conference):
	del gRSSItems[conference]
	del gRSSCache[conference]

def saveRSSChannels(conference, onlyCache=False):
	if not onlyCache:
		path = getConfigPath(conference, RSSITEMS_FILE)
		utils.writeFile(path, str(gRSSItems[conference]))
	
	path = getConfigPath(conference, RSSCACHE_FILE)
	utils.writeFile(path, str(gRSSCache[conference]))

def cleanRSSCache(conference):
	for url in gRSSCache[conference]:
		cache = gRSSCache[conference][url]
		while len(cache) > RSS_CACHE_SIZE:
			cache.pop()

def sendRSSNews(conference, url, onlyFirst=False):
	response = getURL(url)
	if response:
		rawXML = response.read()
		xmlNode = protocol.simplexml.XML2Node(rawXML)
		if "feed" == xmlNode.getName():
			rssType = TYPE_ATOM
			itemName = "entry"
			textName = "content"
		else:
			rssType = TYPE_RSS
			itemName = "item"
			textName = "description"
			xmlNode = xmlNode.getFirstChild()
		for i, tag in enumerate(xmlNode.getTags(itemName)):
			name = decode(tag.getTagData("title")).strip()
			tagHash = hashlib.md5(name.encode("utf-8")).hexdigest()
			if tagHash not in gRSSCache[conference][url]:
				gRSSCache[conference][url].append(tagHash)
				if not onlyFirst or (onlyFirst and i == 0):
					text = decode(tag.getTagData(textName)).strip()
					if TYPE_ATOM == rssType:
						link = decode(tag.getTag("link").getAttr("href")).strip()
					else:
						link = decode(tag.getTagData("link")).strip()
					sendToConference(conference, u"Тема: %s\n%s\n\nСсылка: %s" % (name, text, link))
					time.sleep(RSS_SEND_INTERVAL)
		
def startRSSQuery(conference):
	for url in gRSSItems[conference].values():
		try:
			sendRSSNews(conference, url)
		except:
			pass
	cleanRSSCache(conference)
	saveRSSChannels(conference, True)

def startRSSQueries():
	for conference in getConferences():
		if gRSSItems[conference]:
			startThread(startRSSQuery, conference)
	startTimer(RSS_UPDATE_TIME, startRSSQueries)

def addRSSChannel(msgType, conference, nick, param):
	param = param.split("=", 1)
	if 2 == len(param):
		name = param[0].strip()
		url = param[1].strip()
		gRSSItems[conference][name] = url
		gRSSCache[conference][url] = []
		if name in gRSSItems[conference]:
			sendMsg(msgType, conference, nick, u"Добавлено")
		else:
			sendMsg(msgType, conference, nick, u"Заменено")
		if getConferenceConfigKey(conference, "rss"):
			sendRSSNews(conference, url, True)
		saveRSSChannels(conference)
	else:
		sendMsg(msgType, conference, nick, u"Читай справку по команде")
	
def delRSSChannel(msgType, conference, nick, param):
	if param in gRSSItems[conference]:
		url = gRSSItems[conference][param]
		del gRSSItems[conference][param]
		del gRSSCache[conference][url]
		saveRSSChannels(conference)
		sendMsg(msgType, conference, nick, u"Удалено")
	else:
		sendMsg(msgType, conference, nick, u"Нет такой ленты")

def showRSSChannels(msgType, conference, nick, param):
	if not param:
		info = []
		for i, name, in enumerate(gRSSItems[conference]):
			info.append(u"%d) %s" % (i + 1, name))
		if info:
			message = u"RSS-ленты:\n%s" % (u"\n".join(info))
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"Нет лент")
	else:
		if param in gRSSItems[conference]:
			url = gRSSItems[conference][param]
			message = u"Инфо о ленте:\nНазвание: %s\nСсылка: %s" % (param, url)
			sendMsg(msgType, conference, nick, message)
		else:
			sendMsg(msgType, conference, nick, u"Нет такой ленты")

registerEventHandler(startRSSQueries, EVT_READY)
registerEventHandler(loadRSSChannels, EVT_ADDCONFERENCE)
registerEventHandler(freeRSSChannels, EVT_DELCONFERENCE)

registerCommand(addRSSChannel, u"рсс+", 30, 
				u"Добавляет рсс-ленту", 
				u"<название = ссылка>", 
				(u"http://server.tld/rss = News"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(delRSSChannel, u"рсс-", 30, 
				u"Удаляет рсс-ленту", 
				u"<название>", 
				(u"новости"), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(showRSSChannels, u"рсс*", 30, 
				u"Показывает рсс-ленты. Если указать название, то выведет подробную информацию", 
				None, 
				None, 
				CMD_CONFERENCE)