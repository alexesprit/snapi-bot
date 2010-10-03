# coding: utf-8

# dumpz.py

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import urllib2

DUMPZ_LANGS_FILE = "languages.txt"

DUMPZ_LANGS = {}

def uploadToDumpz(msgType, conference, nick, param):
	if(param):
		args = param.split(None, 1)
		lang = args[0]
		if(lang in DUMPZ_LANGS):
			if(len(args) == 2):
				text = args[1]
			else:
				sendMsg(msgType, conference, nick, u"а где тескт?")
				return
		else:
			text = param
			lang = "text"
		query = urllib.urlencode({"lexer": lang, "code": text.encode("utf-8")})
		req = urllib2.Request("http://dumpz.org/", query, {"Content-type": "application/x-www-form-urlencoded"})
		res = urllib2.urlopen(req)
		sendMsg(msgType, conference, nick, u"залито на %s" % (res.url))
	else:
		langs = [u"%s - %s" % (lang, name) \
				for lang, name in DUMPZ_LANGS.items()]
		langs.sort()
		message = u"Доступные языки:\n%s" % ("\n".join(langs))
		sendMsg(msgType, conference, nick, message)

def loadDumpzLanguages():
	global DUMPZ_LANGS
	fileName = getFilePath(RESOURCE_DIR, DUMPZ_LANGS_FILE)
	DUMPZ_LANGS = eval(readFile(fileName))

registerEvent(loadDumpzLanguages, STARTUP)

registerCommand(uploadToDumpz, u"пастебин", 10, 
				u"Заливает текст на пастебин-сервис dumpz.org. Без параметров покажет доступные языки", 
				u"пастебин [язык] [текст]", 
				(u"пастебин This is text", u"пастебин cpp int *n, *p;"));