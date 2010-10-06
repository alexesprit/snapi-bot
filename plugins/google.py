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

def searchInGoogleAll(msgType, conference, nick, text):
	query = urllib.urlencode({"q" : text.encode("utf-8")})
	url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&hl=ru&%s" % (query)
	searchInGoogle(msgType, conference, nick, url)

def searchInGoogleEN(msgType, conference, nick, text):
	query = urllib.urlencode({"q" : text.encode("utf-8")})
	url = "http://ajax.googleapis.com/ajax/services/search/web?hl=en&v=1.0&%s&lr=lang_en" % (query)
	searchInGoogle(msgType, conference, nick, url)

def searchInGoogleRU(msgType, conference, nick, text):
	query = urllib.urlencode({"q" : text.encode("utf-8")})
	url = "http://ajax.googleapis.com/ajax/services/search/web?hl=ru&v=1.0&%s&lr=lang_ru" % (query)
	searchInGoogle(msgType, conference, nick, url)

def searchInGoogle(msgType, conference, nick, url):
	req = urllib.urlopen(url)
	answer = simplejson.load(req)
	results = answer["responseData"]["results"]
	if(results):
		if(msgType == xmpp.TYPE_PUBLIC):
			msg = ["%(title)s\n%(content)s\n%(unescapedUrl)s" % (results[0])]
		else:
			msg = ["%(title)s\n%(content)s\n%(unescapedUrl)s" % (result) for result in results]
		sendMsg(msgType, conference, nick, decode("\n\n".join(msg)))
	else:
		sendMsg(msgType, conference, nick, u"не найдено")

registerCommand(searchInGoogleEN, u"гугльен", 10, 
				u"Поиск через Google по зарубежным сайтам", 
				u"гугльен <текст>", 
				(u"гугльен yandex", ), 
				ANY | PARAM)
registerCommand(searchInGoogleRU, u"гугльру", 10, 
				u"Поиск через Google по русскоязычным сайтам", 
				u"гугльру <текст>", 
				(u"гугльру yandex", ), 
				ANY | PARAM)
registerCommand(searchInGoogleAll, u"гугль", 10, 
				u"Поиск через Google", 
				u"гугль <текст>", 
				(u"гугль yandex", ), 
				ANY | PARAM)
