# coding: utf-8;

# votes.py
# Initial Copyright (c) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

VOTES_FILE = "votes.txt"

VOTE_CREATED = 0x1
VOTE_STARTED = 0x2
VOTE_FINISHED = 0x3

gVote = {}

def loadVotes(conference):
	path = getConfigPath(conference, VOTES_FILE)
	gVote[conference] = eval(utils.readFile(path, "{}"))

def freeVotes(conference):
	del gVote[conference]

def getVoteText(conference):
	voteText = u"Текущее голосование\nСоздатель: %(creator)s\n%(text)s\n" % (gVote[conference])
	elements = [u" %d) %s" % (i + 1, x[0]) for i, x in enumerate(gVote[conference]["opinions"])]
	voteText += "\n".join(elements)
	voteText += u"\nЧтобы проголосовать, напиши номер мнения, например \"мнение 1\""
	return voteText

def getVoteResults(conference):
	answers = [[x[1], x[0]] for x in gVote[conference]["opinions"]]
	answers.sort()
	answers.reverse()
	voteText = u"Результаты голосования\nСоздатель: %(creator)s\n%(text)s\n%%s" % (gVote[conference])
	elements = [u" %d) %s (%d голосов)" % (i + 1, x[1], x[0]) for i, x in enumerate(answers)]
	return voteText % ("\n".join(elements))

def saveVotes(conference):
	path = getConfigPath(conference, VOTES_FILE)
	utils.writeFile(path, str(gVote[conference]))

def vote(msgType, conference, nick, param):
	if gVote[conference]:
		if gVote[conference]["state"] == VOTE_FINISHED:
			sendMsg(msgType, conference, nick, u"Голосование уже завершено!")
		elif gVote[conference]["state"] == VOTE_CREATED:
			sendMsg(msgType, conference, nick, u"Голосование ещё не запущено")
		else:
			truejid = getTrueJID(conference, nick)
			if not truejid in gVote[conference]["voted"]:
				gVote[conference]["voted"][truejid] = False
			if not gVote[conference]["voted"][truejid]:
				try:
					param = int(param) - 1
					if param >= 0:
						gVote[conference]["opinions"][param][1] += 1
						gVote[conference]["voted"][truejid] = True
						saveVotes(conference)
						
						sendMsg(msgType, conference, nick, u"Поняла")
					else:
						raise IndexError
				except ValueError:
					sendMsg(msgType, conference, nick, u"Чтобы проголосовать, нужно указать номер мнения!")
				except IndexError:
					sendMsg(msgType, conference, nick, u"Нет такого пункта")
			else:
				sendMsg(msgType, conference, nick, u"2-ой раз голосовать не надо :P")
	else:
		sendMsg(msgType, conference, nick, u"Сейчас нет никаких голосований")

def createNewVote(msgType, conference, nick, param):
	if param:
		if gVote[conference] and gVote[conference]["state"] != VOTE_FINISHED:
			sendMsg(msgType, conference, nick, u"Имеется неоконченное голосование")
		else:
			gVote[conference] = {
				"state": VOTE_CREATED, 
				"creator": nick, 
				"creatorjid": getTrueJID(conference, nick), 
				"text": param, 
				"voted": {}, 
				"opinions": []
			}
			saveVotes(conference)
			sendMsg(msgType, conference, nick, u"Голосование создано! Чтобы добавить пункты напиши \"пункт+ твой_пункт\", удалить - \"пункт- номер пункта\". Начать голосование - команда \"голосование+\". Посмотреть текущие результаты - команда \"мнения\". Окончить голосование - команда \"итоги\"")
	else:
		if gVote[conference]:
			if gVote[conference]["state"] == VOTE_FINISHED:
				sendMsg(msgType, conference, nick, getVoteResults(conference))
			elif gVote[conference]["state"] == VOTE_STARTED:
				sendMsg(msgType, conference, nick, getVoteText(conference))
			else:
				sendMsg(msgType, conference, nick, u"Голование создано, но ещё не запущено")
		else:
			sendMsg(msgType, conference, nick, u"Сейчас нет никаких голосований")

