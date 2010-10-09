# coding: utf-8

# votes.py
# Initial Copyright (c) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

VOTES_FILE = "votes.txt"

gVotes = {}

VOTE_STARTED = 0x1
VOTE_FINISHED = 0x2

VOTE_TEXT = 0x0
VOTE_STATE = 0x1
VOTE_VOTED = 0x2
VOTE_CREATOR = 0x3
VOTE_OPINIONS = 0x4

VOTE_OPINIONS = 0x1
VOTE_FIRSTONLY = 0x2
VOTE_SCORES = 0x4

voteTemplate = u"голосование создано! Чтобы показать его, напишите \"голосование %d\". \
Чтобы проголосовать напишите \"мнение %d <номер_мнения>\". \
Закончить голосование - \"итоги %d\""

def getFreeID(base):
	id = 1
	while(True):
		if(id not in base):
			return(id)
		id += 1

def createOpinions(opinions):
	opinionPoints = []
	for opinion in opinions:
		opinionPoints.append([0, opinion])
	return(opinionPoints)

def getOpinionScores(vote):
	scores = 0
	for opinion in vote[VOTE_OPINIONS]:
		scores += opinion[0]
	return(scores)

def getVoteText(vote, flags=0x0):
	voteText = vote[VOTE_TEXT]
	if(flags & VOTE_OPINIONS):
		if(flags & VOTE_SCORES):
			voteOpinions = sorted(vote[VOTE_OPINIONS])
			voteOpinions.reverse()
		else:
			voteOpinions = vote[VOTE_OPINIONS]
		if(flags & VOTE_FIRSTONLY):
			voteOpinions = voteOpinions[:1]
		for opinion in voteOpinions:
			scores, text = opinion
			if(flags & VOTE_SCORES):
				voteText += u"\n * %s (%s голосов)" % (text, scores)
			else:
				voteText += u"\n * %s" % (text)
	return(voteText)

def showVotes(msgType, conference, nick, param):
	if(param and param.isdigit()):
		voteID = int(param)
		try:
			vote = gVotes[conference][voteID]
		except(KeyError):
			sendMsg(msgType, conference, nick, u"такого голосования нет!")
			return
		sendMsg(msgType, conference, nick, getVoteText(vote, VOTE_OPINIONS))
	elif(not param):
		if(not gVotes[conference].isEmpty()):
			voteText = u"Текущие голосования:\n"
			for i, vote in enumerate(gVotes[conference]):
				vote = gVotes[conference][vote]
				voteText += u"%d) %s" % (i + 1, getVoteText(vote))
				if(vote[VOTE_STATE] == VOTE_STARTED):
					voteText += u"\nНе завершено, голосов: %d\n\n" \
								% (getOpinionScores(vote))
				else:
					voteText += u"\nЗавершено, голосов: %d\n\n" \
								% (getOpinionScores(vote))
			voteText += u"подробнее - \"голосование <номер>\", например: \"голосование 1\""
			sendMsg(msgType, conference, nick, voteText)
		else:
			sendMsg(msgType, conference, nick, u"голосований нет");	

def createVote(msgType, conference, nick, param):
	rawData = param.split("\n")
	if(len(rawData) > 1):
		text, opinions = rawData[0], rawData[1:]
		vote = {}
		vote[VOTE_TEXT] = text
		vote[VOTE_STATE] = VOTE_STARTED
		vote[VOTE_VOTED] = []
		vote[VOTE_CREATOR] = [nick, getTrueJid(conference, nick)]
		vote[VOTE_OPINIONS] = createOpinions(opinions)
		voteID = getFreeID(gVotes[conference])
		gVotes[conference][voteID] = vote
		gVotes[conference].save()
		sendMsg(msgType, conference, nick, voteTemplate % (voteID, voteID, voteID))
	else:
		sendMsg(msgType, conference, nick, u"читай справку по команде")

def deleteVote(msgType, conference, nick, param):
	if(param.isdigit()):
		try:
			voteID = int(param)
			vote = gVotes[conference][voteID]
			trueJid = getTrueJid(conference, nick)
			creatorJid = vote[VOTE_CREATOR][1]
			userAccess = getAccess(conference, trueJid)
			if(trueJid == creatorJid or userAccess >= 20):
				del(gVotes[conference][voteID])
				gVotes[conference].save()
				sendMsg(msgType, conference, nick, u"удалила")
			else:
				sendMsg(msgType, conference, nick, u"недостаточно прав")
		except(IndexError):
			sendMsg(msgType, conference, nick, u"такого голосования нет!")
	elif(param == u"все"):
		trueJid = getTrueJid(conference, nick)
		userAccess = getAccess(conference, trueJid)
		if(userAccess >= 30):		
			gVotes[conference].clear()
			gVotes[conference].save()
			sendMsg(msgType, conference, nick, u"удалила")
		else:
			sendMsg(msgType, conference, nick, u"недостаточно прав")
			
