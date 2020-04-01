import html
import json
import time
import datetime
import telegram
import threading

import model
import utils
import settings

CACHE={}
BOT=None

def start():
    threading.Thread(target=check_outdata_crafting_list, name="OUTDATE_CRAFTING_TIME_INTERVAL").start()
    
def check_outdata_crafting_list():
    while True:
        time.sleep(int(model.get_data("CRAFT_OUTDATE_INTERVAL_HOURS", 8*3600)))
        cid=model.get_data("CRAFTING_ROOM_CHAT_ID", None)
        print("[TIMER] check_outdata_crafting_list:", cid)
        if cid:
            today=datetime.datetime.today()
            try:
                for u in model.users():
                    crafting=json.loads(u.crafting)
                    if crafting and len(crafting.keys()):
                        # validate the date
                        t=datetime.datetime.fromisoformat(crafting["datetime"])
                        tmp=(datetime.datetime.today()-t).total_seconds()/(24.0*3600.0)
                        if tmp>int(model.get_data("CRAFT_OUTDATE_INTERVAL_DAYS", 3)):
                            BOT.send_message(chat_id=cid, 
                                             text=u'@{0}, your crafting data is outdated. Please, forward it here...'.format(html.escape(u.username)),
                                             parse_mode=telegram.ParseMode.HTML,
                                             disable_web_page_preview=True)
            except Exception as e:
                class Context:
                    bot=BOT
                context=Context()
                utils._admin_error(context, "timer.check_outdata_crafting_list", error=str(e))
        