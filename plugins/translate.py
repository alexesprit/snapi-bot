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

def getTranslateQuery(text, langpair=None):
	param = {
		"v": "1.0", 
		"q": text.encode("utf-8")
	}
	if langpair:
		param["langpair"] = langpair
	return param

def getTranslatedText(text, source, target):
	url = "http://ajax.googleapis.com/ajax/services/language/translate"
	langpair = "%s|%s" % (source, target)
	qparam = getTranslateQuery(text, langpair)
	response = getURL(url, qparam)
	if response:
		answer = simplejson.load(response)
		if answer["responseData"]:
			return answer["responseData"]["translatedText"]
	return None

def detectLanguage(text):
	url = "http://ajax.googleapis.com/ajax/services/language/detect"
	qparam = getTranslateQuery(text)
	response = getURL(url, qparam)
	if response:
		answer = simplejson.load(response)
		if answer["responseData"]:
			return answer["responseData"]["language"]
	return None

def translateText(msgType, conference, nick, param):
	if param.lower() == u"языки":
		elements = [u"%s - %s" % (lang, name)
				for lang, name in TRANSL_LANGS.items()]
		elements.sort()
		message = u"Доступные языки:\n%s" % ("\n".join(elements))
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

registerEvent(loadLangsForTranslate, EVT_STARTUP)

registerCommand(translateText, u"перевод", 10, 
				u"Перевод текста с одного языка на другой. Указав \"языки\" в кач-ве параметра можно посмотреть доступные языки для перевода", 
				u"<исходный_язык> <нужный_язык> <фраза>", 
				(u"языки", u"en ru hello", u"ru en привет"), 
				CMD_ANY | CMD_PARAM)
