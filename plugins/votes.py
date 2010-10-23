# coding: utf-8;

# vote.py
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

def getVoteText(conference):
	voteText = u"Голосование\nСоздатель: %(creator)s\n%(text)s\n" % (gVote[conference])
	items = [u" * %s" % (x[0]) for x in gVote[conference]["opinions"]]
	voteText += "\n".join(items)
	voteText += u"\nЧтобы проголосовать, напиши номер мнения, например \"мнение 1\""
	return voteText

def getVoteResults(conference):
	answers = [[x[1], x[0]] for x in gVote[conference]["opinions"]]
	answers.sort()
	answers.reverse()
	voteText = u"Результаты голосования\nСоздатель: %(creator)s\n%(text)s\n%%s" % (gVote[conference])
	items = [u" * %s (%d место и %d голосов)" % (x[1], i + 1, x[0]) for i, x in enumerate(answers)]
	return voteText % ("\n".join(items))

def saveVotes(conference):
	fileName = getConfigPath(conference, VOTES_FILE)
	utils.writeFile(fileName, str(gVote[conference]))

def vote(msgType, conference, nick, param):
	if(gVote[conference]):
		if(gVote[conference]["state"] == VOTE_FINISHED):
			sendMsg(msgType, conference, nick, u"голосование было завершено")
		elif(gVote[conference]["state"] == VOTE_CREATED):
			sendMsg(msgType, conference, nick, u"голосование ещё не запущено")
		else:
			trueJid = getTrueJid(conference, nick)
			if(not trueJid in gVote[conference]["voted"]):
				gVote[conference]["voted"][trueJid] = False
			if(not gVote[conference]["voted"][trueJid]):
				try:
					n = int(param) - 1
					gVote[conference]["opinions"][n][1] += 1
					gVote[conference]["voted"][trueJid] = True
					saveVotes(conference)
					sendMsg(msgType, conference, nick, u"поняла")
				except(IndexError, ValueError):
					sendMsg(msgType, conference, nick, u"нет такого пункта")
			else:
				sendMsg(msgType, conference, nick, u"2-ой раз голосовать не надо :P")
	else:
		sendMsg(msgType, conference, nick, u"сейчас нет никаких голосований")

def createNewVote(msgType, conference, nick, param):
	if param:
		if(gVote[conference] and gVote[conference]["state"] != VOTE_FINISHED):
			sendMsg(msgType, conference, nick, u"имеется неоконченное голосование")
		else:
			trueJid = getTrueJid(conference, nick)
			gVote[conference] = {"state": VOTE_CREATED, "creator": nick, "creatorjid": getTrueJid(conference, nick), "text": param, "voted": {}, "opinions": []}
			saveVotes(conference)
			sendMsg(msgType, conference, nick, u"Голосование создано! Чтобы добавить пункты напиши \"пункт+ твой_пункт\", удалить - \"пункт- номер пункта\". Начать голосование - команда \"голосование+\". Посмотреть текущие результаты - команда \"мнения\". Окончить голосование - команда \"итоги\"")
	else:
		if(gVote[conference]):
			if(gVote[conference]["state"] == VOTE_FINISHED):
				sendMsg(msgType, conference, nick, getVoteResults(conference))
			elif(gVote[conference]["state"] == VOTE_STARTED):
				sendMsg(msgType, conference, nick, getVoteText(conference))
			else:
				sendMsg(msgType, conference, nick, u"голование создано, но ещё не запущено")
		else:
			sendMsg(msgType, conference, nick, u"сейчас нет никаких голосований")

def startVote(msgType, conference, nick, parameters):
	if(gVote[conference]):
		if(gVote[conference]["state"] == VOTE_STARTED):
			sendMsg(msgType, conference, nick, u"голосование уже запущено")
		elif(gVote[conference]["state"] == VOTE_FINISHED):
			sendMsg(msgType, conference, nick, u"голосование было завершено")
		elif(not gVote[conference]["opinions"]):
			sendMsg(msgType, conference, nick, u"голосование не имеет пунктов")
		else:
			trueJid = getTrueJid(conference, nick)
			creatorJid = gVote[conference]["creatorjid"]
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				gVote[conference]["state"] = VOTE_STARTED
				saveVotes(conference)
				sendToConference(conference, getVoteText(conference))
			else:
				sendMsg(msgType, conference, nick, u"недостаточно прав")	  
	else:
		sendMsg(msgType, conference, nick, u"сейчас нет никаких голосований")

def stopVote(msgType, conference, nick, param):
	if(gVote[conference]):
		if(gVote[conference]["state"] == VOTE_FINISHED):
			sendMsg(msgType, conference, nick, u"неприменимо к оконченному голосованию")
		elif(gVote[conference]["state"] == VOTE_STARTED):
			trueJid = getTrueJid(conference, nick)
			creatorJid = gVote[conference]["creatorjid"]
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				gVote[conference]["state"] = VOTE_CREATED
				saveVotes(conference)
				sendMsg(msgType, conference, nick, u"голосование приостановлено")
			else:
				sendMsg(msgType, conference, nick, u"ага, щаззз")
		else:
			sendMsg(msgType, conference, nick, u"голосование уже приостановлено")
	else:
		sendMsg(msgType, conference, nick, u"сейчас нет никаких голосований")

