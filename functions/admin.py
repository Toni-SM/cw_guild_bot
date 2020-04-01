import html
import json
import datetime
import telegram

import model
import utils
import settings

CACHE={}

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
                text=u'<b>Subscribed users:</b> {0}\n\nUse /users_list for display the full list\nUse /users_detail for display detailed info (a lot of messages)'.format(len(users))
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
            # detailed list
            elif update.message.text=="/users_detail":            
                for user in users:
                    text="<b>id:</b> {0}\n<b>username:</b> {1}\n<b>full_name:</b> {2}\n<b>link:</b> {3}\n<b>cw_name:</b> {4}\n<b>cw_level:</b> {5}\n<b>updated:</b> {6}\n<b>crafting:</b> {7}\n\n<code>/craft_reset {0}</code>\n<code>/users_delete {0}</code>".format(user.id, html.escape(user.username), html.escape(user.full_name), html.escape(user.link), html.escape(user.cw_name), user.cw_level, html.escape(user.updated), html.escape(user.crafting))
                    context.bot.send_message(chat_id=settings.ADMIN_ID, 
                                             text=text,
                                             parse_mode=telegram.ParseMode.HTML,
                                             disable_web_page_preview=True)
            # delete user
            elif update.message.text.split(" ")[0]=="/users_delete" and len(update.message.text.split(" "))==2:
                user=model.user_by_id(update.message.text.split(" ")[1])
                if user:
                    status=model.unsubscribe(user)
                    context.bot.send_message(chat_id=settings.ADMIN_ID, 
                                             text="User unsubscription operation [{1}]... for @{0}".format(html.escape(user.username), status),
                                             parse_mode=telegram.ParseMode.HTML,
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
   
def manage_data(update, context):
    """
    Manage stored data on database
    """
    if str(update.effective_user.id)==settings.ADMIN_ID:
        # list all pair key:value
        if update.message.text=="/data": 
            data=model.data()
            text=u'\U0001F4C1 Registered data\n\nUse /data_set for add or modify a key\nUse /data_delete for remove a pair key:value\n\n'
            for d in data:
                tmp=u'<b>{0}</b>: {1} ({2})\n'.format(html.escape(d.key), html.escape(d.value), html.escape(d.type_of))
                if len(text)+len(tmp)<telegram.constants.MAX_MESSAGE_LENGTH-5:
                    text+=tmp
                else:
                    context.bot.send_message(chat_id=settings.ADMIN_ID, 
                                             text=text,
                                             parse_mode=telegram.ParseMode.HTML,
                                             disable_web_page_preview=True)
                    text=""
            if text:
                context.bot.send_message(chat_id=settings.ADMIN_ID, 
                                         text=text,
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
        # add or modify a pair key:value
        elif update.message.text.split(" ")[0]=="/data_set":
            tmp=update.message.text.split(" ")
            if len(tmp)>2:
                value=" ".join(tmp[2:])
                if tmp[2]=="this":
                    value=update.message.chat.id
                status=model.set_data(tmp[1].upper(), value)
                context.bot.send_message(chat_id=settings.ADMIN_ID, 
                                         text="<b>Data (set)</b>\n\nKey: {0}\nValue: {1}\nStatus: {2}".format(html.escape(tmp[1].upper()), html.escape(" ".join(tmp[2:])), status),
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
            else:
                context.bot.send_message(chat_id=settings.ADMIN_ID, 
                                         text="<b>Invalid format</b>\n<code>/data_set KEY VALUE</code>",
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
        # delete a pair key:value
        elif update.message.text.split(" ")[0]=="/data_delete":
            tmp=update.message.text.split(" ")
            if len(update.message.text.split(" "))>1:
                status=model.del_data(tmp[1].upper())
                context.bot.send_message(chat_id=settings.ADMIN_ID, 
                                         text="<b>Data (delete)</b>\n\nKey: {0}\nStatus: {1}".format(html.escape(tmp[1].upper()), status),
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
            else:
                context.bot.send_message(chat_id=settings.ADMIN_ID, 
                                         text="<b>Invalid format</b>\n<code>/data_delete KEY</code>",
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
                                         