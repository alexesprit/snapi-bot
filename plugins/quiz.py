# coding: utf-8

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

QUIZ_FILE = "questions.txt"
QUIZ_SCORES_FILE = "quiz.txt"

QUIZ_TOTAL_LINES = sum(1 for i in open(getFilePath(RESOURCE_DIR, QUIZ_FILE), "r"))
QUIZ_TIME_LIMIT = 180
QUIZ_IDLE_LIMIT = 3
QUIZ_COEF = 3

gQuizScores = {}

gQuizEnable = {}
gQuizAnswer = {}
gQuizQuestion = {}
gQuizHint = {}

gQuizTimer = {}
gQuizAskTime = {}
gQuizIdleCount = {}

def checkQuizIdle(conference):
	sendToConference(conference, u"(!) Время вышло! Правильный ответ: %s" % (gQuizAnswer[conference]))
	gQuizIdleCount[conference] += 1
	if gQuizIdleCount[conference] == QUIZ_IDLE_LIMIT:
		sendToConference(conference, u"(!) Викторина автоматичеки заверщена по бездействию!")
		quizStop(conference, False)
	else:
		askQuizQuestion(conference, resetIdle=False)

def getQuizHint(answer):
	return ["*"] * len(answer)

def isQuizTimerEnabled(conference):
	return conference in gQuizTimer and gQuizTimer[conference]
	
def resetQuizTimer(conference):
	if isQuizTimerEnabled(conference):
		gQuizTimer[conference].cancel()
	gQuizTimer[conference] = startTimer(QUIZ_TIME_LIMIT, checkQuizIdle, (conference, ))

def getQuizQuestion():
	questionNum = random.randrange(0, QUIZ_TOTAL_LINES)
	fp = file(getFilePath(RESOURCE_DIR, QUIZ_FILE))
	for i in xrange(QUIZ_TOTAL_LINES):
		if i == questionNum:
			(question, answer) = fp.readline().decode("utf-8").strip().split("|", 1)
			fp.close()
			return question, answer
		else:
			fp.readline()

def askQuizQuestion(conference, lastAnswer=None, resetIdle=True):
	question, answer = getQuizQuestion()
	gQuizAnswer[conference] = answer
	gQuizQuestion[conference] = question
	gQuizHint[conference] = getQuizHint(answer)
	if resetIdle:
		gQuizIdleCount[conference] = 0
	gQuizAskTime[conference] = time.time()
	resetQuizTimer(conference)
	gQuizEnable[conference] = True
	if lastAnswer:
		sendToConference(conference, u"(!) Правильный ответ: %s, cмена вопроса:\n%s" % (lastAnswer, question))
	else:
		sendToConference(conference, u"(?) Внимание вопрос:\n%s" % (question))

def quizStop(conference, showScores=True):
	gQuizEnable[conference] = False
	del gQuizAnswer[conference]
	del gQuizQuestion[conference]
	del gQuizHint[conference]
	del gQuizIdleCount[conference]
	del gQuizAskTime[conference]
	if isQuizTimerEnabled(conference):
		gQuizTimer[conference].cancel()
		del gQuizTimer[conference]
	if showScores:
		showScoreList(protocol.TYPE_PUBLIC, conference)

def checkQuizAnswer(conference, nick, trueJid, answer):
	rightAnswer = gQuizAnswer[conference].lower()
	userAnswer = answer.lower()
	if rightAnswer == userAnswer:	
		gQuizEnable[conference] = False
		answerTime = time.time() - gQuizAskTime[conference]
		wLength = len(gQuizHint[conference])
		closedLetters = gQuizHint[conference].count("*")
		points = int(wLength * closedLetters * (QUIZ_COEF / answerTime))
		if points:
			sendToConference(conference, u"(!) %s, поздравляю! +%d в банк! Верный ответ: %s" % (nick, points, rightAnswer))
		else:
			sendToConference(conference, u"(!) %s, поздравляю! Верный ответ: %s" % (nick, rightAnswer))
		base = gQuizScores[conference]
		if trueJid in base:
			base[trueJid][0] = nick
			base[trueJid][1] += points
			base[trueJid][2] += 1
		else:
			base[trueJid] = [nick, points, 1]
		base.save()
		askQuizQuestion(conference)