def addOpinion(msgType, conference, nick, param):
	if(gVote[conference]):
		if(gVote[conference]["state"] == VOTE_STARTED):
			sendMsg(msgType, conference, nick, u"неприменимо к запущеному голосованию, останови и добавь пункты")
		elif(gVote[conference]["state"] == VOTE_FINISHED):
			sendMsg(msgType, conference, nick, u"неприменимо к оконченному голосованию")
		else:
			trueJid = getTrueJid(conference, nick)
			creatorJid = gVote[conference]["creatorjid"]
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				if(param in [x[0] for x in gVote[conference]["opinions"]]):
					sendMsg(msgType, conference, nick, u"уже есть такой пункт")
				else:
					gVote[conference]["opinions"].append([param, 0])
					saveVotes(conference)
					sendMsg(msgType, conference, nick, u"добавила")
			else:
				sendMsg(msgType, conference, nick, u"недостаточно прав")
	else:
		sendMsg(msgType, conference, nick, u"сейчас нет никаких голосований")

def delOpinion(msgType, conference, nick, param):
	if(gVote[conference]):
		if(gVote[conference]["state"] == VOTE_STARTED):
			sendMsg(msgType, conference, nick, u"неприменимо к запущеному голосованию, останови и добавь пункты")
		elif(gVote[conference]["state"] == VOTE_FINISHED):
			sendMsg(msgType, conference, nick, u"неприменимо к оконченному голосованию")
		else:
			trueJid = getTrueJid(conference, nick)
			creatorJid = gVote[conference]["creatorjid"]
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				try:
					n = int(param) - 1
					del(gVote[conference]["opinions"][n])
					saveVotes(conference)
					sendMsg(msgType, conference, nick, u"удалила")
				except(KeyError, IndexError):
					sendMsg(msgType, conference, nick, u"нет такого пункта")
			else:
				sendMsg(msgType, conference, nick, u"недостаточно прав")
	else:
		sendMsg(msgType, conference, nick, u"сейчас нет никаких голосований")

def showOpinions(msgType, conference, nick, param):
	if(gVote[conference]):
		if(gVote[conference]["state"] == VOTE_FINISHED):
			sendMsg(msgType, conference, nick, getVoteResults(conference))
		else:
			trueJid = getTrueJid(conference, nick)
			creatorJid = gVote[conference]["creatorjid"]
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				if(protocol.TYPE_PUBLIC == msgType):
					sendMsg(msgType, conference, nick, u"ушли в приват")
				sendMsg(protocol.TYPE_PRIVATE, conference, nick, getVoteResults(conference))
			else:
				sendMsg(msgType, conference, nick, u"жди окончания голосования :-p")
	else:
		sendMsg(msgType, conference, nick, u"сейчас нет никаких голосований")

def endVote(msgType, conference, nick, param):
	if(gVote[conference]):
		if(gVote[conference]["state"] == VOTE_FINISHED):
			sendMsg(msgType, conference, nick, u"голосование уже закончено, просмотр мнений - команда \"мнения\"")
		else:
			trueJid = getTrueJid(conference, nick)
			creatorJid = gVote[conference]["creatorjid"]
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				gVote[conference]["state"] = VOTE_FINISHED
				del(gVote[conference]["voted"])
				saveVotes(conference)
				sendToConference(conference, getVoteResults(conference))
			else:
				sendMsg(msgType, conference, nick, u"недостаточно прав")
	else:
		sendMsg(msgType, conference, nick, u"сейчас нет никаких голосований")

def showVote(conference, nick, trueJid, aff, role):
	if(gVote[conference]):
		if(gVote[conference]["state"] == VOTE_STARTED):
			if(not trueJid in gVote[conference]["voted"]):
				gVote[conference]["voted"][trueJid] = False
				saveVotes(conference)
				sendMsg(protocol.TYPE_PRIVATE, conference, nick, getVoteText(conference))

def loadVotes(conference):
	fileName = getConfigPath(conference, VOTES_FILE)
	utils.createFile(fileName, "{}")
	gVote[conference] = eval(utils.readFile(fileName))

registerJoinHandler(showVote)
registerEvent(loadVotes, ADDCONF)

registerCommand(vote, u"мнение", 10, 
				u"Для подачи мнения в текущем голосовании", 
				u"мнение <номер>", 
				(u"мнение 1", ), 
				CHAT | PARAM)
registerCommand(createNewVote, u"голосование", 11, 
				u"Создает новое голосование или показывает текущее (если имеется)", 
				u"голосование [текст]", 
				(u"голосование винды - сакс!", u"голосование"), 
				CHAT)
registerCommand(startVote, u"голосование+", 11, 
				u"Возобновляет голосование", 
				None, 
				(u"голосование+", ), 
				CHAT | NONPARAM)
registerCommand(stopVote, u"голосование-", 11, 
				u"Останавливает голосование, все данные сохраняются до продолжения голосования", 
				u"голосование-", 
				(u"голосование-"), 
				CHAT | NONPARAM)
registerCommand(addOpinion, u"пункт+", 11, 
				u"Добавляет пункт к текущему голосованию", 
				u"пункт+ <пункт>", 
				(u"пункт+ да", ), 
				CHAT | PARAM)
registerCommand(delOpinion, u"пункт-", 11, 
				u"Удаляет пункт из голосования. Пункт указывается его номером", 
				u"пункт- <номер_пункта>", 
				(u"пункт- 5", ), 
				CHAT | PARAM)
registerCommand(showOpinions, u"мнения", 11, 
				u"Отдаёт текущие результаты голосования в приват, не завершая голосования при этом", 
				None, 
				(u"мнения", ), 
				CHAT | NONPARAM)
registerCommand(endVote, u"итоги", 11, 
				u"Завершает голование и показывает его результаты", 
				None, 
				(u"итоги", ), 
				CHAT | NONPARAM)