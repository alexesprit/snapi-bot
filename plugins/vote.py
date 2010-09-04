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

VOTE_FILE = 'vote.txt';

gVotes = {};

def getVoteText(conference):
	voteText = u'Голосование\nСоздатель: %(creator)s\nВопрос: %(question)s\n' % (gVotes[conference]);
	items = [u' * %s' % (x[0]) for x in gVotes[conference]['opinions']]
	voteText += '\n'.join(items);
	voteText += u'\nЧтобы проголосовать, напиши номер мнения, например "мнение 1"';
	return(voteText);

def getResults(conference):
	answers = [[x[1], x[0]] for x in gVotes[conference]['opinions']];
	answers.sort();
	answers.reverse();
	voteText = u'Результаты голосования\nСоздатель: %(creator)s\nВопрос: %(question)s\n' % (gVotes[conference]);
	items = [u' * %d место и %d голосов - %s' % (i + 1, x[0], x[1]) for i, x in enumerate(answers)];
	return(voteText + '\n'.join(items));

def saveVotes(conference):
	fileName = getConfigPath(conference, VOTE_FILE);
	writeFile(fileName, str(gVotes[conference]));

def vote(msgType, conference, nick, param):
	if(gVotes[conference]):
		if(gVotes[conference]['finished']):
			sendMsg(msgType, conference, nick, u'голосование было завершено');
		elif(not gVotes[conference]['started']):
			sendMsg(msgType, conference, nick, u'голосование ещё не запущено');
		else:
			trueJid = getTrueJid(conference, nick);
			if(not trueJid in gVotes[conference]['voted']):
				gVotes[conference]['voted'][trueJid] = False;
			if(not gVotes[conference]['voted'][trueJid]):
				try:
					n = int(param) - 1;
					gVotes[conference]['opinions'][n][1] += 1;
					gVotes[conference]['voted'][trueJid] = True;
					saveVotes(conference);
					sendMsg(msgType, conference, nick, u'поняла');
				except(IndexError, ValueError):
					sendMsg(msgType, conference, nick, u'нет такого пункта');
			else:
				sendMsg(msgType, conference, nick, u'2-ой раз голосовать не надо :P');
	else:
		sendMsg(msgType, conference, nick, u'сейчас нет никаких голосований');

registerCommand(vote, u'мнение', 10, u'Для подачи мнения в текущем голосовании', u'мнение <номер>', (u'мнение 1', ), CHAT | PARAM);

def newVote(msgType, conference, nick, param):
	if(gVotes[conference]):
		if(not gVotes[conference]['finished']):
			sendMsg(msgType, conference, nick, getVoteText(conference));
		else:
			sendMsg(msgType, conference, nick, getResults(conference));	
	elif(param):
		trueJid = getTrueJid(conference, nick);
		gVotes[conference] = {'started': False, 'finished': False, 'creator': nick, 'creatorjid': getTrueJid(conference, nick), 'question': param, 'voted': {}, 'opinions': []};
		saveVotes(conference);
		sendMsg(msgType, conference, nick, u'Голосование создано! Чтобы добавить пункты напиши "пункт+ твой_пункт", удалить - "пункт- номер пункта". Начать голосование - команда "голосование+". Посмотреть текущие результаты - команда "мнения". Окончить голосование - команда "итоги"', True);

registerCommand(newVote, u'голосование', 11, u'Создает новое голосование или показывает текущее (если имеется)', u'голосование [текст]', (u'голосование винды - сакс!', u'голосование'), CHAT);

def startVote(msgType, conference, nick, parameters):
	if(gVotes[conference]):
		if(gVotes[conference]['started']):
			sendMsg(msgType, conference, nick, u'голосование уже запущено');
		elif(gVotes[conference]['finished']):
			sendMsg(msgType, conference, nick, u'голосование было завершено');
		elif(not gVotes[conference]['opinions']):
			sendMsg(msgType, conference, nick, u'голосование не имеет пунктов');
		else:
			trueJid = getTrueJid(conference, nick);
			creatorJid = gVotes[conference]['creatorjid'];			
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				gVotes[conference]['started'] = True;
				saveVotes(conference);
				sendToConference(conference, getVoteText(conference));
			else:
				sendMsg(msgType, conference, nick, u'недостаточно прав');			
	else:
		sendMsg(msgType, conference, nick, u'сейчас нет никаких голосований');

registerCommand(startVote, u'голосование+', 11, u'Возобновляет голосование', None, (u'голосование+', ), CHAT | NONPARAM);

def stopVote(msgType, conference, nick, param):
	if(gVotes[conference]):
		if(gVotes[conference]['finished']):
			sendMsg(msgType, conference, nick, u'неприменимо к оконченному голосованию');
		elif(gVotes[conference]['started']):
			trueJid = getTrueJid(conference, nick);
			creatorJid = gVotes[conference]['creatorjid'];			
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				gVotes[conference]['started'] = False;
				saveVotes(conference);
				sendMsg(msgType, conference, nick, u'голосование приостановлено');
			else:
				sendMsg(msgType, conference, nick, u'ага, щаззз');
		else:
			sendMsg(msgType, conference, nick, u'голосование уже приостановлено');
	else:
		sendMsg(msgType, conference, nick, u'сейчас нет никаких голосований');

