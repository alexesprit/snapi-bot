#!/usr/bin/python
# coding: utf-8

# pybot.py
# Initial Copyright (c) 2002-2005 Mike Mintz <mikemintz@gmail.com>
# Modification Copyright (c) 2007 Als <Als@exploit.in>
# Modification Copyright (c) 2007 dimichxp <dimichxp@gmail.com>
# Modification Copyright (c) esprit
# Part of code Copyright (c) Boris Kotov <admin@avoozl.ru>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from __future__ import with_statement

import gc
import os
import random
import re
import sys
import threading
import time
import traceback

import module.config as Config
import module.version as Version

from module import database
from module import io
from module import macros
from module import netutil

from module.xmpp import client
from module.xmpp import debug
from module.xmpp import protocol
from module.xmpp import simplexml

CONFIG_DIR = "config"
PLUGIN_DIR = "plugins"
SYSLOG_DIR = "syslogs"
RESOURCE_DIR = "resource"

BOTCONFIG_FILE = "config.py"

ACCESS_FILE = "access.dat"
CONFIG_FILE = "config.dat"
CONF_FILE = "conferences.txt"
LOG_ERRORS_FILE = "%Y.%m.%d_errors.txt"
LOG_CRASHES_FILE = "%Y.%m.%d_crashes.txt"

FLAG_INFO = "info"
FLAG_ERROR = "error"
FLAG_WARNING = "warning"
FLAG_SUCCESS = "success"

MODE_ASYNC = 0x1
MODE_SYNC = 0x2

CMD_CONFERENCE = 0x01
CMD_ROSTER = 0x02
CMD_FROZEN = 0x04
CMD_NONPARAM = 0x08
CMD_PARAM = 0x10
CMD_ANY = CMD_CONFERENCE | CMD_ROSTER

CMD_ACCESS = 0
CMD_DESC = 1
CMD_SYNTAX = 2
CMD_EXAMPLE = 3
CMD_TYPE = 4

NICK_JID = "jid"
NICK_IDLE = "idle"
NICK_HERE = "here"
NICK_ROLE = "role"
NICK_AFF = "aff"
NICK_SHOW = "show"
NICK_STATUS = "status"
NICK_JOINED = "joined"

LOG_ERRORS = 0x1
LOG_CRASHES = 0x2

LOG_TYPES = {
    LOG_CRASHES: LOG_CRASHES_FILE,
    LOG_ERRORS: LOG_ERRORS_FILE
}

ROLES = {
    protocol.ROLE_NONE: 0,
    protocol.ROLE_VISITOR: 0,
    protocol.ROLE_PARTICIPANT: 10,
    protocol.ROLE_MODERATOR: 15
}

AFFILIATIONS = {
    protocol.AFF_OUTCAST: 0,
    protocol.AFF_NONE: 0,
    protocol.AFF_MEMBER: 1,
    protocol.AFF_ADMIN: 5,
    protocol.AFF_OWNER: 15
}

FORBIDDEN_TYPES = (
    protocol.TYPE_NORMAL,
    protocol.TYPE_HEADLINE
)

STATUS_STRINGS = (
    protocol.PRS_AWAY,
    protocol.PRS_NA,
    protocol.PRS_DND,
    protocol.PRS_CHAT
)

KEEPALIVE_TIMEOUT = 120
REJOIN_DELAY = 60
RECONNECT_DELAY = 15

H_CONFERENCE = 0x0001
H_ROSTER = 0x0002

EVT_IQ = 0x0004
EVT_MSG = 0x0008
EVT_PRS = 0x0010

EVT_SELFMSG = 0x0020

EVT_USERJOIN = 0x0040
EVT_USERLEAVE = 0x0080

EVT_ADDCONFERENCE = 0x0100
EVT_DELCONFERENCE = 0x0200

EVT_CONNECTED = 0x0400
EVT_READY = 0x0800
EVT_SHUTDOWN = 0x1000