def startVote(msgType, conference, nick, parameters):
	if gVote[conference]:
		if gVote[conference]["state"] == VOTE_STARTED:
			sendMsg(msgType, conference, nick, u"Голосование уже запущено")
		elif gVote[conference]["state"] == VOTE_FINISHED:
			sendMsg(msgType, conference, nick, u"Голосование было завершено")
		elif not gVote[conference]["opinions"]:
			sendMsg(msgType, conference, nick, u"Голосование не имеет пунктов")
		else:
			truejid = getTrueJID(conference, nick)
			creatorjid = gVote[conference]["creatorjid"]
			if creatorjid == truejid or getAccess(conference, truejid) >= 20:
				gVote[conference]["state"] = VOTE_STARTED
				saveVotes(conference)
				sendToConference(conference, getVoteText(conference))
			else:
				sendMsg(msgType, conference, nick, u"Недостаточно прав")
	else:
		sendMsg(msgType, conference, nick, u"Сейчас нет никаких голосований")

def stopVote(msgType, conference, nick, param):
	if gVote[conference]:
		if gVote[conference]["state"] == VOTE_FINISHED:
			sendMsg(msgType, conference, nick, u"Неприменимо к оконченному голосованию")
		elif gVote[conference]["state"] == VOTE_STARTED:
			truejid = getTrueJID(conference, nick)
			creatorjid = gVote[conference]["creatorjid"]
			if creatorjid == truejid or getAccess(conference, truejid) >= 20:
				gVote[conference]["state"] = VOTE_CREATED
				saveVotes(conference)
				sendMsg(msgType, conference, nick, u"Голосование приостановлено")
			else:
				sendMsg(msgType, conference, nick, u"Недостаточно прав")
		else:
			sendMsg(msgType, conference, nick, u"Голосование уже приостановлено")
	else:
		sendMsg(msgType, conference, nick, u"Сейчас нет никаких голосований")

def addOpinion(msgType, conference, nick, param):
	if gVote[conference]:
		if gVote[conference]["state"] == VOTE_STARTED:
			sendMsg(msgType, conference, nick, u"Неприменимо к запущеному голосованию, останови и добавь пункты")
		elif gVote[conference]["state"] == VOTE_FINISHED:
			sendMsg(msgType, conference, nick, u"Неприменимо к оконченному голосованию")
		else:
			truejid = getTrueJID(conference, nick)
			creatorjid = gVote[conference]["creatorjid"]
			if creatorjid == truejid or getAccess(conference, truejid) >= 20:
				if param in [x[0] for x in gVote[conference]["opinions"]]:
					sendMsg(msgType, conference, nick, u"уже есть такой пункт")
				else:
					gVote[conference]["opinions"].append([param, 0])
					saveVotes(conference)
					sendMsg(msgType, conference, nick, u"Добавила")
			else:
				sendMsg(msgType, conference, nick, u"Недостаточно прав")
	else:
		sendMsg(msgType, conference, nick, u"Сейчас нет никаких голосований")

def delOpinion(msgType, conference, nick, param):
	if gVote[conference]:
		if gVote[conference]["state"] == VOTE_STARTED:
			sendMsg(msgType, conference, nick, u"Неприменимо к запущеному голосованию, останови и удали пункты")
		elif gVote[conference]["state"] == VOTE_FINISHED:
			sendMsg(msgType, conference, nick, u"Неприменимо к оконченному голосованию")
		else:
			truejid = getTrueJID(conference, nick)
			creatorjid = gVote[conference]["creatorjid"]
			if creatorjid == truejid or getAccess(conference, truejid) >= 20:
				try:
					param = int(param) - 1
					if param >= 0:
						del gVote[conference]["opinions"][param]
						saveVotes(conference)
						
						sendMsg(msgType, conference, nick, u"Удалила")
					else:
						raise IndexError
				except ValueError:
					sendMsg(msgType, conference, nick, u"Чтобы удалить пункт, нужно указать его номер!")
				except IndexError:
					sendMsg(msgType, conference, nick, u"Нет такого пункта")
			else:
				sendMsg(msgType, conference, nick, u"Недостаточно прав")
	else:
		sendMsg(msgType, conference, nick, u"Сейчас нет никаких голосований")

