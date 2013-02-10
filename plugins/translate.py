# coding: utf-8

# translate.py
# Initial Copyright (c) 2007 Als <Als@exploit.in>
# Parts of code Copyright (c) Krishna Pattabiraman (PyTrans project) <http://code.google.com/p/pytrans/>
# Modification Copyright (c) esprit

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from module import simplejson

TRANSL_LANGS_FILE = "transllangs.txt"

def getTranslateLangs():
	path = getFilePath(RESOURCE_DIR, TRANSL_LANGS_FILE)
	return eval(io.read(path))

def getTranslatedText(text, source, target, detailed):
	url = "http://translate.google.ru/translate_a/t"
	qparam = {
		"client": "x",
		"text": text.encode("utf-8"),
		"sl": source,
		"tl": target
	}
	response = netutil.getURLResponse(url, qparam)
	if response:
		rawdata = simplejson.load(response)
		try:
			detailed &= ("dict" in rawdata)
			if detailed:
				elements = []
				for d in rawdata["dict"]:
					for e in d["entry"]:
						word = e["word"]
						transl = ", ".join(r for r in e["reverse_translation"])
						elements.append("* %s (%s)" % (word, transl))
				result = "\n".join(elements)
			else:
				result = "".join(s["trans"] for s in rawdata["sentences"])
				if not source:
					src = rawdata["src"]
					result = "%s [%s]" % (result, src)
			return result
		except KeyError, IndexError:
			print "cant translate: %s [%s -> %s]" % (text, source, target)
	return None

def translateText(msgType, conference, nick, param):
	if param.lower() == u"языки":
		elements = [u"%s - %s" % (name, lang)
				for lang, name in getTranslateLangs().items()]
		elements.sort()
		message = u"Доступные языки:\n%s" % ("\n".join(elements))
		sendMsg(msgType, conference, nick, message)
	else:
		args = param.split(None, 2)
		if len(args) >= 2:
			source = args[0]
			target = args[1]
			langs = getTranslateLangs()
			if source in langs:
				# maybe target is a text
				if target not in langs:
					args = param.split(None, 1)
					target, text = args
					source = ""
				else:
					if 3 == len(args):
						text = args[2]
					else:
						sendMsg(msgType, conference, nick, u"Вы не указали текст для перевода!")
						return
				detailed = (msgType == protocol.TYPE_PRIVATE)
				text = getTranslatedText(text, source, target, detailed)
				if text:
					sendMsg(msgType, conference, nick, netutil.unescapeHTML(text))
				else:
					sendMsg(msgType, conference, nick, u"Не могу перевести")

registerCommand(translateText, u"перевод", 10,
				u"Переводит текст с одного языка на другой. Чтобы получить список доступных языков для перевода, укажите \"языки\" в кач-ве параметра",
				u"[исходный_язык] <нужный_язык> <фраза>",
				(u"языки", u"en привет", u"en ru hello"),
				CMD_ANY | CMD_PARAM)