ACTION_RESTART = 0x1
ACTION_SHUTDOWN = 0x2

gEventHandlers = {}
gCmdHandlers = {}

gGlobalAccess = {}
gTempAccess = {}
gPermAccess = {}

gCommands = {}
gCmdOff = {}
gMacros = macros.Macros(CONFIG_DIR)

gConferenceConfig = {}
gConferences = {}

gInfo = {"msg": 0, "prs": 0, "iq": 0, "cmd": 0, "thr": 0, "err": 0, "last": 0}

gDebug = debug.Debug([debug.DBG_ALWAYS], showFlags=False)
gDebug.colors[FLAG_ERROR] = debug.colorBrightRed
gDebug.colors[FLAG_WARNING] = debug.colorYellow
gDebug.colors[FLAG_SUCCESS] = debug.colorBrightCyan

def registerCommand(function, command, access, desc, syntax, examples, cmdType=CMD_ANY):
    gCmdHandlers[command] = function
    gCommands[command] = (access, desc, syntax, examples, cmdType)

def registerEventHandler(function, evtType):
    if evtType not in gEventHandlers:
        gEventHandlers[evtType] = []
    gEventHandlers[evtType].append(function)

def callEventHandlers(evtType, mode, *args):
    if evtType in gEventHandlers:
        if MODE_ASYNC == mode:
            for function in gEventHandlers[evtType]:
                startThread(function, *args)
        else:
            for function in gEventHandlers[evtType]:
                function(*args)

def clearEventHandlers(evtType):
    del gEventHandlers[evtType]

def startThread(function, *args):
    gInfo["thr"] += 1
    threading.Thread(None, execute, function.__name__, (function, args)).start()

def startTimer(timeout, function, *args):
    gInfo["thr"] += 1
    timer = threading.Timer(timeout, execute, (function, args))
    timer.setName(function.__name__)
    timer.start()
    return timer

def execute(function, args):
    try:
        function(*args)
    except Exception:
        printf(u"Exception in %s function [args: %s]" % (function.__name__, str(args)), FLAG_ERROR)
        addTextToSysLog(traceback.format_exc(), LOG_ERRORS)

def printf(text, flag=FLAG_INFO):
    gDebug.show(text, flag, flag)

getFilePath = os.path.join

def getConfigPath(*param):
    return os.path.join(CONFIG_DIR, *param)

