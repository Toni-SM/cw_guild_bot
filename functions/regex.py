import html
import json
import datetime
import telegram

import model
import utils
import settings


CACHE={}

def stomp(update, context):
    """
    Mention stronger users for stomp the hostile creatures
    """
    if settings.VERBOSE:
        print("[REGEX] help for stomp hostile creatures")
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
            
def resource(update, context):
    """
    Show info about an specific resource
    """
    global CACHE
    day_range=7
    if settings.VERBOSE:
        print("[REGEX] resource")
    cid=update.message.chat.id
    
    # validate user
    if not utils._check_user(context, update.effective_user.id, cid):
        return
        
    # list of resources
    recipes=""
    parts=""
    # code
    r_recipe=utils.item_by_code("r{0}".format(update.message.text.split("@")[0][2:]), "recipes")
    r_recipe_amount=0
    r_part=utils.item_by_code("k{0}".format(update.message.text.split("@")[0][2:]), "parts", adjust_part_code=True)
    r_part_amount=0
    if r_recipe and r_part:
        # guild
        if "guild" in CACHE:
            # recipes
            tmp=CACHE["guild"]["recipes"].get(r_recipe["name"].lower(), 0)
            if tmp:
                r_recipe_amount+=tmp
                recipes+="\n    - {0} x {1}".format(settings.GUILD_NAME.decode('unicode_escape'), tmp)
            # parts
            tmp=CACHE["guild"]["parts"].get(r_part["name"].lower(), 0)
            if tmp:
                r_part_amount+=tmp
                parts+="\n    - {0} x {1}".format(settings.GUILD_NAME.decode('unicode_escape'), tmp)
        # users
        for u in model.users():
            crafting=json.loads(u.crafting)
            if crafting:
                # validate the date
                dated=""
                t=datetime.datetime.fromisoformat(crafting["datetime"])
                if (datetime.datetime.today()-t).total_seconds()/(day_range*24.0*60.0*60.0)>1:
                    dated=u' \U0000231B'
                # recipes
                tmp=crafting["recipes"].get(r_recipe["name"].lower(), 0)
                if tmp:
                    r_recipe_amount+=tmp
                    recipes+='\n    - <a href="https://t.me/share/url?url=/g_deposit%20{2}%20{1}">{0}</a> x {1}{3}'.format(html.escape(u.username), tmp, r_recipe["code"], dated)
                # parts
                tmp=crafting["parts"].get(r_part["name"].lower(), 0)
                if tmp:
                    r_part_amount+=tmp
                    parts+='\n    - <a href="https://t.me/share/url?url=/g_deposit%20{2}%20{1}">{0}</a> x {1}{3}'.format(html.escape(u.username), tmp, r_part["code"], dated)
        # send message
        crafteable=u'\U00002705' if utils.item_is_crafteable(r_recipe, r_recipe_amount, r_part_amount) else u'\U0001F17E'
        text="{1} <b>{0}</b>\n(links are deposit shortcuts)\n\n".format(r_recipe["name"][:-7], crafteable)
        text+="{0} ({1}){2}\n\n{3} ({4}){5}".format(r_recipe["name"], r_recipe_amount, recipes if recipes else "", r_part["name"], r_part_amount, parts if parts else "")
        context.bot.send_message(chat_id=cid, 
                                 text=text,
                                 parse_mode=telegram.ParseMode.HTML,
                                 disable_web_page_preview=True)             
    else:
        context.bot.send_message(chat_id=cid, 
                                 text=settings.MESSAGES["unknow"].format(""),
                                 disable_web_page_preview=True)

def todo_edit(update, context):
    """
    Edit todo
    """
    action_status=False
    action_text=False
    action=""
    cid=update.message.chat.id
    
    # validate user
    if not utils._check_user(context, update.effective_user.id, cid):
        return
    
    text=update.message.text.split("_")
    if len(text)==3:
        action=text[1]
        uid=text[2]
        # get content
        data=json.loads(utils.todo_get_data().value)
        # apply action
        if action=="check" or action=="uncheck":
            print("TODO CHECK/UNCHECK", action, uid)
            for d in data:
                if d["uid"]==uid:
                    if action=="check":
                        d["checked"]=True
                    else:
                        d["checked"]=False
                    action_status=True
                    action_text=d["text"]
        elif action=="delete":
            print("TODO DELETE", uid)
            for i in range(len(data)):
                if data[i]["uid"]==uid:
                    action_text=data[i]["text"]
                    del data[i]
                    action_status=True
                    break
        # save changes
        status=model.set_data("TODO", json.dumps(data))
    # send a message
    if action_status:
        context.bot.send_message(chat_id=cid, 
                                 text="{0} has been {1}ed".format(action_text, action),
                                 disable_web_page_preview=True)
    else:
        context.bot.send_message(chat_id=cid, 
                                 text=settings.MESSAGES["unknow"].format("unknown item or format"),
                                 disable_web_page_preview=True)
        