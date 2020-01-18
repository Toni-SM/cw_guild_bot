ACTIVE=True
VERBOSE=True

# BOT
ADMIN_ID="<telegram-user-id>"
ADMIN_CONTACT="@<telegram-user-link>"
TOKEN="<bot-token-from-@BotFather>"

# PROXY
PROXY=False
PROXY_TYPE="http://"
PROXY_URL="<proxy-url>:<proxy-port>"
PROXY_AUTH="<proxy-username>:<proxy-password>"

# DATABASE
SQL_URL="sqlite:///data.db"

# CW & GUILD DATA
CW_BOT_ID=408101137
GUILD_NAME=b'\\U0001f954[31P]'

# MESSAGES
MESSAGES={
          "start": u'Welcome <b>{0}</b>!\n\nUse /help for more details',
          "help": u'Hi <b>{0}</b>! Are you having trouble?\n\nFeel free to contact with my creator if you have any question or feedback.\n\nBest regards\nMe (the bot)',
          "application-error": u'\U000026A0 Application Warning\n\n<b>message:</b> {0}\n<b>error:</b> {1}',
          "application-admin-error": u'\U0001F534\U000026A0 Application Error\n\n<b>message:</b> {0}\n<b>user:</b> {1}\n<b>error:</b> {2}\n<b>trace:</b> {3}',
          "error": u'\U0000274C {0}',
          "unknow": u'\U000002C9\U0000005C_(\U0000FF82)_/\U000002C9\n{0}',
          "cache-denied": u'\U0000274C Entry not Found\nSorry, this search is too old or I had been restarted. Write the question again for reload the search',
          "subscription": u'\U00002728 New subscription\n<b>status:</b> {0}\n<b>user:</b> {1}'
         }
