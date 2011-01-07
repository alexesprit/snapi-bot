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

import simplejson

TRANSL_LANGS_FILE = "transllangs.txt"

def loadLangsForTranslate():
	global TRANSL_LANGS
	path = getFilePath(RESOURCE_DIR, TRANSL_LANGS_FILE)
	TRANSL_LANGS = eval(utils.readFile(path, "utf-8"))

def getTranslatedText(text, source, target):
	url = "http://ajax.googleapis.com/ajax/services/language/translate"
	qparam = {
		"v": "1.0", 
		"q": text.encode("utf-8"), 
		"langpair": "%s|%s" % (source, target)
	}
	response = getURL(url, qparam)
	if response:
		rawdata = simplejson.load(response)
		if rawdata["responseData"]:
			return rawdata["responseData"]["translatedText"]
	return None

def translateText(msgType, conference, nick, param):
	if param.lower() == u"языки":
		elements = [u"%s - %s" % (name, lang)
				for lang, name in TRANSL_LANGS.items()]
		elements.sort()
		message = u"Доступные языки:\n%s" % ("\n".join(elements))
		sendMsg(msgType, conference, nick, message)
	else:
		args = param.split(None, 2)
		if len(args) >= 2:
			source = args[0]
			target = args[1]
			if source in TRANSL_LANGS:
				# maybe target is a text
				if target not in TRANSL_LANGS:
					args = param.split(None, 1)
					target, text = args
					source = ""
				else:
					if 3 == len(args):
						text = args[2]
					else:
						sendMsg(msgType, conference, nick, u"Вы не указали текст для перевода!")
						return
				text = getTranslatedText(text, source, target)
				if text:
					sendMsg(msgType, conference, nick, utils.unescapeHTML(text))
				else:
					sendMsg(msgType, conference, nick, u"Не могу перевести")

registerEventHandler(loadLangsForTranslate, EVT_STARTUP)

registerCommand(translateText, u"перевод", 10, 
				u"Переводит текст с одного языка на другой. Чтобы получить список доступных языков для перевода, укажите \"языки\" в кач-ве параметра",
				u"[исходный_язык] <нужный_язык> <фраза>", 
				(u"языки", u"en привет", u"en ru hello"), 
				CMD_ANY | CMD_PARAM)
