# coding: utf-8

# google.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

def getGoogleSearchQuery(text, lang=None):
	param = {
		"v": "1.0",
		"q": text.encode("utf-8")
	}
	if lang:
		param["lr"] = lang
	return param

def searchInGoogleAll(msgType, conference, nick, text):
	url = "http://ajax.googleapis.com/ajax/services/search/web"
	qparam = getGoogleSearchQuery(text)
	searchInGoogle(msgType, conference, nick, url, qparam)

def searchInGoogleEN(msgType, conference, nick, text):
	url = "http://ajax.googleapis.com/ajax/services/search/web"
	qparam = getGoogleSearchQuery(text, "lang_en")
	searchInGoogle(msgType, conference, nick, url, qparam)

def searchInGoogleRU(msgType, conference, nick, text):
	url = "http://ajax.googleapis.com/ajax/services/search/web"
	qparam = getGoogleSearchQuery(text, "lang_ru")
	searchInGoogle(msgType, conference, nick, url, qparam)

def searchInGoogle(msgType, conference, nick, url, qparam):
	response = getURL(url, qparam)
	if response:
		response = simplejson.load(response)
		results = response["responseData"]["results"]
		if results:
			if msgType == protocol.TYPE_PUBLIC:
				results = results[:1]
			print results
			elements = ["%(title)s\n%(content)s\n%(unescapedUrl)s" % (result) for result in results]
			sendMsg(msgType, conference, nick, decode("\n\n".join(elements)))
		else:
			sendMsg(msgType, conference, nick, u"Не найдено!")
	else:
		sendMsg(msgType, conference, nick, u"Ошибка!")

registerCommand(searchInGoogleEN, u"гугльен", 10, 
				u"Поиск через Google по зарубежным сайтам", 
				u"<текст>", 
				(u"yandex", ), 
				CMD_ANY | CMD_PARAM)
registerCommand(searchInGoogleRU, u"гугльру", 10, 
				u"Поиск через Google по русскоязычным сайтам", 
				u"<текст>", 
				(u"yandex", ), 
				CMD_ANY | CMD_PARAM)
registerCommand(searchInGoogleAll, u"гугль", 10, 
				u"Поиск через Google", 
				u"<текст>", 
				(u"yandex", ), 
				CMD_ANY | CMD_PARAM)
