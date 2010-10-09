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

LANGUAGES = {u"en": u"английский", u"ja": u"японский", u"ru": u"русский", u"auto": u"Определить язык", u"sq": u"албанский", 
			u"en": u"английский", u"ar": u"арабский", u"af": u"африкаанс", u"be": u"белорусский", u"bg": u"болгарский", 
			u"cy": u"валлийский", u"hu": u"венгерский", u"vi": u"вьетнамский", u"gl": u"галисийский", u"nl": u"голландский", 
			u"el": u"греческий", u"da": u"датский", u"iw": u"иврит", u"yi": u"идиш", u"id": u"индонезийский", u"ga": u"ирландский", 
			u"is": u"исландский", u"es": u"испанский", u"it": u"итальянский", u"ca": u"каталанский", u"zh-CN": u"китайский", 
			u"ko": u"корейский", u"lv": u"латышский", u"lt": u"литовский", u"mk": u"македонский", u"ms": u"малайский", 
			u"mt": u"мальтийский", u"de": u"немецкий", u"no": u"норвежский", u"fa": u"персидский", u"pl": u"польский", 
			u"pt": u"португальский", u"ro": u"румынский", u"ru": u"русский", u"sr": u"сербский", u"sk": u"словацкий", 
			u"sl": u"словенский", u"sw": u"суахили", u"tl": u"тагальский", u"th": u"тайский", u"tr": u"турецкий", u"uk": u"украинский", 
			u"fi": u"финский", u"fr": u"французский", u"hi": u"хинди", u"hr": u"хорватский", u"cs": u"чешский", u"sv": u"шведский", 
			u"et": u"эстонский"}

def translateText(msgType, conference, nick, param):
	if(param == u"языки"):
		langs = [u"%s - %s" % (lang, name) \
				for lang, name in LANGUAGES.items()]
		langs.sort()
		message = u"Доступные языки:\n%s" % ("\n".join(langs))
		sendMsg(msgType, conference, nick, message)
	else:
		param = param.split(None, 2)
		if(len(param) == 3):
			(src, target, text) = param
			if(src in LANGUAGES and target in LANGUAGES):
				if(src == "auto"):
					if(target == "auto"):
						sendMsg(msgType, conference, nick, u"ошибочный запрос. прочитай помощь по использованию команды")
						return
					else:
						src = detectLanguage(text)
						if(src):
							if(not src in LANGUAGES):
								sendMsg(msgType, conference, nick, u"не могу понять, что это за язык (%s)" % (src))
								return
						else:
							sendMsg(msgType, conference, nick, u"не могу перевести")
				text = getTranslatedText(text, src, target)
				if(text):
					sendMsg(msgType, conference, nick, xmpp.simplexml.XMLUnescape(text))
				else:
					sendMsg(msgType, conference, nick, u"не могу перевести")

def getTranslatedText(text, src, target):
	try:
		query = urllib.urlencode({"q" : text.encode("utf-8")})
		req = urllib.urlopen("http://ajax.googleapis.com/ajax/services/language/translate?v=1.0&%s&langpair=%s%s" % (query, src + "%7C", target))
		answer = simplejson.load(req)
		if(answer["responseData"]):
			return(answer["responseData"]["translatedText"])
	except(KeyError):
		return(None)

def detectLanguage(text):
	try:
		query = urllib.urlencode({"q" : text.encode("utf-8")})
		req = urllib.urlopen("http://ajax.googleapis.com/ajax/services/language/detect?v=1.0&%s" % (query))
		answer = simplejson.load(req)
		if(answer["responseData"]):
			return(answer["responseData"]["language"])
	except(KeyError):
		return(None)

registerCommand(translateText, u"перевод", 10, 
				u"Перевод текста с одного языка на другой. Указав \"языки\" в кач-ве параметра можно посмотреть доступные языки для перевода", 
				u"перевод <исходный_язык> <нужный_язык> <фраза>", 
				(u"перевод en ru hello", u"перевод ru en привет"), 
				ANY | PARAM)
