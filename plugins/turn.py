# coding: utf-8

# turn.py
# Initial Copyright (с) ???

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

TURN_TABLE = {
	u"~": u"Ё", u"Ё": u"~",
	u"`": u"ё", u"ё": u"`",
	u"#": u"№", u"№": u"#",
	u"q": u"й", u"й": u"q",
	u"w": u"ц", u"ц": u"w",
	u"e": u"у", u"у": u"e",
	u"r": u"к", u"к": u"r",
	u"t": u"е", u"е": u"t",
	u"y": u"н", u"н": u"y",
	u"u": u"г", u"г": u"u",
	u"i": u"ш", u"ш": u"i",
	u"o": u"щ", u"щ": u"o",
	u"p": u"з", u"з": u"p",
	u"a": u"ф", u"ф": u"a",
	u"s": u"ы", u"ы": u"s",
	u"d": u"в", u"в": u"d",
	u"f": u"а", u"а": u"f",
	u"g": u"п", u"п": u"g",
	u"h": u"р", u"р": u"h",
	u"j": u"о", u"о": u"j",
	u"k": u"л", u"л": u"k",
	u"l": u"д", u"д": u"l",
	u"z": u"я", u"я": u"z",
	u"x": u"ч", u"ч": u"x",
	u"c": u"с", u"с": u"c",
	u"v": u"м", u"м": u"v",
	u"b": u"и", u"и": u"b",
	u"n": u"т", u"т": u"n",
	u"m": u"ь", u"ь": u"m",
	u"Q": u"Й", u"Й": u"Q",
	u"W": u"Ц", u"Ц": u"W",
	u"E": u"У", u"У": u"E",
	u"R": u"К", u"К": u"R",
	u"T": u"Е", u"Е": u"T",
	u"Y": u"Н", u"Н": u"Y",
	u"U": u"Г", u"Г": u"U",
	u"I": u"Ш", u"Ш": u"I",
	u"O": u"Щ", u"Щ": u"O",
	u"P": u"З", u"З": u"P",
	u"A": u"Ф", u"Ф": u"A",
	u"S": u"Ы", u"Ы": u"S",
	u"D": u"В", u"В": u"D",
	u"F": u"А", u"А": u"F",
	u"G": u"П", u"П": u"G",
	u"H": u"Р", u"Р": u"H",
	u"J": u"О", u"О": u"J",
	u"K": u"Л", u"Л": u"K",
	u"L": u"Д", u"Д": u"L",
	u"Z": u"Я", u"Я": u"Z",
	u"X": u"Ч", u"Ч": u"X",
	u"C": u"С", u"С": u"C",
	u"V": u"М", u"М": u"V",
	u"B": u"И", u"И": u"B",
	u"N": u"Т", u"Т": u"N",
	u"M": u"Ь", u"Ь": u"M",
	u"[": u"х", u"х": u"[",
	u"{": u"Х", u"Х": u"{",
	u"]": u"ъ", u"ъ": u"]",
	u"}": u"Ъ", u"Ъ": u"}",
	u";": u"ж", u"ж": u";",
	u":": u"Ж", u"Ж": u":",
	u"'": u"э", u"э": u"'",
	u"\"": u"Э", u"Э": u"\"",
	u"<": u"Б", u"Б": u"<",
	u">": u"Ю", u"Ю": u">",
	u"&": u"?", u"?": u"&",
	u"?": u",", u",": u"?",
	u",": u"б", u"б": u",",
	u"|": u"/", u"/": u"|",
	u".": u"ю", u"ю": u".",
	u"/": u".", 
	u"@": u"\"", 
	u"$": u";", 
	u"^": u":"
}

gTurnMsgCache = {}

def getCharForTurn(char):
	return TURN_TABLE.get(char, char)

def turnMessage(text):
	text = "".join(map(getCharForTurn, text))
	return text

def turnLastMessage(msgType, conference, nick, param):
	if param:
		sendMsg(msgType, conference, nick, turnMessage(param))
	else:
		if not msgType == protocol.TYPE_PUBLIC:
			sendMsg(msgType, conference, nick, u"Только в конференции!")
			return
		truejid = getTrueJID(conference, nick)
		if truejid not in gTurnMsgCache[conference]:
			# TODO придумать реплику одинаковой для М и Ж 
			sendMsg(msgType, conference, nick, u"А ты ещё ничего не говорил")
		else:
			savedMsg = gTurnMsgCache[conference][truejid]
			receiver = None
			for userNick in getNicks(conference):
				if savedMsg.startswith(userNick):
					for x in [userNick + x for x in (":", ",")]:
						if savedMsg.startswith(x):
							savedMsg = savedMsg.replace(x, turnMessage(x))
							receiver = userNick
				if receiver:
					break
			if receiver:
				sendToConference(conference, u"%s (от %s)" % (turnMessage(savedMsg), nick))
			else:
				sendMsg(msgType, conference, nick, turnMessage(savedMsg))

def saveTurnMessage(stanza, msgType, conference, nick, truejid, message):
	if msgType == protocol.TYPE_PUBLIC:
		if truejid != gConfig.JID and truejid != conference:
			if "turn" != message.lower():
				gTurnMsgCache[conference][truejid] = message

def initTurnCache(conference):
	gTurnMsgCache[conference] = {}

def freeTurnCache(conference):
	del gTurnMsgCache[conference]

def clearTurnCache(conference, nick, truejid, reason, code):
	if truejid in gTurnMsgCache[conference]:
		del gTurnMsgCache[conference][truejid]

registerEventHandler(initTurnCache, EVT_ADDCONFERENCE)
registerEventHandler(freeTurnCache, EVT_DELCONFERENCE)

registerEventHandler(clearTurnCache, EVT_USERLEAVE)

registerEventHandler(saveTurnMessage, EVT_MSG | H_CONFERENCE)

registerCommand(turnLastMessage, u"turn", 10, 
				u"Переключает раскладку вашего последнего сообщения или текста в параметре команды", 
				u"[текст]", 
				(None, u"jkjkj"))