def showOpinions(msgType, conference, nick, param):
	if(not gVotes[conference].isEmpty()):
		if(param and param.isdigit()):
			voteID = int(param)
			try:
				vote = gVotes[conference][voteID]
				votes = [vote]
				flags = VOTE_OPINIONS | VOTE_SCORES
			except(KeyError):
				sendMsg(msgType, conference, nick, u"такого голосования нет!")
				return
		else:
			votes = [gVotes[conference][i] for i in gVotes[conference]]
			flags = VOTE_OPINIONS | VOTE_FIRSTONLY | VOTE_SCORES
		voteText = []
		userJid = getTrueJid(conference, nick)
		for i, vote in enumerate(votes):
			creatorJid = vote[VOTE_CREATOR][1]
			voteState = vote[VOTE_STATE]
			if(creatorJid == userJid or voteState == VOTE_FINISHED):
				voteText.append(u"%d) %s" % (i + 1, getVoteText(vote, flags)))
			else:
				voteText.append(u"%d) %s\nРезультаты недоступны" % (i + 1, getVoteText(vote)))
		if(xmpp.TYPE_PUBLIC == msgType):
			sendMsg(msgType, conference, nick, u"ушли в приват")
		sendMsg(xmpp.TYPE_PRIVATE, conference, nick, u"Результаты голосований:\n%s" % ("\n\n".join(voteText)))
	else:
		sendMsg(msgType, conference, nick, u"голосований нет")

def vote(msgType, conference, nick, param):
	param = param.split()
	if(len(param) == 2):
		try:
			voteID = int(param[0])
			opinionNum = int(param[1]) - 1
			trueJid = getTrueJid(conference, nick)
			vote = gVotes[conference][voteID]
			if(trueJid not in vote[VOTE_VOTED]):
				opinion = vote[VOTE_OPINIONS][opinionNum]
				opinion[0] += 1
				vote[VOTE_VOTED].append(trueJid)
				gVotes[conference].save()
				sendMsg(msgType, conference, nick, u"поняла")
			else:
				sendMsg(msgType, conference, nick, u"ты и так уже голосовал :-P")
		except(KeyError, IndexError, ValueError):
			sendMsg(msgType, conference, nick, u"читай справку по команде")

def endVote(msgType, conference, nick, param):
	if(not gVotes[conference].isEmpty()):
		if(param and param.isdigit()):
			voteID = int(param)
			try:
				vote = gVotes[conference][voteID]
				if(VOTE_FINISHED != vote[VOTE_STATE]):
					trueJid = getTrueJid(conference, nick)
					creatorJid = vote[VOTE_CREATOR][1]
					userAccess = getAccess(conference, trueJid)
					if(trueJid == creatorJid or userAccess >= 20):
						vote[VOTE_STATE] = VOTE_FINISHED
						del(vote[VOTE_VOTED])
						gVotes[conference].save()

						flags = VOTE_OPINIONS | VOTE_SCORES
						message = u"Результаты:\n%s" % (getVoteText(vote, flags))
						sendMsg(msgType, conference, nick, message)
					else:
						sendMsg(msgType, conference, nick, u"недостаточно прав")
				else:
					showOpinions(msgType, conference, nick, param);		
			except(KeyError):
				sendMsg(msgType, conference, nick, u"такого голосования нет!")
				return
		else:
			showOpinions(msgType, conference, nick, None)
	else:
		sendMsg(msgType, conference, nick, u"голосований нет")

def sendNewVotes(conference, nick, trueJid, role, aff):
	for voteID in gVotes[conference]:
		vote = gVotes[conference][voteID]
		if(vote[VOTE_STATE] != VOTE_FINISHED):
			if(trueJid not in vote[VOTE_VOTED]):
				voteText = u"Голосование\n%s" % (getVoteText(vote, VOTE_OPINIONS))
				voteText += u"\nЧтобы проголосовать напишите \"мнение %d <номер_мнения>\"" % (voteID)
				sendMsg(xmpp.TYPE_PRIVATE, conference, nick, voteText)

def loadVotes(conference):
	fileName = getConfigPath(conference, VOTES_FILE)
	gVotes[conference] = database.DataBase(fileName)

registerEvent(loadVotes, ADDCONF)
registerJoinHandler(sendNewVotes)

registerCommand(createVote, u"голосование+", 
				11, u"Создаёт новое голосование", 
				u"голосование+ <текст>\n<пункт>\n<пункт>\n...", 
				(u"голосование винды - сакс!\nда\nнет!!"), 
				CHAT | PARAM)
registerCommand(deleteVote, u"голосование-", 11, 
				u"Удаляет голосование", 
				u"голосование- <номер>", 
				(u"голосование- 5", ), 
				CHAT | PARAM)
registerCommand(showVotes, u"голосования", 11, 
				u"Показывает все голосования или какое-либо одно", 
				u"голосование [номер]", 
				(u"голосование", u"голосование 4"), 
				CHAT)
registerCommand(vote, u"мнение", 11, 
				u"Для подачи мнения в голосовании", 
				u"мнение <номер_голосования> <номер_пункта>", 
				(u"мнение 2 4", ), 
				CHAT | PARAM)
registerCommand(showOpinions, u"мнения", 11, 
				u"Отдаёт текущие результаты голосования в приват, не завершая голосования при этом", 
				u"мнения [номер]", 
				(u"мнения", u"мнения 5"), 
				CHAT)
registerCommand(endVote, u"итоги", 11, 
				u"Завершает голосование и выдает результаты", 
				u"итоги [номер]",
				(u"итоги", u"итоги 5"), 
				CHAT)