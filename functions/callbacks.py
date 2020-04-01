import html
import json
import datetime
import telegram

import model
import utils
import settings


CACHE={}

def _craft(update):
    """
    """
    global CACHE
    today=datetime.datetime.today()
    recipes={}
    parts={}
    owners=""
    text_full_list=""
    text_ready_list=""
    # guild
    if "guild" in CACHE:
        # recipes
        for k in CACHE["guild"]["recipes"]:
            if k in recipes:
                recipes[k]+=CACHE["guild"]["recipes"][k]
            else:
                recipes[k]=CACHE["guild"]["recipes"][k]
        # parts
        for k in CACHE["guild"]["parts"]:
            if k in parts:
                parts[k]+=CACHE["guild"]["parts"][k]
            else:
                parts[k]=CACHE["guild"]["parts"][k]
        if recipes:
            owners+="\n    - {0} ({1})".format(settings.GUILD_NAME.decode('unicode_escape'), "recipes")            
        if parts:
            owners+="\n    - {0} ({1})".format(settings.GUILD_NAME.decode('unicode_escape'), "parts")            
    # users
    for u in model.users():
        crafting=json.loads(u.crafting)
        if crafting and len(crafting.keys()):
            # validate the date
            t=datetime.datetime.fromisoformat(crafting["datetime"])
            tmp=(datetime.datetime.today()-t).total_seconds()/(24.0*3600.0)
            if tmp>int(model.get_data("CRAFT_OUTDATE_INTERVAL_DAYS", 3)):
                owners+=u"\n    - {0} (\U0000231B {1} days ago)".format(html.escape(u.username), int(tmp))
            else:
                owners+="\n    - {0}".format(html.escape(u.username))
            # recipes
            for k in crafting["recipes"]:
                if k in recipes:
                    recipes[k]+=crafting["recipes"][k]
                else:
                    recipes[k]=crafting["recipes"][k]
            # parts
            for k in crafting["parts"]:
                if k in parts:
                    parts[k]+=crafting["parts"][k]
                else:
                    parts[k]=crafting["parts"][k]
    # list items
    for i in range(1,125):
        code=str(i).zfill(2)
        item_recipe=utils.item_by_code("r{0}".format(code), "recipes")
        item_part=utils.item_by_code("k{0}".format(code), "parts")
        if item_recipe and item_part:
            r_recipe=recipes.get(item_recipe["name"], 0)
            r_part=parts.get(item_part["name"], 0)
            is_crafteable=utils.item_is_crafteable(item_recipe, r_recipe, r_part)
            crafteable=u'\U00002705' if is_crafteable else u'\U0001F17E'
            text_full_list+="\n/w{0}  {4}  {1} | {2}  {3}".format(code, r_recipe, r_part, item_recipe["name"][:-7], crafteable)
            if is_crafteable:
                text_ready_list+="\n/w{0}  {4}  {1} | {2}  {3}".format(code, r_recipe, r_part, item_recipe["name"][:-7], crafteable)
    return text_full_list, text_ready_list, owners


def empty(update, context):
    context.bot.answer_callback_query(update.callback_query.id)
 
def craft_resume(update, context):
    query=update.callback_query
    text_full_list, text_ready_list, owners=_craft(update)
    # send message
    text=text_ready_list
    if not len(text):
        text=u"\U0001F622 Nothing ready to craft"
    if owners:
        text+=u"\n\n<b>Owners:</b>"+owners
    else:
        text+=u"\n\n<b>Owners:</b>\n    - <i>empty list</i>"
    # inline keyboard
    keyboard=[[telegram.InlineKeyboardButton(u'\U00002705 resume', callback_data="empty"),
               telegram.InlineKeyboardButton(u'\U0001F4C3 full list', callback_data="craft_all")]]
    if query.id=="new-message":
        try:
            cid=update.message.chat.id
        except:
            cid=update.callback_query.message.chat.id
        context.bot.send_message(chat_id=cid, 
                                 text=text,
                                 reply_markup=telegram.InlineKeyboardMarkup(keyboard),
                                 parse_mode=telegram.ParseMode.HTML,
                                 disable_web_page_preview=True)
    else:
        query.edit_message_text(text=text,
                                 reply_markup=telegram.InlineKeyboardMarkup(keyboard),
                                 parse_mode=telegram.ParseMode.HTML,
                                 disable_web_page_preview=True)
        context.bot.answer_callback_query(update.callback_query.id)

def craft_all(update, context):
    query=update.callback_query
    text_full_list, text_ready_list, owners=_craft(update)
    # send message
    text=text_full_list
    # inline keyboard
    keyboard=[[telegram.InlineKeyboardButton(u'\U00002705 resume', callback_data="craft_resume"),
               telegram.InlineKeyboardButton(u'\U0001F4C3 full list', callback_data="empty")]]
    query.edit_message_text(text=text,
                            reply_markup=telegram.InlineKeyboardMarkup(keyboard),
                            parse_mode=telegram.ParseMode.HTML,
                            disable_web_page_preview=True)
    context.bot.answer_callback_query(update.callback_query.id)
