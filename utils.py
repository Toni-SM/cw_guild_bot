import time
import json
import html
import hashlib
import telegram
import traceback

import model
import settings

def _admin_error(context, msg, user="", error="", trace=True):
    trace_text="-"
    if trace:
        trace_text=html.escape(traceback.format_exc())
    try:
        context.bot.send_message(chat_id=settings.ADMIN_ID, 
                                 text=settings.MESSAGES["application-admin-error"].format(msg, html.escape(str(user)), html.escape(error), trace_text), 
                                 parse_mode=telegram.ParseMode.HTML)
    except Exception as e:
        print("[EXCEPTION] admin _error", e)

def _check_user(context, uid, cid):
    if model.user_by_id(uid) is None:
        _admin_error(context, "spai: " + str(uid) + " " + str(cid), trace=False)
        context.bot.send_message(chat_id=cid, 
                                 text="SPAI!!!")
        
        return False
    return True

# TO DO list

def todo_get_data():
    data=None
    for d in model.data():
        if d.key=="TODO":
            data=d
            break
    # create if not exist
    if not data:
        status=model.set_data("TODO", json.dumps([]))
        if settings.VERBOSE:
            print("Create TODO:", status)
        for d in model.data():
            if d.key=="TODO":
                data=d
                break
    return data

def todo_item_in_todo(todo_list, item):
    for i in todo_list:
        if item==i["text"]:
            return True
    return False

def todo_add_item(todo_list, item):
    _uid=hashlib.sha256(bytes(str(item), "utf-8")).hexdigest()[:5]
    todo_list.append({"text": item, "checked": False, "uid": _uid})

# ITEMS

ITEMS={}
with open('items.json') as jsonfile:
    ITEMS=json.load(jsonfile)

def item_by_name(item_name, item_type=None):
    if item_type in ITEMS:
        for k in ITEMS[item_type]:
            if ITEMS[item_type][k]["name"].lower()==item_name.lower():
                return ITEMS[item_type][k]
    else:
        for t in ITEMS:
            for k in ITEMS[t]:
                if ITEMS[t][k]["name"].lower()==item_name.lower():
                    return ITEMS[t][k]
    return {}
   
def item_by_code(item_code, item_type=None, adjust_part_code=False):
    # adjust part code (overseer)
    if adjust_part_code:
        if item_code=="k116":
            item_code="k117"
        elif item_code=="k117":
            item_code="k118"
        elif item_code=="k118":
            item_code="k119"
        elif item_code=="k119":
            item_code="k120"
        elif item_code=="k120":
            item_code="k116"
    if item_type in ITEMS:
        for k in ITEMS[item_type]:
            if ITEMS[item_type][k]["code"]==str(item_code):
                return ITEMS[item_type][k]
    else:
        for t in ITEMS:
            for k in ITEMS[t]:
                if ITEMS[t][k]["code"]==str(item_code):
                    return ITEMS[t][k]
    return {}
    
def item_is_crafteable(item, recipe_amount=0, part_amount=0):
    amount=0
    # adjust cloak parts
    if item["code"][1:] in ['59', '60', '61']:
        amount=3
    elif item["code"][1:] in ['100', '101', '102']:
        amount=4
    # adjust some weapons
    elif item["code"][1:] in ['91', '96', '97', '103']:
        amount=5
    elif item["code"][1:] in ['108', '110']:
        amount=7
    elif item["code"][1:] in ['105', '107', '109', '111']:
        amount=9
    # iterate by tiers
    elif item["tier"]=="T2":
        amount=3
    elif item["tier"]=="T3":
        amount=5
    elif item["tier"]=="T4":
        amount=6
    elif item["tier"]=="T5":
        amount=8
    if amount and recipe_amount>0 and part_amount>=amount:
        return True
    return False
    
def emoji_tier(tier):
    # iterate by tiers
    if tier.lower()=="t2":
        return u'\U0001F4D7'
    elif tier.lower()=="t3":
        return u'\U0001F4D8'
    elif tier.lower()=="t4":
        return u'\U0001F4D9'
    elif tier.lower()=="t5":
        return u'\U0001F4D2'
    return u'\U0001F4DA'
    
    
    
if __name__=="__main__":
    print("")
    print("item_by_name")
    print(item_by_name("Iron ore", "resources"))
    print(item_by_name("Black Morningstar part"))
    
    print("")
    print("item_by_code")
    print(item_by_code("10", "resources"))
    print(item_by_code("k99"))
    
    time.sleep(5)