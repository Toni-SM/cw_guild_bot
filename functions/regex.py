import html
import telegram

import model
import utils
import settings


def stomp(update, context):
    """
    Mention stronger users for stomp the hostile creatures
    """
    if settings.VERBOSE:
        print("[REGEX] help for stomp hostile creatures")
    cid=update.message.chat.id
    # telegram user
    user=model.User(id=update.effective_user.id,
                    username=update.effective_user.username,
                    full_name=update.effective_user.full_name,
                    link=update.effective_user.link,
                    is_bot=update.effective_user.is_bot)
    # parse message
    msg=update.message.text[7:].split("@")[0].split("_")
    if settings.VERBOSE:
        print("       ", msg)
    # validate the user
    if msg[1]==str(update.effective_user.id):
        # list users
        users=model.filtered_users(user, int(msg[0]), 20)
        i=0
        tmp=""
        for u in users[1]:
            if u.id==str(update.effective_user.id):
                continue
            tmp+="@{0} ".format(u.username)
            i+=1
            if not i%3:
                i=0
                try:
                    context.bot.send_message(chat_id=cid, 
                                             text="Someone needs your help for stomp the hostile creatures\n"+tmp,
                                             parse_mode=telegram.ParseMode.HTML,
                                             disable_web_page_preview=True)
                except Exception as e:
                    utils._admin_error(context, "regex stomp: accepted", user=user, error=str(e))
                tmp=""
        if tmp:
            try:
                context.bot.send_message(chat_id=cid, 
                                         text="Someone needs your help for stomp the hostile creatures\n"+tmp,
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
            except Exception as e:
                utils._admin_error(context, "regex stomp: accepted", user=user, error=str(e))
    else:
        try:
            context.bot.send_message(chat_id=cid, 
                                     text=u'\U0001F622 Only the owner of this encounter can request for help',
                                     parse_mode=telegram.ParseMode.HTML,
                                     disable_web_page_preview=True)
        except Exception as e:
            utils._admin_error(context, "regex stomp: denied", user=user, error=str(e))
            