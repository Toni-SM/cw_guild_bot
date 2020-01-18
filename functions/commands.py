import html
import telegram

import model
import utils
import settings

# DEFAULT COMMANDS

def start(update, context):
    """
    Start the bot
    """
    cid=update.effective_user.id
    user=model.User(id=update.effective_user.id,
                    username=update.effective_user.username,
                    full_name=update.effective_user.full_name,
                    link=update.effective_user.link,
                    is_bot=update.effective_user.is_bot)
    # send the message
    context.bot.send_message(chat_id=cid, 
                             text=settings.MESSAGES["start"].format(html.escape(update.effective_user.full_name)),
                             parse_mode=telegram.ParseMode.HTML)
              
def help(update, context):
    """
    Show the help message
    """
    cid=update.effective_user.id
    # send the message
    context.bot.send_message(chat_id=cid, 
                             text=settings.MESSAGES["help"].format(html.escape(update.effective_user.full_name)),
                             parse_mode=telegram.ParseMode.HTML)

# ADMIN COMMANDS

def users(update, context):
    """
    List the subscribed users
    """
    try:
        if str(update.effective_user.id)==settings.ADMIN_ID:
            users=model.users()
            # summary
            if update.message.text=="/users":            
                text=u'<b>Subscribed users:</b> {0}\n\nUse /users_list for display the full list (a lot of messages)'.format(len(users))
                context.bot.send_message(chat_id=settings.ADMIN_ID, 
                                         text=text,
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
            # full list
            elif update.message.text=="/users_list":            
                text=""
                for user in users:
                    tmp=u'\U0001F539 {0} {1}\n      @{2}\n'.format(user.cw_level, html.escape(user.cw_name), html.escape(user.username))
                    if len(text)+len(tmp)<telegram.constants.MAX_MESSAGE_LENGTH-5:
                        text+=tmp
                    else:
                        context.bot.send_message(chat_id=settings.ADMIN_ID, 
                                                 text=text,
                                                 disable_web_page_preview=True)
                        text=""
                if text:
                    context.bot.send_message(chat_id=settings.ADMIN_ID, 
                                             text=text,
                                             disable_web_page_preview=True)
    except Exception as e:
        utils._admin_error(context, "/users", error=str(e), trace=False)
    
def message(update, context):
    """
    Send a message to each user
    """
    try:
        if str(update.effective_user.id)==settings.ADMIN_ID:
            # message hint
            if update.message.text=="/message":            
                text='Use /message <i>text</i> for send the current text to each subscribed user\n\nThe text can be formatted:\n{0} user full name\n{1} admin link'
                context.bot.send_message(chat_id=settings.ADMIN_ID, 
                                         text=text,
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
            # build and send message
            else:
                text=update.message.text[9:]
                text.format("", html.escape(settings.ADMIN_CONTACT))
                counter_success=0
                counter_fail=0
                list_fail=[]
                users=model.users()
                for user in users:
                    try: 
                        context.bot.send_message(chat_id=user.id, 
                                                 text=text.format(html.escape(user.full_name), html.escape(settings.ADMIN_CONTACT)),
                                                 parse_mode=telegram.ParseMode.HTML,
                                                 disable_web_page_preview=True)
                        counter_success+=1
                    except Exception as e:
                        counter_fail+=1
                        list_fail.append(user.full_name)
                # send report to the admin
                report_text='<b>Message:</b> {0}\n\n<b>Subscribed users:</b> {1}\n<b>Successful deliveries:</b> {2}\n<b>Unsuccessful deliveries:</b> {3}'.format(text.format("USER", html.escape(settings.ADMIN_CONTACT)), len(users), counter_success, counter_fail)
                if list_fail:
                    report_text+="\n<b>Unsuccessful users:</b> {0}".format(", ".join(list_fail))
                context.bot.send_message(chat_id=settings.ADMIN_ID,   
                                         text=report_text,
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
    except Exception as e:
        utils._admin_error(context, "/message", error=str(e), trace=False)
   
# COMMANDS
   
def pin(update, context):
    """
    Pin a message
    """
    cid=update.message.chat.id
    # text
    text=" ".join(update.message.text.split(" ")[1:])
    if text:
        context.bot.pin_chat_message(chat_id=cid, 
                                     message_id=update.message.message_id, 
                                     disable_notification=None)
    else:
        text='Use /pin <i>text</i> for pin a message in the current chat'
        context.bot.send_message(chat_id=cid, 
                                 text=text,
                                 parse_mode=telegram.ParseMode.HTML,
                                 disable_web_page_preview=True)
                                 
def everybody(update, context):
    """
    Mention all subscribed users
    """
    cid=update.message.chat.id
    # telegram user
    user=model.User(id=update.effective_user.id,
                    username=update.effective_user.username,
                    full_name=update.effective_user.full_name,
                    link=update.effective_user.link,
                    is_bot=update.effective_user.is_bot)
    # mention users 
    users=model.users()
    i=0
    tmp=""
    for u in users:
        if u.id==str(update.effective_user.id):
            continue
        tmp+="@{0} ".format(u.username)
        i+=1
        if not i%3:
            i=0
            try:
                context.bot.send_message(chat_id=cid, 
                                         text=tmp,
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
            except Exception as e:
                utils._admin_error(context, "/everybody", user=user, error=str(e))
            tmp=""
    if tmp:
        try:
            context.bot.send_message(chat_id=cid, 
                                     text=tmp,
                                     parse_mode=telegram.ParseMode.HTML,
                                     disable_web_page_preview=True)
        except Exception as e:
            utils._admin_error(context, "/everybody", user=user, error=str(e))
   
def elite(update, context):
    """
    Mention the elite 
    """
    cid=update.message.chat.id
    # telegram user
    user=model.User(id=update.effective_user.id,
                    username=update.effective_user.username,
                    full_name=update.effective_user.full_name,
                    link=update.effective_user.link,
                    is_bot=update.effective_user.is_bot)
    # mention users
    users=model.users()
    i=0
    tmp=""
    max_cw_level=0
    for u in users:
        if u.cw_level>max_cw_level:
            max_cw_level=u.cw_level
    for u in users:
        if u.id==str(update.effective_user.id) or u.cw_level<max_cw_level-15:
            continue
        tmp+="@{0} ".format(u.username)
        i+=1
        if not i%3:
            i=0
            try:
                context.bot.send_message(chat_id=cid, 
                                         text=u"\U0000270A Sir! Yes Sir!\n"+tmp,
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
            except Exception as e:
                utils._admin_error(context, "/elite", user=user, error=str(e))
            tmp=""
    if tmp:
        try:
            context.bot.send_message(chat_id=cid, 
                                     text=tmp,
                                     parse_mode=telegram.ParseMode.HTML,
                                     disable_web_page_preview=True)
        except Exception as e:
            utils._admin_error(context, "/elite", user=user, error=str(e))
