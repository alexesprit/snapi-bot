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

VOTES_FILE = 'config/%s/vote.txt';

gVoteCache = {};

def getVoteText(conference):
	voteText = u'Результаты голосования\nСоздатель: %(creator)s\nВопрос: %(question)s\n' % (gVoteCache[conference]);
	items = [u' * %s' % (x[0]) for x in gVoteCache[conference]['opinions']]
	voteText += '\n'.join(items);
	voteText += u'\nЧтобы проголосовать, напиши номер мнения, например "мнение 1"';
	return(voteText);

def getResults(conference):
	answers = [[x[1], x[0]] for x in gVoteCache[conference]['opinions']];
	answers.sort();
	answers.reverse();
	voteText = u'Результаты голосования\nСоздатель: %(creator)s\nВопрос: %(question)s\n' % (gVoteCache[conference]);
	items = [u' * %d место и %d голосов - %s' % (i + 1, x[0], x[1]) for i, x in enumerate(answers)];
	return(voteText + '\n'.join(items));

def saveVotes(conference):
	fileName = VOTES_FILE % (conference);
	writeFile(fileName, str(gVoteCache[conference]));

def vote(type, conference, nick, param):
	if(gVoteCache[conference]):
		if(gVoteCache[conference]['finished']):
			sendMsg(type, conference, nick, u'голосование было завершено');
		elif(not gVoteCache[conference]['started']):
			sendMsg(type, conference, nick, u'голосование ещё не запущено');
		else:
			trueJid = getTrueJid(conference, nick);
			if(not trueJid in gVoteCache[conference]['voted']):
				gVoteCache[conference]['voted'][trueJid] = False;
			if(not gVoteCache[conference]['voted'][trueJid]):
				try:
					n = int(param) - 1;
					gVoteCache[conference]['opinions'][n][1] += 1;
					gVoteCache[conference]['voted'][trueJid] = True;
					saveVotes(conference);
					sendMsg(type, conference, nick, u'поняла');
				except(IndexError, ValueError):
					sendMsg(type, conference, nick, u'нет такого пункта');
			else:
				sendMsg(type, conference, nick, u'2-ой раз голосовать не надо :P');
	else:
		sendMsg(type, conference, nick, u'сейчас нет никаких голосований');

registerCommand(vote, u'мнение', 10, u'Для подачи мнения в текущем голосовании', u'мнение <номер>', (u'мнение 1', ), CHAT | PARAM);

def newVote(type, conference, nick, param):
	if(gVoteCache[conference]):
		if(not gVoteCache[conference]['finished']):
			sendMsg(type, conference, nick, getVoteText(conference));
		else:
			sendMsg(type, conference, nick, getResults(conference));	
	elif(param):
		trueJid = getTrueJid(conference, nick);
		gVoteCache[conference] = {'started': False, 'finished': False, 'creator': nick, 'creatorjid': getTrueJid(conference, nick), 'question': param, 'voted': {}, 'opinions': []};
		saveVotes(conference);
		sendMsg(type, conference, nick, u'Голосование создано! Чтобы добавить пункты напиши "пункт+ твой_пункт", удалить - "пункт- номер пункта". Начать голосование - команда "голосование+". Посмотреть текущие результаты - команда "мнения". Окончить голосование - команда "итоги"', True);

registerCommand(newVote, u'голосование', 11, u'Создает новое голосование или показывает текущее (если имеется)', u'голосование [текст]', (u'голосование винды - сакс!', u'голосование'), CHAT);

def startVote(type, conference, nick, parameters):
	if(gVoteCache[conference]):
		if(gVoteCache[conference]['started']):
			sendMsg(type, conference, nick, u'голосование уже запущено');
		elif(gVoteCache[conference]['finished']):
			sendMsg(type, conference, nick, u'голосование было завершено');
		elif(not gVoteCache[conference]['opinions']):
			sendMsg(type, conference, nick, u'голосование не имеет пунктов');
		else:
			trueJid = getTrueJid(conference, nick);
			creatorJid = gVoteCache[conference]['creatorjid'];			
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				gVoteCache[conference]['started'] = True;
				saveVotes(conference);
				sendToConference(conference, getVoteText(conference));
			else:
				sendMsg(type, conference, nick, u'недостаточно прав');			
	else:
		sendMsg(type, conference, nick, u'сейчас нет никаких голосований');

registerCommand(startVote, u'голосование+', 11, u'Возобновляет голосование', None, (u'голосование+', ), CHAT | NONPARAM);

def stopVote(type, conference, nick, param):
	if(gVoteCache[conference]):
		if(gVoteCache[conference]['finished']):
			sendMsg(type, conference, nick, u'неприменимо к оконченному голосованию');
		elif(gVoteCache[conference]['started']):
			trueJid = getTrueJid(conference, nick);
			creatorJid = gVoteCache[conference]['creatorjid'];			
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				gVoteCache[conference]['started'] = False;
				saveVotes(conference);
				sendMsg(type, conference, nick, u'голосование приостановлено');
			else:
				sendMsg(type, conference, nick, u'ага, щаззз');
		else:
			sendMsg(type, conference, nick, u'голосование уже приостановлено');
	else:
		sendMsg(type, conference, nick, u'сейчас нет никаких голосований');

