# coding: utf-8

# учётная запись и пароль
gJid = "username@server.tld"
gPassword = "secret"

# сервер и порт для подключения 
gHost = "server.tld"
gPort = 5222

# client.SECURE_DISABLE - отключить SSL/TLS
# client.SECURE_AUTO - автоопределение (SSL, если порт 443, 5223, иначе TLS)
# client.SECURE_FORCE - форсировать (нестандартный порт)
gSecureMode = client.SECURE_AUTO
gUseResolver = False

# ресурс и приоритет
gResource = "Snapi-Snup"
gPriority = 0

# станд. ник для конференций
gBotNick = u"Snapi-Snup"

# список владельцев бота и пароль
gAdmins = ["admin@server.tld"]
gAdminPass = "secret"

# перезагружаться при ошибках?
gRestart = True

# Описание флагов лога:
# always - все типы флагов
# info - различные инф. сообщения
# error - ошибки
# success - успешные результаты
# warning - предупреждения
gCoreDebug = ["always"]
# always - все типы флагов
# auth - авторизация
# bind - назначение ресурса
# dispatcher - обработка станз
# roster - работа с ростером
# socket - передаваемые данные
# tls - включение TLS/SSL
gXMPPDebug = []

# расскоментируйте, чтобы отключить логирование действий
# лог ошибок по прежнему можно будет посмотреть в syslogs
#debug.Debug = debug.NoDebug

# папка для логов конференций
gLogDir = ""