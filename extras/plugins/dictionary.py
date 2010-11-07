# coding: utf-8

# dictionary.py
# Initial Copyright (с) 2010 -Esprit-

# Плагин показывает информацию о слове/выражении, используя Google Dictionary.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

DICTIONARY_LANGPAIRS = {
	"en en": u"английский - словарь", 
	"en ar": u"английский - арабский", 
	"en bn": u"английский - бенгальский", 
	"en bg": u"английский - болгарский", 
	"en el": u"английский - греческий", 
	"en gu": u"английский - гуджарати", 
	"en iw": u"английский - иврит", 
	"en es": u"английский - испанский", 
	"en it": u"английский - итальянский", 
	"en kn": u"английский - каннада", 
	"en zh-TW": u"английский - китайский (традиционный)", 
	"en zh-CN": u"английский - китайский (упрощенный)", 
	"en ko": u"английский - корейский", 
	"en ml": u"английский - малайялам", 
	"en mr": u"английский - маратхи", 
	"en de": u"английский - немецкий", 
	"en pt": u"английский - португальский", 
	"en ru": u"английский - русский", 
	"en sr": u"английский - сербский", 
	"en th": u"английский - тайский", 
	"en ta": u"английский - тамильский", 
	"en te": u"английский - телугу", 
	"en fi": u"английский - финский", 
	"en fr": u"английский - французский", 
	"en hi": u"английский - хинди", 
	"en hr": u"английский - хорватский", 
	"en cs": u"английский - чешский", 
	"ar en": u"арабский - английский", 
	"bn en": u"бенгальский - английский", 
	"bg en": u"болгарский - английский", 
	"nl nl": u"голландский – словарь", 
	"el en": u"греческий - английский", 
	"gu en": u"гуджарати - английский", 
	"iw en": u"иврит - английский", 
	"es en": u"испанский - английский", 
	"es es": u"испанский – словарь", 
	"it en": u"итальянский - английский", 
	"it it": u"итальянский – словарь", 
	"kn en": u"каннада - английский", 
	"zh-TW en": u"китайский (традиционный) - английский", 
	"zh-TW zh-TW": u"китайский (традиционный) – словарь", 
	"zh-CN en": u"китайский (упрощенный) - английский", 
	"zh-CN zh-CN": u"китайский (упрощенный) – словарь", 
	"ko en": u"корейский - английский", 
	"ko ko": u"корейский – словарь", 
	"ml en": u"малайялам - английский", 
	"mr en": u"маратхи - английский", 
	"de en": u"немецкий - английский", 
	"de de": u"немецкий – словарь", 
	"pt en": u"португальский - английский", 
	"pt pt": u"португальский – словарь", 
	"ru en": u"русский - английский", 
	"ru ru": u"русский – словарь", 
	"sr en": u"сербский - английский", 
	"th en": u"тайский - английский", 
	"ta en": u"тамильский - английский", 
	"te en": u"телугу - английский", 
	"fi en": u"финский - английский", 
	"fr en": u"французский - английский", 
	"fr fr": u"французский – словарь", 
	"hi en": u"хинди - английский", 
	"hr en": u"хорватский - английский", 
	"cs en": u"чешский - английский", 
	"cs cs": u"чешский – словарь"
}

def searchInGoogleDict(msgType, conference, nick, param):
	if param == u"языки":
		langs = [u"%s: %s" % (lang, name)
				for lang, name in DICTIONARY_LANGPAIRS.items()]
		langs.sort()
		message = u"Доступные пары языков:\n%s" % ("\n".join(langs))
		sendMsg(msgType, conference, nick, message)
	else:
		param = param.split(None, 2)
		if len(param) == 3:
			src, target, text = param
			if not ("%s %s" % (src, target)) in DICTIONARY_LANGPAIRS:
				sendMsg(msgType, conference, nick, u"читай справку по команде")
				return
			param = {
				"q": text.encode("utf-8"), 
				"langpair": "%s|%s" % (src, target) 
			}
			query = urllib.urlencode(param)
			url = "http://www.google.com/dictionary?%s" % (query)
			rawHTML = urllib.urlopen(url).read()
			rawHTML = unicode(rawHTML, "utf-8")
			message = []
			valueItems = re.findall(r"<li class=\"dct-ec\".+?>(.+?)</ul>\n</li>", rawHTML, re.DOTALL)
			if valueItems:
				for item in valueItems:
					partOfSpeech = re.search(r"Part-of-speech\">(.+?)</span>", item)
					meanings = re.findall(r"span class=\"dct-tt\">(.+?)</span>", item)
					message.append(partOfSpeech.group(1))
					for mean in meanings:
						message.append(u" * %s" % (mean))
				similarPhrases = re.search(r"<ul class=\"rlt-snt\">(.+?)</ul>", rawHTML, re.DOTALL)
				similarPhrases = similarPhrases.group(1)
				phrases = re.findall(r"<a href.+?>(.+?)</a>(.+?)</li>", similarPhrases, re.DOTALL)
				if phrases:
					message.append(u"\nПохожие фразы:")
					for i, phrase in enumerate(phrases):
						message.append(u"%d) %s" % (i + 1, phrase[0]))
						items = re.findall(r"</b>.\n(.+?)\n", phrase[1])
						if items:
							for item in items:
								message.append(u" * %s" % (item))
						else:
							phrase = decode(phrase[1]).strip()
							message.append(u" * %s" % (phrase))
				sendMsg(msgType, conference, nick, u"\n".join(message))
			else:
				sendMsg(msgType, conference, nick, u"не найдено")
		else:
			sendMsg(msgType, conference, nick, u"читай справку по команде")

registerCommand(searchInGoogleDict, u"определение", 10, 
				u"Поиск значения слова/выражения через Google Dictionary", 
				u"определение <исходный_язык> <нужный_язык> <текст>", 
				(u"определение en ru unity", ), 
				ANY | PARAM)