registerCommand(stopVote, u'голосование-', 11, u'Останавливает голосование, все данные сохраняются до продолжения голосования', u'голосование-', (u'голосование-'), CHAT | NONPARAM);

def addOpinion(type, conference, nick, param):
	if(gVoteCache[conference]):
		if(gVoteCache[conference]['started']):
			sendMsg(type, conference, nick, u'неприменимо к запущеному голосованию, останови и добавь пункты');
		elif(gVoteCache[conference]['finished']):
			sendMsg(type, conference, nick, u'неприменимо к оконченному голосованию');
		else:
			trueJid = getTrueJid(conference, nick);
			creatorJid = gVoteCache[conference]['creatorjid'];
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				if(param in [x[0] for x in gVoteCache[conference]['opinions']]):
					sendMsg(type, conference, nick, u'уже есть такой пункт');
				else:
					gVoteCache[conference]['opinions'].append([param, 0]);
					saveVotes(conference);
					sendMsg(type, conference, nick, u'добавила');
			else:
				sendMsg(type, conference, nick, u'недостаточно прав');
	else:
		sendMsg(type, conference, nick, u'сейчас нет никаких голосований');

registerCommand(addOpinion, u'пункт+', 11, u'Добавляет пункт к текущему голосованию', u'пункт+ <пункт>', (u'пункт+ да', ), CHAT | PARAM);
	
def delOpinion(type, conference, nick, param):
	if(gVoteCache[conference]):
		if(gVoteCache[conference]['started']):
			sendMsg(type, conference, nick, u'неприменимо к запущеному голосованию, останови и добавь пункты');
		elif(gVoteCache[conference]['finished']):
			sendMsg(type, conference, nick, u'неприменимо к оконченному голосованию');
		else:
			trueJid = getTrueJid(conference, nick);
			creatorJid = gVoteCache[conference]['creatorjid'];
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				try:
					n = int(param) - 1;
					del(gVoteCache[conference]['opinions'][n]);
					saveVotes(conference);
					sendMsg(type, conference, nick, u'удалила');
				except(KeyError, IndexError):
					sendMsg(type, conference, nick, u'нет такого пункта');
			else:
				sendMsg(type, conference, nick, u'недостаточно прав');
	else:
		sendMsg(type, conference, nick, u'сейчас нет никаких голосований');

registerCommand(delOpinion , u'пункт-', 11, u'Удаляет пункт из голосования. Пункт указывается его номером', u'пункт- <номер_пункта>', (u'пункт- 5', ), CHAT | PARAM);
	
def showOpinions(type, conference, nick, param):
	if(gVoteCache[conference]):
		trueJid = getTrueJid(conference, nick);
		creatorJid = gVoteCache[conference]['creatorjid'];
		if(gVoteCache[conference]['finished']):
			sendMsg(type, conference, nick, getResults(conference));
		elif(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
			if(PUBLIC == type):
				sendMsg(type, conference, nick, u'ушли в приват');
			sendMsg(PRIVATE, conference, nick, getResults(conference));
		else:
			sendMsg(type, conference, nick, u'жди окончания голосования :-p');
	else:
		sendMsg(type, conference, nick, u'сейчас нет никаких голосований');

registerCommand(showOpinions, u'мнения', 11, u'Отдаёт текущие результаты голосования в приват, не завершая голосования при этом', None, (u'мнения', ), CHAT | NONPARAM);

def endVote(type, conference, nick, param):
	if(gVoteCache[conference]):
		if(gVoteCache[conference]['finished']):
			sendMsg(type, conference, nick, u'голосование уже закончено');
		else:
			trueJid = getTrueJid(conference, nick);
			creatorJid = gVoteCache[conference]['creatorjid'];
			if(creatorJid == trueJid or getAccess(conference, trueJid) >= 20):
				gVoteCache[conference]['started'] = False;
				gVoteCache[conference]['finished'] = True;
				del(gVoteCache[conference]['voted']);
				saveVotes(conference);
				sendToConference(conference, getResults(conference));
			else:
				sendMsg(type, conference, nick, u'недостаточно прав');
	else:
		sendMsg(type, conference, nick, u'сейчас нет никаких голосований');

registerCommand(endVote, u'итоги', 11, u'Завершает голование и показывает его результаты', None, (u'итоги', ), CHAT | NONPARAM);

def showVote(conference, nick, trueJid, aff, role):
	if(gVoteCache[conference]):
		if(gVoteCache[conference]['started']):
			if(not trueJid in gVoteCache[conference]['voted']):
				gVoteCache[conference]['voted'][trueJid] = False;
				saveVotes(conference);
				sendMsg(PRIVATE, conference, nick, getVoteText(conference));

registerJoinHandler(showVote);

def loadVotes(conference):
	fileName = VOTES_FILE % (conference);
	createFile(fileName, '{}');
	gVoteCache[conference] = eval(readFile(fileName));

registerEvent(loadVotes, ADDCONF);