registerCommand(stopVote, u'голосование-', 11, u'Останавливает голосование, все данные сохраняются до продолжения голосования', u'голосование-', (u'голосование-', ), CHAT | NONPARAM);

def addOpinion(msgType, conference, nick, param):
	if(gVotes[conference]):
		if(gVotes[conference]['started']):
			sendMsg(msgType, conference, nick, u'неприменимо к запущеному голосованию, останови и добавь пункты');
		elif(gVotes[conference]['finished']):
			sendMsg(msgType, conference, nick, u'неприменимо к оконченному голосованию');
		else:
			trueJid = getTrueJid(conference, nick);
			creatorJid = gVotes[conference]['creatorjid'];
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				if(param in [x[0] for x in gVotes[conference]['opinions']]):
					sendMsg(msgType, conference, nick, u'уже есть такой пункт');
				else:
					gVotes[conference]['opinions'].append([param, 0]);
					saveVotes(conference);
					sendMsg(msgType, conference, nick, u'добавила');
			else:
				sendMsg(msgType, conference, nick, u'недостаточно прав');
	else:
		sendMsg(msgType, conference, nick, u'сейчас нет никаких голосований');

registerCommand(addOpinion, u'пункт+', 11, u'Добавляет пункт к текущему голосованию', u'пункт+ <пункт>', (u'пункт+ да', ), CHAT | PARAM);
	
def delOpinion(msgType, conference, nick, param):
	if(gVotes[conference]):
		if(gVotes[conference]['started']):
			sendMsg(msgType, conference, nick, u'неприменимо к запущеному голосованию, останови и добавь пункты');
		elif(gVotes[conference]['finished']):
			sendMsg(msgType, conference, nick, u'неприменимо к оконченному голосованию');
		else:
			trueJid = getTrueJid(conference, nick);
			creatorJid = gVotes[conference]['creatorjid'];
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				try:
					n = int(param) - 1;
					del(gVotes[conference]['opinions'][n]);
					saveVotes(conference);
					sendMsg(msgType, conference, nick, u'удалила');
				except(KeyError, IndexError):
					sendMsg(msgType, conference, nick, u'нет такого пункта');
			else:
				sendMsg(msgType, conference, nick, u'недостаточно прав');
	else:
		sendMsg(msgType, conference, nick, u'сейчас нет никаких голосований');

registerCommand(delOpinion , u'пункт-', 11, u'Удаляет пункт из голосования. Пункт указывается его номером', u'пункт- <номер_пункта>', (u'пункт- 5', ), CHAT | PARAM);
	
def showOpinions(msgType, conference, nick, param):
	if(gVotes[conference]):
		trueJid = getTrueJid(conference, nick);
		creatorJid = gVotes[conference]['creatorjid'];
		if(gVotes[conference]['finished']):
			sendMsg(msgType, conference, nick, getResults(conference));
		elif(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
			if(PUBLIC == msgType):
				sendMsg(msgType, conference, nick, u'ушли в приват');
			sendMsg(PRIVATE, conference, nick, getResults(conference));
		else:
			sendMsg(msgType, conference, nick, u'жди окончания голосования :-p');
	else:
		sendMsg(msgType, conference, nick, u'сейчас нет никаких голосований');

registerCommand(showOpinions, u'мнения', 11, u'Отдаёт текущие результаты голосования в приват, не завершая голосования при этом', None, (u'мнения', ), CHAT | NONPARAM);

def endVote(msgType, conference, nick, param):
	if(gVotes[conference]):
		if(gVotes[conference]['finished']):
			sendMsg(msgType, conference, nick, getResults(conference));
		else:
			trueJid = getTrueJid(conference, nick);
			creatorJid = gVotes[conference]['creatorjid'];
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				gVotes[conference]['started'] = False;
				gVotes[conference]['finished'] = True;
				del(gVotes[conference]['voted']);
				saveVotes(conference);
				sendToConference(conference, getResults(conference));
			else:
				sendMsg(msgType, conference, nick, u'недостаточно прав');
	else:
		sendMsg(msgType, conference, nick, u'сейчас нет никаких голосований');

registerCommand(endVote, u'итоги', 11, u'Завершает голование и показывает его результаты', None, (u'итоги', ), CHAT | NONPARAM);

def showVote(conference, nick, trueJid, aff, role):
	if(gVotes[conference]):
		if(gVotes[conference]['started']):
			if(not trueJid in gVotes[conference]['voted']):
				gVotes[conference]['voted'][trueJid] = False;
				saveVotes(conference);
				sendMsg(PRIVATE, conference, nick, getVoteText(conference));

registerJoinHandler(showVote);

def loadVotes(conference):
	fileName = getConfigPath(conference, VOTE_FILE);
	createFile(fileName, '{}');
	gVotes[conference] = eval(readFile(fileName));

registerEvent(loadVotes, ADDCONF);

def unloadVotes(conference):
	del(gVotes[conference]);

registerEvent(unloadVotes, DELCONF);
