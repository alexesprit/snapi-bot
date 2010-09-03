# coding: utf-8;

# quiz.py
# Initial Copyright (c) Gigabyte
# Modification Copyright (c) -Esprit-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

QUIZ_FILE = 'questions.txt';
QUIZ_SCORES_FILE = 'quiz.txt';

QUIZ_TOTAL_LINES = sum(1 for i in open(getFilePath(RESOURCE_DIR, QUIZ_FILE), 'r'));
QUIZ_TIME_LIMIT = 180;
QUIZ_IDLE_LIMIT = 3;
QUIZ_COEF = 3;

gQuizScores = {};

gQuizAnswer = {};
gQuizQuestion = {};
gQuizHint = {};

gQuizTimer = {};
gQuizAskTime = {};
gQuizIdleCount = {};

def idleCheck(conference):
	sendToConference(conference, u'(!) Время вышло! Правильный ответ: %s' % (gQuizAnswer[conference]));
	gQuizIdleCount[conference] += 1;
	if(gQuizIdleCount[conference] == QUIZ_IDLE_LIMIT):
		sendToConference(conference, u'(!) Викторина автоматичеки заверщена по бездействию!');
		quizStop();
	else:
		askNewQuestion(conference);

def getHintString(answer):
	return(['*'] * len(answer));

def isTimerEnabled(conference):
	return(conference in gQuizTimer and gQuizTimer[conference]);
	
def resetQuizTimer(conference):
	if(isTimerEnabled(conference)):
		gQuizTimer[conference].cancel();
	gInfo['tmr'] += 1;
	gQuizTimer[conference] = startTimer(QUIZ_TIME_LIMIT, idleCheck, (conference, ));

def getNewQuestion():
	questionNum = random.randrange(0, QUIZ_TOTAL_LINES);
	fp = file(QUIZ_FILE);
	for i in xrange(QUIZ_TOTAL_LINES):
		if(i == questionNum):
			(question, answer) = fp.readline().decode('utf-8').strip().split('|', 1);
			fp.close();
			return(question, answer);
		else:
			fp.readline();

def askNewQuestion(conference, lastAnswer = None):
	question, answer = getNewQuestion();
	gQuizAnswer[conference] = answer;
	gQuizQuestion[conference] = question;
	gQuizHint[conference] = getHintString(answer);
	gQuizIdleCount[conference] = 0;
	gQuizAskTime[conference] = time.time();
	resetQuizTimer(conference);
	if(lastAnswer):
		sendToConference(conference, u'(!) Правильный ответ: %s, cмена вопроса:\n%s' % (lastAnswer, question));
	else:
		sendToConference(conference, u'(?) Внимание вопрос:\n%s' % (question));

def quizStop(conference):
	del(gQuizAnswer[conference]);
	del(gQuizQuestion[conference]);
	del(gQuizHint[conference]);
	del(gQuizIdleCount[conference]);
	del(gQuizAskTime[conference]);
	if(isTimerEnabled(conference)):
		gQuizTimer[conference].cancel();
		del(gQuizTimer[conference]);
	gQuizScores[conference].save();
	showScoreList(PUBLIC, conference);

def checkAnswer(conference, nick, trueJid, answer):
	rightAnswer = gQuizAnswer[conference].lower();
	userAnswer = answer.lower();
	if(rightAnswer == userAnswer):	
		answerTime = time.time() - gQuizAskTime[conference];
		wLength = len(gQuizHint[conference]);
		closedLetters = gQuizHint[conference].count('*');
		points = int(wLength * closedLetters * (QUIZ_COEF / answerTime));
		if(points):
			sendToConference(conference, u'(!) %s, поздравляю! +%d в банк! Верный ответ: %s' % (nick, points, rightAnswer));
		else:
			sendToConference(conference, u'(!) %s, поздравляю! Верный ответ: %s' % (nick, rightAnswer));
		base = gQuizScores[conference];
		scores = base.getKey(trueJid);
		if(scores):
			scores[0] = nick;
			scores[1] += points;
			scores[2] += 1;
		else:
			scores = [nick, points, 1];
		base.setKey(trueJid, scores);
		askNewQuestion(conference);