def quizAnswerListener(stanza, msgType, conference, nick, trueJid, text):
	if gQuizEnable[conference]:
		checkQuizAnswer(conference, nick, trueJid, text)

def showScoreList(msgType, conference, nick=None):
	base = gQuizScores[conference]
	if not base.isEmpty():
		scores = []
		for jid, info in base.items():
			scores.append([info[1], info[2], info[0]])
		scores.sort()
		scores.reverse()
		scores = scores[:10]
		items = [u"%s) %s, %s, %s" % (i + 1, x[2], x[0], x[1]) for i, x in enumerate(scores)]
		if nick:
			message = u"Статистика по игре:\nНик, счет, ответов\n"
			sendMsg(msgType, conference, nick, message + "\n".join(items))
		else:
			message = u"(*) Счёт:\nНик, счет, ответов\n"
			sendToConference(conference, message + "\n".join(items))
	else:
		if nick:
			sendMsg(msgType, conference, nick, u"Статистика по игре отсутствует")

def startQuiz(msgType, conference, nick, param):
	if gQuizEnable[conference]:
		sendMsg(msgType, conference, nick, u"Викторина уже существует!")
	else:
		askQuizQuestion(conference)

def stopQuiz(msgType, conference, nick, param):
	if gQuizEnable[conference]:
		sendToConference(conference, u"(!) Викторина остановлена")
		quizStop(conference)

def showNextQuestion(msgType, conference, nick, param):
	if gQuizEnable[conference]:
		askQuizQuestion(conference, gQuizAnswer[conference])

def showQuizHint(msgType, conference, nick, param):
	if gQuizEnable[conference]:
		answer = gQuizAnswer[conference]
		hint = gQuizHint[conference]
		hiddenLetters = ""
		for i in range(0, len(answer)):
			if hint[i] == "*":
				hiddenLetters += answer[i]
		randLetter = random.choice(hiddenLetters)
		for i in range(0, len(answer)):
			if answer[i] == randLetter:
				hint[i] = randLetter
		if hint.count("*"):
			gQuizHint[conference] = hint
			sendToConference(conference, u"(*) Подсказка: %s" % ("".join(hint)))
			gQuizIdleCount[conference] = 0
			resetQuizTimer(conference)
		else:
			askQuizQuestion(conference, answer)

def showQuizScores(msgType, conference, nick, param):
	showScoreList(msgType, conference, nick)

def showQuizQuestion(msgType, conference, nick, param):
	if gQuizEnable[conference]:
		sendMsg(msgType, conference, nick, u"(*) Текущий вопрос: \n" + gQuizQuestion[conference])
		
def loadQuizScores(conference):
	path = getConfigPath(conference, QUIZ_SCORES_FILE)
	gQuizScores[conference] = database.DataBase(path)
	gQuizEnable[conference] = False

def freeQuizScores(conference):
	del gQuizScores[conference]

registerEvent(loadQuizScores, ADDCONF)
registerEvent(freeQuizScores, DELCONF)
registerMessageHandler(quizAnswerListener, CHAT)

registerCommand(startQuiz, u"старт", 10, 
				u"Запуск игры", 
				None, 
				None, 
				CHAT | NONPARAM)
registerCommand(stopQuiz, u"стоп", 10, 
				u"Остановка игры", 
				None, 
				None, 
				CHAT | NONPARAM)
registerCommand(showQuizScores, u"счет", 10, 
				u"Показывает счёт игры", 
				None, 
				None, 
				CHAT | NONPARAM)
registerCommand(showQuizHint, u"х", 10, 
				u"Показать подсказку", 
				None, 
				None, 
				CHAT | NONPARAM)
registerCommand(showQuizQuestion, u"повтор", 10, 
				u"Повтор текущего вопроса", 
				None, 
				None, 
				CHAT | NONPARAM)
registerCommand(showNextQuestion, u"сл", 10, 
				u"Следущий вопрос", 
				None, 
				None, 
				CHAT | NONPARAM)
