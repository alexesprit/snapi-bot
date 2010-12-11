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

DUMPZ_LANGS_FILE = "dumpzlangs.txt"

def loadLangsForDumpz():
	global DUMPZ_LANGS
	path = getFilePath(RESOURCE_DIR, DUMPZ_LANGS_FILE)
	DUMPZ_LANGS = eval(utils.readFile(path))

def uploadToDumpz(msgType, conference, nick, param):
	if u"языки" == param.lower():
		elements = [u"%s - %s" % (lang, name) \
				for lang, name in DUMPZ_LANGS.items()]
		elements.sort()
		message = u"Доступные языки:\n%s" % ("\n".join(elements))
		sendMsg(msgType, conference, nick, message)
	else:
		args = param.split(None, 1)
		lang = args[0]
		if lang in DUMPZ_LANGS:
			if len(args) == 2:
				text = args[1]
			else:
				sendMsg(msgType, conference, nick, u"А где тескт?")
				return
		else:
			text = param
			lang = "text"
		url = "http://dumpz.org/"
		data = {
			"lexer": lang,
			"code": text.encode("utf-8")
		}
		headers = {"Content-type": "application/x-www-form-urlencoded"}
		response = getURL(url, None, data, headers)
		if response:
			sendMsg(msgType, conference, nick, u"Залито на %s" % (response.url))
		else:
			sendMsg(msgType, conference, nick, u"Ошибка!")

registerEventHandler(loadLangsForDumpz, EVT_STARTUP)

registerCommand(uploadToDumpz, u"пастебин", 10, 
				u"Заливает текст на пастебин-сервис dumpz.org. Чтобы получить список поддерживаемых языков, укажите \"языки\" в кач-ве параметра", 
				u"[язык] <текст>", 
				(u"языки", u"This is text", u"cpp int *n, *p;"), 
				CMD_ANY | CMD_PARAM);