def showOpinions(msgType, conference, nick, param):
	if gVote[conference]:
		if gVote[conference]["state"] == VOTE_FINISHED:
			sendMsg(msgType, conference, nick, getVoteResults(conference))
		else:
			truejid = getTrueJID(conference, nick)
			creatorjid = gVote[conference]["creatorjid"]
			if creatorjid == truejid or getAccess(conference, truejid) >= 20:
				if protocol.TYPE_PUBLIC == msgType:
					sendMsg(msgType, conference, nick, u"Ушли")
				sendMsg(protocol.TYPE_PRIVATE, conference, nick, getVoteResults(conference))
			else:
				sendMsg(msgType, conference, nick, u"Жди окончания голосования :-p")
	else:
		sendMsg(msgType, conference, nick, u"Сейчас нет никаких голосований")

def endVote(msgType, conference, nick, param):
	if gVote[conference]:
		if gVote[conference]["state"] == VOTE_FINISHED:
			sendMsg(msgType, conference, nick, u"Голосование уже закончено, просмотр мнений - команда \"мнения\"")
		else:
			truejid = getTrueJID(conference, nick)
			creatorjid = gVote[conference]["creatorjid"]
			if creatorjid == truejid or getAccess(conference, truejid) >= 20:
				gVote[conference]["state"] = VOTE_FINISHED
				del gVote[conference]["voted"]
				saveVotes(conference)
				sendToConference(conference, getVoteResults(conference))
			else:
				sendMsg(msgType, conference, nick, u"Недостаточно прав")
	else:
		sendMsg(msgType, conference, nick, u"Сейчас нет никаких голосований")

def showVote(conference, nick, truejid, aff, role):
	if gVote[conference]:
		if gVote[conference]["state"] == VOTE_STARTED:
			if not truejid in gVote[conference]["voted"]:
				gVote[conference]["voted"][truejid] = False
				saveVotes(conference)
				sendMsg(protocol.TYPE_PRIVATE, conference, nick, getVoteText(conference))

registerEventHandler(loadVotes, EVT_ADDCONFERENCE)
registerEventHandler(freeVotes, EVT_DELCONFERENCE)

registerEventHandler(showVote, EVT_USERJOIN)

registerCommand(vote, u"мнение", 10, 
				u"Для подачи мнения в текущем голосовании", 
				u"<номер>", 
				(u"1", ), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(createNewVote, u"голосование", 11, 
				u"Создает новое голосование или показывает текущее (если имеется)", 
				u"[текст]", 
				(None, u"винды - сакс!"), 
				CMD_CONFERENCE)
registerCommand(startVote, u"голосование+", 11, 
				u"Запускает голосование (если оно создано и имеет пункты)", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
registerCommand(stopVote, u"голосование-", 11, 
				u"Останавливает голосование, все данные сохраняются до продолжения голосования", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
registerCommand(addOpinion, u"пункт+", 11, 
				u"Добавляет пункт к текущему голосованию", 
				u"<пункт>", 
				(u"да", ), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(delOpinion, u"пункт-", 11, 
				u"Удаляет пункт из голосования. Пункт указывается его номером", 
				u"<номер_пункта>", 
				(u"5", ), 
				CMD_CONFERENCE | CMD_PARAM)
registerCommand(showOpinions, u"мнения", 11, 
				u"Отдаёт текущие результаты голосования в приват, не завершая голосования при этом", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)
registerCommand(endVote, u"итоги", 11, 
				u"Завершает голование и показывает его результаты", 
				None, 
				None, 
				CMD_CONFERENCE | CMD_NONPARAM)