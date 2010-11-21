# coding: utf-8

# учётная запись и пароль
PROFILE_JID = "username@server.tld"
PROFILE_PASSWORD = "secret"

# ресурс и приоритет
PROFILE_RESOURCE = "Snapi-Snup"
PROFILE_PRIORITY = 0

# станд. ник для конференций
PROFILE_NICK = u"Snapi-Snup"

# сервер и порт для подключения
PROFILE_HOST = "server.tld"
PROFILE_PORT = 5222

# client.SECURE_DISABLE - отключить SSL/TLS
# client.SECURE_AUTO - автоопределение (SSL, если порт 443, 5223, иначе TLS)
# client.SECURE_FORCE - форсировать (нестандартный порт)
PROFILE_SECURE = client.SECURE_AUTO
PROFILE_USE_RESOLVER = False

# список владельцев бота и пароль
PROFILE_ADMINS = ["admin@server.tld"]
PROFILE_ADMIN_PASSWORD = "secret"

# перезагружаться при ошибках?
PROFILE_RESTART = True

# Описание флагов лога:
# always - все типы флагов
# info - различные инф. сообщения
# error - ошибки
# success - успешные результаты
# warning - предупреждения
PROFILE_CORE_DBG = ["always"]
# always - все типы флагов
# auth - авторизация
# bind - назначение ресурса
# dispatcher - обработка станз
# roster - работа с ростером
# socket - передаваемые данные
# tls - включение TLS/SSL
PROFILE_XMPP_DBG = []

# папка для логов конференций
PROFILE_LOG_DIR = ""

# расскоментируйте, чтобы отключить логирование действий
# лог ошибок по прежнему можно будет посмотреть в syslogs
#debug.Debug = debug.NoDebug