def answerListener(stanza, msgType, conference, nick, trueJid, text):
	if(conference in gQuizAnswer):
		checkAnswer(conference, nick, trueJid, text);

def showScoreList(msgType, conference, nick = None):
	base = gQuizScores[conference];
	if(not base.isEmpty()):
		scores = [];
		for jid in base.items():
			item = base.getKey(jid);
			scores.append([item[1], item[2], item[0]]);
		scores.sort();
		scores.reverse();
		scores = scores[:10];
		items = [u'%s) %s, %s, %s' % (i + 1, x[2], x[0], x[1]) for i, x in enumerate(scores)];
		if(nick):
			message = u'статистика по игре:\nНик, счет, ответов\n';
			sendMsg(msgType, conference, nick, message + '\n'.join(items));
		else:
			message = u'(*) Счёт:\nНик, счет, ответов\n';
			sendToConference(conference, message + '\n'.join(items));
	else:
		sendMsg(msgType, conference, nick, u'cтатистика по игре отсутствует');

def startQuiz(msgType, conference, nick, param):
	if(conference in gQuizAnswer):
		sendMsg(msgType, conference, nick, u'Викторина уже существует!');
	else:
		askNewQuestion(conference);

def stopQuiz(msgType, conference, nick, param):
	if(conference in gQuizAnswer):
		sendToConference(conference, u'(!) Викторина остановлена');
		quizStop(conference);

def askQuestion(msgType, conference, nick, param):
	if(conference in gQuizAnswer):
		askNewQuestion(conference, gQuizAnswer[conference]);

def showHint(msgType, conference, nick, param):
	if(conference in gQuizAnswer):
		answer = gQuizAnswer[conference];
		hint = gQuizHint[conference];
		hiddenLetters = '';
		for i in range(0, len(answer)):
			if(hint[i] == '*'):
				hiddenLetters += answer[i];
		randLetter = random.choice(hiddenLetters);
		for i in range(0, len(answer)):
			if(answer[i] == randLetter):
				hint[i] = randLetter;
		if(hint.count('*')):
			gQuizHint[conference] = hint;
			sendToConference(conference, u'(*) Подсказка: %s' % (''.join(hint)));
			gQuizIdleCount[conference] = 0;
			resetQuizTimer(conference);
		else:
			askNewQuestion(conference, answer);

def showScores(msgType, conference, nick, param):
	showScoreList(msgType, conference, nick);

def showQuestion(msgType, conference, nick, param):
	if(conference in gQuizAnswer):
		sendMsg(msgType, conference, nick, u'(*) Текущий вопрос: \n' + gQuizQuestion[conference]);
		
def loadQuizScores(conference):
	fileName = getConfigPath(conference, QUIZ_SCORES_FILE);
	gQuizScores[conference] = database.DataBase(fileName);

registerEvent(loadQuizScores, ADDCONF);

def unloadQuizScores(conference):
	del(gQuizScores[conference]);

registerEvent(unloadQuizScores, DELCONF);

registerMessageHandler(answerListener, CHAT);
registerCommand(startQuiz, u'старт', 10, u'Запуск игры', None, (u'старт', ), CHAT | NONPARAM);
registerCommand(stopQuiz, u'стоп', 10, u'Остановка игры', None, (u'стоп', ), CHAT | NONPARAM);
registerCommand(showScores, u'счет', 10, u'Показывает счёт игры', None, (u'счет', ), CHAT | NONPARAM);
registerCommand(showHint, u'х', 10, u'Показать подсказку', None, (u'х', ), CHAT | NONPARAM);
registerCommand(showQuestion, u'повтор', 10, u'Повтор текущего вопроса', None, (u'повтор', ), CHAT | NONPARAM);
registerCommand(askQuestion, u'сл', 10, u'Следущий вопрос', None, (u'сл', ), CHAT | NONPARAM);