def getUptimeStr(time):
    minutes, seconds = divmod(time, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    timeStr = "%02d:%02d:%02d" % (hours, minutes, seconds)
    if days:
        timeStr = u"%d дн. %s" % (days, timeStr)
    return timeStr

def getTimeStr(time):
    minutes, seconds = divmod(time, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    timeStr = ""
    if seconds:
        timeStr = u"%d сек." % (seconds)
    if minutes:
        timeStr = u"%d мин. %s" % (minutes, timeStr)
    if hours:
        timeStr = u"%d ч. %s" % (hours, timeStr)
    if days:
        timeStr = u"%d дн. %s" % (days, timeStr)
    return timeStr

def saveConferences():
    io.write(getConfigPath(CONF_FILE), gConferences.keys())

def loadConferenceConfig(conference):
    path = getConfigPath(conference, CONFIG_FILE)
    gConferenceConfig[conference] = io.load(path, {})

def saveConferenceConfig(conference):
    path = getConfigPath(conference, CONFIG_FILE)
    io.dump(path, gConferenceConfig[conference])

def getConferenceConfigKey(conference, key):
    return gConferenceConfig[conference].get(key)

def setConferenceConfigKey(conference, key, value):
    gConferenceConfig[conference][key] = value

def addConference(conference):
    gConferences[conference] = {}
    loadConferenceConfig(conference)
    callEventHandlers(EVT_ADDCONFERENCE, MODE_SYNC, conference)

def delConference(conference):
    callEventHandlers(EVT_DELCONFERENCE, MODE_SYNC, conference)
    del gConferenceConfig[conference]
    del gConferences[conference]

def joinConference(conference):
    nick = getBotNick(conference)
    pswd = getConferenceConfigKey(conference, "password")    

    status = getConferenceConfigKey(conference, "status")
    show = getConferenceConfigKey(conference, "show")
    jid = u"%s/%s" % (conference, nick)

    prs = getPresenceNode(jid, show, status)
    mucTag = prs.addChild("x", xmlns=protocol.NS_MUC)
    mucTag.addChild("history", {"maxchars": "0"})
    if pswd:
        mucTag.setTagData("password", pswd)
    gClient.send(prs)

def leaveConference(conference, status=None):
    setOfflineStatus(conference, status)
    delConference(conference)

getConferences = gConferences.keys

def isConferenceInList(conference):
    return conference in gConferences

def getMUCSetRoleStanza(conference, user, role, reason=None):
    iq = protocol.Iq(protocol.TYPE_SET, to=conference)
    query = iq.addChild("query", xmlns=protocol.NS_MUC_ADMIN)
    role = query.addChild("item", {"nick": user, "role": role})
    if reason:
        role.setTagData("reason", reason)
    return iq

def getMUCSetAfflStanza(conference, user, itemType, aff, reason=None):
    iq = protocol.Iq(protocol.TYPE_SET, to=conference)
    query = iq.addChild("query", xmlns=protocol.NS_MUC_ADMIN)
    aff = query.addChild("item", {itemType: user, "affiliation": aff})
    if reason:
        aff.setTagData("reason", reason)
    return iq
    
def setMUCRole(conference, user, role, reason=None):
    iq = getMUCSetRoleStanza(conference, user, role, reason)
    gClient.send(iq)

def setMUCAffl(conference, user, itemType, aff, reason=None):
    iq = getMUCSetAffiliationStanza(conference, user, itemType, aff, reason)
    gClient.send(iq)

def getBotNick(conference):
    return getConferenceConfigKey(conference, "nick") or Config.NICK

def isCommand(command):
    return command in gCommands

def isCommandType(command, cmdType):
    return gCommands[command][CMD_TYPE] & cmdType

def isAvailableCommand(conference, command):
    return command not in gCmdOff[conference]

def isMacros(macros, conference):
    return gMacros.hasMacros(macros, conference) or gMacros.hasMacros(macros)

def getNicks(conference):
    return gConferences[conference].keys()

def getOnlineNicks(conference):
    return [x for x in gConferences[conference] if getNickKey(conference, x, NICK_HERE)]

def getTrueJID(barejid, resource=None):
    if barejid in gConferences:
        if isNickInConference(barejid, resource):
            return getNickKey(barejid, resource, NICK_JID)
        return None
    return barejid

def getNickByJID(conference, truejid, offline=False):
    nicks = offline and getNicks(conference) or getOnlineNicks(conference)
    for nick in nicks:
        if getNickKey(conference, nick, NICK_JID) == truejid:
            return nick
    return None

def getNickFromJID(jid, resource):
    return (isConferenceInList(jid)) and resource or jid.split("@")[0]

def getNickKey(conference, nick, key):
    return gConferences[conference][nick].get(key)

def setNickKey(conference, nick, key, value):
    gConferences[conference][nick][key] = value

def isNickInConference(conference, nick):
    return nick in gConferences[conference]

def isNickOnline(conference, nick):
    return isNickInConference(conference, nick) and getNickKey(conference, nick, NICK_HERE)

def isNickModerator(conference, nick):
    return getNickKey(conference, nick, NICK_ROLE) == protocol.ROLE_MODERATOR

def setTempAccess(conference, jid, level=0):
    gTempAccess[conference][jid] = None
    if level:
        gTempAccess[conference][jid] = level
    else:
        del gTempAccess[conference][jid]

def setPermAccess(conference, jid, level=0):
    gPermAccess[conference][jid] = None
    if level:
        gPermAccess[conference][jid] = level
    else:
        del gPermAccess[conference][jid]
    path = getConfigPath(conference, ACCESS_FILE)
    io.dump(path, gPermAccess[conference])

def setPermGlobalAccess(jid, level=0):
    path = getConfigPath(ACCESS_FILE)
    tempAccess = io.load(path)
    tempAccess[jid] = None
    gGlobalAccess[jid] = None
    if level:
        tempAccess[jid] = level
        gGlobalAccess[jid] = level
    else:
        del tempAccess[jid]
        del gGlobalAccess[jid]
    path = getConfigPath(ACCESS_FILE)
    io.dump(path, tempAccess)

def setTempGlobalAccess(jid, level=0):
    gGlobalAccess[jid] = None
    if level:
        gGlobalAccess[jid] = level
    else:
        del gGlobalAccess[jid]

def getAccess(conference, jid):
    if jid in gGlobalAccess:
        return gGlobalAccess[jid]
    if conference in gConferences:
        if jid in gPermAccess[conference]:
            return gPermAccess[conference][jid]
        if jid in gTempAccess[conference]:
            return gTempAccess[conference][jid]
    else:
        return 10
    return 0

def getPresenceNode(to=None, show=None, status=None):
    prs = protocol.Presence(to, show=show, status=status)
    prs.setAttr("ver", Version.version)
    caps = prs.addChild("c", xmlns=protocol.NS_CAPS)
    caps.setAttr("node", Version.caps)
    caps.setAttr("ver", Version.verhash)
    caps.setAttr("hash", "sha-1")
    return prs

def setStatus(to=None, show=None, status=None):
    gClient.send(getPresenceNode(to, show, status))

def setOfflineStatus(to=None, status=None):
    prs = protocol.Presence(to, protocol.PRS_OFFLINE, status=status)
    gClient.send(prs)

def sendTo(msgType, jid, text):
    message = protocol.Message(jid, typ=msgType)
    text = text.strip()
    if text is not None:
        message.setBody(text)
    gClient.send(message)
    callEventHandlers(EVT_SELFMSG, MODE_ASYNC, msgType, jid, text)

def sendToConference(conference, text):
    sendTo(protocol.TYPE_PUBLIC, conference, text)

def sendMsg(msgType, conference, nick, text, force=False):
    if protocol.TYPE_PUBLIC == msgType and not force:
        msgLimit = getConferenceConfigKey(conference, "msg")
        if msgLimit and len(text) > msgLimit:
            sendMsg(msgType, conference, nick, u"Смотри в привате (ограничение в %d символов)" % (msgLimit), True)
            msgType = protocol.TYPE_PRIVATE
    if protocol.TYPE_PUBLIC == msgType:
        text = u"%s, %s" % (nick, text)
        jid = conference
    else:
        jid = u"%s/%s" % (conference, nick)
    sendTo(msgType, jid, text)

def startKeepAliveSending():
    def conference_ping_answer(stanza, conference):
        if protocol.TYPE_RESULT == stanza.getType():
            userNicks = (x.getAttr('name') for x in stanza.getQueryChildren())
            if getBotNick(conference) not in userNicks:
                joinConference(conference)
                printf('rejoined to %s' % conference)

    for conference in gConferences:
        iq = protocol.Iq(protocol.TYPE_GET)
        query = iq.addChild("query", xmlns=protocol.NS_DISCO_ITEMS)
        iq.setTo(conference)
        gClient.sendAndCallForResponse(iq, conference_ping_answer, (conference, ))
        time.sleep(1)
    startTimer(KEEPALIVE_TIMEOUT, startKeepAliveSending)

def parseMessage(stanza):
    gInfo["msg"] += 1
    msgType = stanza.getType()
    if stanza.isOffline() or msgType in FORBIDDEN_TYPES:
        return
    fulljid = stanza.getFrom()
    barejid = fulljid.getBareJID()
    conference = barejid
    isConference = conference in gConferences
    if protocol.TYPE_PUBLIC == msgType and not isConference:
        return
    resource = fulljid.getResource()
    nick = resource
    if isConference:
        truejid = getTrueJID(conference, nick)
        userAccess = getAccess(conference, truejid)
    else:
        userAccess = getAccess(None, barejid)
    if -100 == userAccess:
        return
    message = (stanza.getBody() or "").strip()
    isSystem = False
    if isConference:
        if not nick:
            isSystem = True
    if protocol.TYPE_ERROR == msgType:
        errorCode = stanza.getErrorCode()
        if errorCode == "500":
            time.sleep(1)
            gClient.send(stanza.buildReply(protocol.TYPE_PUBLIC, message))
        elif errorCode == "406":
            addTextToSysLog("Not allowed: %s" % (str(stanza)), FLAG_WARNING)
            joinConference(conference)
        return
    if not message:
        return
    if protocol.TYPE_PUBLIC == msgType:
        if not isSystem:
            setNickKey(conference, nick, NICK_IDLE, time.time())
    else:
        if stanza.getTag("request"):
            reportMsg = protocol.Message(fulljid)
            reportMsg.setID(stanza.getID())
            reportMsg.addChild("received", xmlns=protocol.NS_RECEIPTS)
            gClient.send(reportMsg)
    if isConference:
        callEventHandlers(EVT_MSG | H_CONFERENCE, MODE_ASYNC, stanza, msgType, conference, nick, truejid, message)
    else:
        callEventHandlers(EVT_MSG | H_ROSTER, MODE_ASYNC, stanza, msgType, barejid, resource, message)
    # topic can starts with some command word
    if isSystem:
        return
    if isConference:
        botNick = getBotNick(conference)
        if botNick == nick:
            return
        if message.startswith(botNick):
            for x in [botNick + x for x in (":", ",")]:
                if message.startswith(x):
                    message = message.replace(x, "").strip()
                    break
        prefix = getConferenceConfigKey(barejid, "prefix")
        if prefix:
            if message.startswith(prefix):
                message = message[len(prefix):].strip()
            elif protocol.TYPE_PUBLIC == msgType:
                return
        if not message:
            return
    rawbody = message.split(None, 1)
    command = rawbody[0].lower()
    if isConference:
        if not isAvailableCommand(conference, command):
            return
    if isCommand(command):
        cmdAccess = gCommands[command][CMD_ACCESS]
    else:
        if gMacros.hasMacros(command):
            param = (len(rawbody) == 2) and rawbody[1] or None
            message = gMacros.getParsedMacros(command, param, (barejid, nick))
            cmdAccess = gMacros.getAccess(command)
        else:
            if isConference and gMacros.hasMacros(command, conference):
                param = (len(rawbody) == 2) and rawbody[1] or None
                message = gMacros.getParsedMacros(command, param, (conference, nick), conference)
                cmdAccess = gMacros.getAccess(command, conference)
            else:
                return
        rawbody = message.split(None, 1)
        command = rawbody[0].lower()
        if not isCommand(command):
            return
        if isConference:
            if not isAvailableCommand(conference, command):
                return
    cmdType = isConference and CMD_CONFERENCE or CMD_ROSTER
    if isCommandType(command, cmdType):
        if userAccess >= cmdAccess:
            param = (len(rawbody) == 2) and rawbody[1] or None
            if param and isCommandType(command, CMD_NONPARAM):
                return
            if not param and isCommandType(command, CMD_PARAM):
                return
            gInfo["cmd"] += 1
            gInfo["last"] = time.time()
            startThread(gCmdHandlers[command], msgType, barejid, resource, param)
        else:
            sendMsg(msgType, barejid, resource, u"Недостаточно прав")

def parsePresence(stanza):
    gInfo["prs"] += 1
    fulljid = stanza.getFrom()
    jid = fulljid.getBareJID()
    prsType = stanza.getType()
    if jid in gConferences:
        conference = jid
        truejid = stanza.getJID()
        nick = fulljid.getResource()
        if truejid:
            truejid = protocol.UserJID(truejid).getBareJID()
        if not prsType:
            if not truejid:
                leaveConference(conference, u"Без прав модератора работа невозможна!")
                return
            aff = stanza.getAffiliation()
            role = stanza.getRole()
            if not isNickOnline(conference, nick):
                if not isNickInConference(conference, nick):
                    gConferences[conference][nick] = {}
                setNickKey(conference, nick, NICK_JID, truejid)
                setNickKey(conference, nick, NICK_IDLE, time.time())
                setNickKey(conference, nick, NICK_HERE, True)
                setNickKey(conference, nick, NICK_JOINED, time.time())

                callEventHandlers(EVT_USERJOIN, MODE_ASYNC, conference, nick, truejid, aff, role)
            roleAccess = ROLES[role]
            affAccess = AFFILIATIONS[aff]
            setTempAccess(conference, truejid, roleAccess + affAccess)
            setNickKey(conference, nick, NICK_AFF, aff)
            setNickKey(conference, nick, NICK_ROLE, role)
        elif protocol.PRS_OFFLINE == prsType:
            if nick == getBotNick(conference):
                printf(u"dc: %s" % (conference))
                printf(stanza)
            if isNickOnline(conference, nick):
                code = stanza.getStatusCode()
                reason = stanza.getReason() or stanza.getStatus()
                if "303" == code:
                    newNick = stanza.getNick()
                    if not isNickInConference(conference, newNick):
                        gConferences[conference][newNick] = {}
                    for key in gConferences[conference][nick]:
                        oldval = getNickKey(conference, nick, key)
                        setNickKey(conference, newNick, key, oldval)
                setNickKey(conference, nick, NICK_HERE, False)
                if not getNickByJID(conference, truejid):
                    setTempAccess(conference, truejid)
                for key in (NICK_IDLE, NICK_AFF, NICK_ROLE, NICK_STATUS, NICK_SHOW):
                    if key in gConferences[conference][nick]:
                        del gConferences[conference][nick][key]
                callEventHandlers(EVT_USERLEAVE, MODE_ASYNC, conference, nick, truejid, reason, code)
        elif protocol.TYPE_ERROR == prsType:
            errorCode = stanza.getErrorCode()
            if errorCode:
                try:
                    printf(stanza)
                except:
                    printf("Failed to print stanza with code %s" % (errorCode))
            if errorCode in "409":
                newNick = getBotNick(conference) + "."
                setConferenceConfigKey(conference, "nick", newNick)
                saveConferenceConfig(conference)
                joinConference(conference)
            elif errorCode in ("503", "332"):
                leaveConference(conference)
                startTimer(REJOIN_DELAY, joinConference, conference)
                printf("Got 503 error code in %s" % (conference))
            elif errorCode in ("401", "403", "405"):
                leaveConference(conference, u"Got %s error code" % errorCode)
                printf(u"Got error in %s (%s)" % (conference, errorCode), FLAG_WARNING)
            elif errorCode == "404":
                delConference(conference)
                saveConferences()
                printf(u"%s is deleted (%s)" % (conference, errorCode), FLAG_WARNING)
        callEventHandlers(EVT_PRS | H_CONFERENCE, MODE_ASYNC, stanza, conference, nick, truejid)
    else:
        if protocol.PRS_SUBSCRIBE == prsType:
            printf(u"%s has added me into his/her roster" % (jid))

            roster = gClient.getRoster()
            roster.authorize(jid)
            roster.subscribe(jid)
        elif protocol.PRS_UNSUBSCRIBE == prsType:
            printf(u"%s has removed me into his/her roster" % (jid))

            roster = gClient.getRoster()
            roster.unauthorize(jid)
            roster.delItem(jid)
        elif protocol.PRS_SUBSCRIBED == prsType:
            printf(u"I've added %s into my roster" % (jid), FLAG_SUCCESS)
        elif protocol.PRS_UNSUBSCRIBED == prsType:
            printf(u"I've removed %s from my roster" % (jid), FLAG_SUCCESS)

        resource = fulljid.getResource()
        callEventHandlers(EVT_PRS | H_ROSTER, MODE_ASYNC, stanza, jid, resource)

def parseIQ(stanza):
    gInfo["iq"] += 1
    fulljid = stanza.getFrom()
    # fix for prosody servers
    if not fulljid:
        return
    barejid = fulljid.getBareJID()
    resource = fulljid.getResource()
    isConference = barejid in gConferences
    if isConference:
        truejid = getTrueJID(barejid, resource)
        if getAccess(barejid, truejid) == -100:
            return
    else:
        if getAccess(None, barejid) == -100:
            return
    if protocol.TYPE_GET == stanza.getType():
        if stanza.getTags("query", xmlns=protocol.NS_VERSION):
            iq = stanza.buildReply(protocol.TYPE_RESULT)
            query = iq.getTag("query")
            query.setTagData("name", Version.appname)
            query.setTagData("version", Version.version)
            query.setTagData("os", Version.osname)
        elif stanza.getTags("query", xmlns=protocol.NS_LAST):
            iq = stanza.buildReply(protocol.TYPE_RESULT)
            query = iq.getTag("query")
            query.setAttr("seconds", int(time.time() - gInfo["last"]))
        elif stanza.getTags("time", xmlns=protocol.NS_ENTITY_TIME):
            tZone = time.altzone if time.localtime()[8] else time.timezone
            sign = (tZone < 0) and "+" or "-"
            tzo = "%s%02d:%02d" % (sign, abs(tZone) / 3600, abs(tZone) / 60 % 60)
            utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            iq = stanza.buildReply(protocol.TYPE_RESULT)
            tNode = iq.addChild("time", xmlns=protocol.NS_ENTITY_TIME)
            tNode.setTagData("tzo", tzo)
            tNode.setTagData("utc", utc)
        elif stanza.getTags("ping", xmlns=protocol.NS_PING):
            iq = stanza.buildReply(protocol.TYPE_RESULT)
        elif stanza.getTags("query", xmlns=protocol.NS_DISCO_INFO):
            iq = stanza.buildReply(protocol.TYPE_RESULT)
            query = iq.addChild("query", xmlns=protocol.NS_DISCO_ITEMS)
            attrs = {
                "category": Version.identcat,
                "type": Version.identtype,
                "name": Version.identname
            }
            query.addChild("identity", attrs)
            for feat in Version.BOT_FEATURES:
                query.addChild("feature", {"var": feat})
        else:
            iq = stanza.buildReply(protocol.TYPE_ERROR)
            error = iq.addChild("error", {"type": "cancel"})
            error.addChild("feature-not-implemented", xmlns=protocol.NS_STANZAS)
        gClient.send(iq)
    if isConference:
        callEventHandlers(EVT_IQ | H_CONFERENCE, MODE_ASYNC, stanza, barejid, resource, truejid)
    else:
        callEventHandlers(EVT_IQ | H_ROSTER, MODE_ASYNC, stanza, barejid, resource)

def addTextToSysLog(text, logtype, show=False):
    path = getFilePath(SYSLOG_DIR, time.strftime(LOG_TYPES[logtype]))
    if isinstance(text, unicode):
        text = text.encode("utf-8")
    io.write(path, text + "\n", "a")
    if LOG_ERRORS == logtype:
        gInfo["err"] += 1
    if show:
        printf(text, FLAG_ERROR)

def loadPlugins():
    validPlugins = 0
    invalidPlugins = 0
    plugins = os.listdir(PLUGIN_DIR)
    for plugin in plugins:
        if plugin.endswith('.py'):
            try:
                path = os.path.join(PLUGIN_DIR, plugin)
                if os.path.isfile(path):
                    execfile(path, globals())
                    validPlugins += 1
            except (SyntaxError, NameError):
                printf("Exception in loadPlugins function", FLAG_ERROR)
                addTextToSysLog(traceback.format_exc(), LOG_ERRORS)
                invalidPlugins += 1
    if not invalidPlugins:
        printf("Loaded %d plugins" % (validPlugins), FLAG_SUCCESS)
    else:
        printf("Loaded %d plugins (%d with errors)" % (validPlugins, invalidPlugins), FLAG_WARNING)

def stop(action, message=None):
    for thr in threading.enumerate():
        if isinstance(thr, threading._Timer):
            thr.cancel()
    if gClient.isConnected():
        callEventHandlers(EVT_SHUTDOWN, MODE_SYNC)
        setOfflineStatus(None, message)
        gClient.disconnect()
        gClient.disconnected()

    if ACTION_RESTART == action:
        printf("Restarting...")
        os.execl(sys.executable, sys.executable, sys.argv[0])
    elif ACTION_SHUTDOWN == action:
        printf("Terminating...", FLAG_SUCCESS)

def start():
    try:
        Config.load(BOTCONFIG_FILE)

        global gClient
        gClient = client.Client(server=Config.SERVER, port=Config.PORT)

        printf("Loading plugins...")
        loadPlugins()
        
        
        while True: 
            printf("Connecting...")
            if gClient.connect(Config.SECURE, Config.USE_RESOLVER):
                printf("Connection established (%s)" % gClient.getConnectType(), FLAG_SUCCESS)
                break
            else:
                printf("Unable to connect", FLAG_ERROR)
                if not Config.RESTART_IF_ERROR:
                    stop(ACTION_SHUTDOWN)
                    return 0
            printf("Sleeping for %d seconds..." % RECONNECT_DELAY)
            time.sleep(RECONNECT_DELAY)
                    
        printf("Authenticating...")
        if gClient.auth(Config.USERNAME, Config.PASSWORD, Config.RESOURCE):
            printf("Done", FLAG_SUCCESS)
        else:
            printf("Incorrect login/password", FLAG_ERROR)
            stop(ACTION_SHUTDOWN)
            return

        gClient.registerHandler("message", parseMessage)
        gClient.registerHandler("presence", parsePresence)
        gClient.registerHandler("iq", parseIQ)

        callEventHandlers(EVT_CONNECTED, MODE_ASYNC)
        clearEventHandlers(EVT_CONNECTED)

        gClient.getRoster()
        setStatus()

        path = getConfigPath(CONF_FILE)
        conferences = eval(io.read(path, "[]"))
        if conferences:
            for conference in conferences:
                addConference(conference)
                joinConference(conference)
                printf("joined in %s" % conference)
            printf("Entered in %d rooms" % (len(conferences)), FLAG_SUCCESS)

        startTimer(KEEPALIVE_TIMEOUT, startKeepAliveSending)

        callEventHandlers(EVT_READY, MODE_ASYNC)
        clearEventHandlers(EVT_READY)

        printf("Now I am ready to work :)")

        try:
            while gClient.process(10):
                pass
        except protocol.StreamError as se:
            printf(se.message, FLAG_WARNING)
            stop(ACTION_SHUTDOWN)
        except Exception:
            printf("Exception in main thread", FLAG_ERROR)
            addTextToSysLog(traceback.format_exc(), LOG_CRASHES)
            action = ACTION_RESTART if Config.RESTART_IF_ERROR else ACTION_SHUTDOWN
            stop(action, u"Что-то сломано...")
    except KeyboardInterrupt:
        stop(ACTION_SHUTDOWN, u"Выключаюсь: CTRL+C")
        
def main(args):
    gInfo["start"] = time.time()
    workdir = os.path.dirname(args[0])
    if workdir:
        os.chdir(workdir)
    start()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
