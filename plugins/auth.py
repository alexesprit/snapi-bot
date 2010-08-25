# coding: utf-8;

# auth.py
# Initial Copyright (c) ???
# Modification Copyright (с) 2010 -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

AA = {'question': u'сорок + семь', 'answer': '47'};
AB = {'question': u'60 + четыре', 'answer': '64'};
AC = {'question': u'тридцать + 2', 'answer': '32'};
AD = {'question': u'7 + девять', 'answer': '16'};
AE = {'question': u'2 + шесть', 'answer': '8'};
AF = {'question': u'2 + два', 'answer': '4'};
AG = {'question': u'один + один', 'answer': '2'};

CFG_AUTH = 'auth';

gAuthAnswer = {};

def askAuthQuestion(conference, nick, trueJid, afl, role):
	if(getConfigKey(conference, 'auth')):
		if(afl == 'none'):
			question = random.choice((AA, AB, AC, AD, AE, AF, AG, ));
			setRole(conference, nick, 'visitor', u'неавторизованый участник');
			message = u'Чтобы получить голос, реши пример: %(question)s. Как решишь, напиши мне ответ' % (question);
			sendMsg(PRIVATE, conference, nick, message);
			gAuthAnswer[conference][trueJid] = question['answer'];

registerJoinHandler(askAuthQuestion);

def clearAuthCache(conference, nick, trueJid, reason, code):
	if(trueJid in gAuthAnswer[conference]):
		del(gAuthAnswer[conference][trueJid]);

registerLeaveHandler(clearAuthCache);

def authAnswerListener(stanza, type, conference, nick, trueJid, body):
	if(PRIVATE == type):
		if(trueJid in gAuthAnswer[conference]):
			if(gAuthAnswer[conference][trueJid] == body):
				sendMsg(type, conference, nick, u'ок, признаю - ты не бот =)');
				setRole(conference, nick, 'participant', u'авторизация пройдена');
				del(gAuthAnswer[conference][trueJid]);
			else:
				sendMsg(type, conference, nick, u'неправильный ответ. подумай или заюзай гугл');

registerMessageHandler(authAnswerListener, CHAT);

def authControl(type, conference, nick, param):
	if(param):
		if(param.isdigit()):
			param = int(param);
			if(param == 1):
				setConfigKey(conference, CFG_AUTH, 1);
				sendMsg(type, conference, nick, u'авторизация включена');
			else:
				setConfigKey(conference, CFG_AUTH, 0);
				sendMsg(type, conference, nick, u'авторизация отключена');
			saveChatConfig(conference);
		else:
			sendMsg(type, conference, nick, u'прочитай помощь по команде');
	else:
		sendMsg(type, conference, nick, u'текущее значение: %d' % (getConfigKey(conference, CFG_AUTH)));

registerCommand(authControl, u'авторизация', 30, u'Отключает (0) или включает (1) проверку вошедшего пользователя на человечность. Без параметра покажет текущее значение', u'авторизация [0/1]', (u'авторизация', u'авторизация 0'), CHAT);

def setAuthState(conference):
	gAuthAnswer[conference] = {};
	if(getConfigKey(conference, CFG_AUTH) is None):
		setConfigKey(conference, CFG_AUTH, 0);

registerEvent(setAuthState, ADDCONF);
