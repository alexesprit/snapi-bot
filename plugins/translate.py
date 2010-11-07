# coding: utf-8

# translate.py
# Initial Copyright (c) 2007 Als <Als@exploit.in>
# Parts of code Copyright (c) Krishna Pattabiraman (PyTrans project) <http://code.google.com/p/pytrans/>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

TRANSL_LANGS_FILE = "transllangs.txt"

def loadLangsForTranslate():
	global TRANSL_LANGS
	path = getFilePath(RESOURCE_DIR, TRANSL_LANGS_FILE)
	TRANSL_LANGS = eval(utils.readFile(path, "utf-8"))

def getTranslateQuery(text):
	param = {
		"v": "1.0", 
		"q": text.encode("utf-8")
	}
	query = urllib.urlencode(param)
	return query

def getTranslatedText(text, source, target):
	query = getTranslateQuery(text)
	url = "http://ajax.googleapis.com/ajax/services/language/translate?%s&langpair=%s|%s" % (query, source, target)
	request = urllib.urlopen(url)
	answer = simplejson.load(request)
	if answer["responseData"]:
		return answer["responseData"]["translatedText"]
	return None

def detectLanguage(text):
	query = getTranslateQuery(text)
	url = "http://ajax.googleapis.com/ajax/services/language/detect?%s" % (query)
	request = urllib.urlopen(url)
	answer = simplejson.load(request)
	if answer["responseData"]:
		return answer["responseData"]["language"]
	return None

def translateText(msgType, conference, nick, param):
	if param.lower() == u"языки":
		langs = [u"%s - %s" % (lang, name)
				for lang, name in TRANSL_LANGS.items()]
		langs.sort()
		message = u"Доступные языки:\n%s" % ("\n".join(langs))
		sendMsg(msgType, conference, nick, message)
	else:
		param = param.split(None, 2)
		if len(param) == 3:
			source, target, text = param
			if source in TRANSL_LANGS and target in TRANSL_LANGS:
				if source == "auto":
					if target == "auto":
						sendMsg(msgType, conference, nick, u"Читай помощь по команде")
						return
					else:
						source = detectLanguage(text)
						if source:
							if not source in TRANSL_LANGS:
								sendMsg(msgType, conference, nick, u"Не могу понять, что это за язык (%s)" % (source))
								return
						else:
							sendMsg(msgType, conference, nick, u"Не могу перевести")
				text = getTranslatedText(text, source, target)
				if text:
					sendMsg(msgType, conference, nick, utils.unescapeHTML(text))
				else:
					sendMsg(msgType, conference, nick, u"Не могу перевести")

registerEvent(loadLangsForTranslate, STARTUP)

registerCommand(translateText, u"перевод", 10, 
				u"Перевод текста с одного языка на другой. Указав \"языки\" в кач-ве параметра можно посмотреть доступные языки для перевода", 
				u"перевод <исходный_язык> <нужный_язык> <фраза>", 
				(u"перевод en ru hello", u"перевод ru en привет"), 
				ANY | PARAM)
