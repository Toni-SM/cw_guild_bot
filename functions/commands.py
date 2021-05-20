import html
import json
import datetime
import telegram

import model
import utils
import settings

from functions import callbacks

CACHE={}

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
   
# COMMANDS
   
def pin(update, context):
    """
    Pin a message
    """
    cid=update.message.chat.id
    
    # validate user
    if not utils._check_user(context, update.effective_user.id, cid):
        return 
       
    try:
        reply=update.message.reply_to_message
        context.bot.pin_chat_message(chat_id=cid, 
                                     message_id=reply.message_id, 
                                     disable_notification=None)
        return
    except Exception as e:
        pass       
    # text
    text=" ".join(update.message.text.split(" ")[1:])
    if text:
        context.bot.pin_chat_message(chat_id=cid, 
                                     message_id=update.message.message_id, 
                                     disable_notification=None)
    else:
        text='Use /pin <i>text</i> or reply a message for pin some content in the current chat'
        context.bot.send_message(chat_id=cid, 
                                 text=text,
                                 parse_mode=telegram.ParseMode.HTML,
                                 disable_web_page_preview=True)
                                 
def everybody(update, context):
    """
    Mention all subscribed users
    """
    cid=update.message.chat.id
    
    # validate user
    if not utils._check_user(context, update.effective_user.id, cid):
        return 
        
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
    
    # validate user
    if not utils._check_user(context, update.effective_user.id, cid):
        return 
        
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
        if u.id==str(update.effective_user.id) or u.cw_level<max_cw_level-model.get_data("MENTION_ELITE_DELTA", 15):
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
                                     text=u"\U0000270A Sir! Yes Sir!\n"+tmp,
                                     parse_mode=telegram.ParseMode.HTML,
                                     disable_web_page_preview=True)
        except Exception as e:
            utils._admin_error(context, "/elite", user=user, error=str(e))

def craft(update, context):
    """
    """
    cid=update.message.chat.id
    
    # validate user
    if not utils._check_user(context, update.effective_user.id, cid):
        return 
        
    update.callback_query=telegram.CallbackQuery(id="new-message", 
                                                 from_user=update.effective_user, 
                                                 chat_instance="", 
                                                 data="")
    callbacks.craft_resume(update, context)
                                     
def craft_reset(update, context):
    """
    Reset craft operation
    """
    global CACHE
    cid=update.message.chat.id
    
    # validate user
    if not utils._check_user(context, update.effective_user.id, cid):
        return 
        
    tmp=update.message.text.split(" ")
    if len(tmp)>1:
        if tmp[1]=="yes":
            # reset users
            for user in model.users():
                user.crafting="{}"
                status=model.update_user(user)
            # reset guild
            CACHE["guild"]={"resources": {},
                            "parts": {},
                            "recipes": {}}
            context.bot.send_message(chat_id=cid, 
                                     text="Crafting operation restarted...",
                                     parse_mode=telegram.ParseMode.HTML,
                                     disable_web_page_preview=True)
        else:
            user=model.user_by_id(tmp[1])
            if user:
                user.crafting="{}"
                status=model.update_user(user)
                context.bot.send_message(chat_id=cid, 
                                         text="Crafting operation restarted [{1}]... for @{0}".format(html.escape(user.username), status),
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
                
    else:
        context.bot.send_message(chat_id=cid, 
                                 text='Type "/craft_reset <i>yes</i>" to reset all operation and stored data',
                                 parse_mode=telegram.ParseMode.HTML,
                                 disable_web_page_preview=True)

def todo(update, context):
    """
    TO DO list
    """
    cid=update.message.chat.id
    
    # validate user
    if not utils._check_user(context, update.effective_user.id, cid):
        return 
        
    # get content
    data=json.loads(utils.todo_get_data().value)
    # add a replied message
    try:
        reply=update.message.reply_to_message
        text=reply.text.split("\n")
        for t in text:
            if t and not utils.todo_item_in_todo(data, t):
                utils.todo_add_item(data, t)
        # save changes
        status=model.set_data("TODO", json.dumps(data))
    except Exception as e:
        pass       
    
    # show list
    text=[]
    print(data)
    for d in data:
        tmp="{0} - {1}\n        /todo_{3}check_{2}\n        /todo_delete_{2}".format(u'\U00002705' if d["checked"] else u'\U0001F17E', d["text"], d["uid"], 'un' if d["checked"] else '')
        if d["checked"]:
            text.insert(0, tmp)
        else:
            text.append(tmp)
    if text:
        context.bot.send_message(chat_id=cid, 
                                 text="\n".join(text)+"\n\nReply a message with /todo command to add it in this list (this action append each line of the message as a single item to the list)",
                                 parse_mode=telegram.ParseMode.HTML,
                                 disable_web_page_preview=True)
    else:
        text='Reply a message with /todo command to add it in this list (this action append each line of the message as a single item to the list)'
        context.bot.send_message(chat_id=cid, 
                                 text=text,
                                 parse_mode=telegram.ParseMode.HTML,
                                 disable_web_page_preview=True)
