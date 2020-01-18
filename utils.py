import time
import json
import html
import telegram
import traceback

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


# ITEMS

ITEMS={}
with open('items.json') as jsonfile:
    ITEMS=json.load(jsonfile)

def item_by_name(item_name, item_type=None):
    if item_type in ITEMS:
        for k in ITEMS[item_type]:
            if ITEMS[item_type][k]["name"]==item_name:
                return ITEMS[item_type][k]
    else:
        for t in ITEMS:
            for k in ITEMS[t]:
                if ITEMS[t][k]["name"]==item_name:
                    return ITEMS[t][k]
    return {}
   
def item_by_code(item_code, item_type=None):
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