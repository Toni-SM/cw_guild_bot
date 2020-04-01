import os
import logging
import telegram
from telegram import ext

import utils
import settings
import functions

if not settings.ACTIVE:
    print("BOT INACTIVE (settings.py)")
    exit()

# kill process (generator)
with open('killprocess.sh', mode='w') as file_object:
    file_object.write("kill "+str(os.getpid()))
   
# logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger=logging.getLogger(__name__)

# shared data
SHARED_DATA={}

functions.filters.CACHE=SHARED_DATA
functions.commands.CACHE=SHARED_DATA
functions.regex.CACHE=SHARED_DATA
functions.callbacks.CACHE=SHARED_DATA
functions.timers.CACHE=SHARED_DATA


# ERROR HANDLER

def _error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    # send the error message to the admin
    utils._admin_error(context, "INTERNAL ERROR", error=str(context.error))
    return
    # send the error message to current user if is valid
    try:
        context.bot.send_message(chat_id=update.effective_user.id, 
                                 text=settings.MESSAGES["application-error"].format(update._effective_message.text, context.error), 
                                 parse_mode=telegram.ParseMode.HTML)
    except Exception as e:
        print("[EXCEPTION] user _error", e)
   
# MESSAGE HANDLERS
              
def _incomming_message(update, context):
    pass

# UTILITIES

def _notify_start(bot):
    try:
        bot.send_message(chat_id=settings.ADMIN_ID, 
                         text=u'\U0001F50B\U000026A1 Bot started')
    except Exception as e:
        print("[EXCEPTION] _notify_start")



              
if __name__=="__main__":

    # proxy authentication
    REQUEST_KWARGS=None
    if settings.PROXY:
        import telegram.vendor.ptb_urllib3.urllib3 as urllib3
        REQUEST_KWARGS={"proxy_url": settings.PROXY_TYPE+settings.PROXY_URL, 
                        "urllib3_proxy_kwargs": {'proxy_headers': urllib3.make_headers(proxy_basic_auth=settings.PROXY_AUTH)}}
    
    # frontend to telegram.Bot
    updater=ext.Updater(settings.TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)
    dispatcher=updater.dispatcher
    
    # admin command handlers
    dispatcher.add_handler(ext.CommandHandler(["users", "users_list", "users_detail", "users_delete"], functions.admin.users))
    dispatcher.add_handler(ext.CommandHandler(["data", "data_set", "data_delete"], functions.admin.manage_data))
    dispatcher.add_handler(ext.CommandHandler(["message"], functions.admin.message))
    
    # command handlers
    dispatcher.add_handler(ext.CommandHandler(["start", "restart"], functions.commands.start))
    dispatcher.add_handler(ext.CommandHandler(["help"], functions.commands.help))
    dispatcher.add_handler(ext.CommandHandler(["pin"], functions.commands.pin))
    dispatcher.add_handler(ext.CommandHandler(["everybody"], functions.commands.everybody))
    dispatcher.add_handler(ext.CommandHandler(["elite"], functions.commands.elite))
    dispatcher.add_handler(ext.CommandHandler(["craft"], functions.commands.craft))
    dispatcher.add_handler(ext.CommandHandler(["craft_reset"], functions.commands.craft_reset))
    
    # regexp handlers
    dispatcher.add_handler(ext.MessageHandler(ext.Filters.regex(r'/stomp_[\w]+'), functions.regex.stomp))
    dispatcher.add_handler(ext.MessageHandler(ext.Filters.regex(r'/[wrk][\d]+'), functions.regex.resource))
    
    # filter handlers
    dispatcher.add_handler(ext.MessageHandler(ext.Filters.forwarded, functions.filters.forwarded))
    
    # message handlers
    dispatcher.add_handler(ext.MessageHandler(ext.Filters.text, _incomming_message))
    
    # callback query handlers
    dispatcher.add_handler(ext.CallbackQueryHandler(functions.callbacks.empty, pattern=r'empty'))
    dispatcher.add_handler(ext.CallbackQueryHandler(functions.callbacks.craft_resume, pattern=r'craft_resume'))
    dispatcher.add_handler(ext.CallbackQueryHandler(functions.callbacks.craft_all, pattern=r'craft_all'))
    
    # error handlers
    dispatcher.add_error_handler(_error)
    
    # timing functions
    functions.timers.BOT=updater.bot
    functions.timers.start()
    
    # notify the starting
    _notify_start(updater.bot)
    
    # start the polling
    try:
        updater.start_polling()
    except telegram.error.NetworkError as e:
        print("[TELEGRAM] error.NetworkError:", e)
    updater.idle()
