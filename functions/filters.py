import html
import json
import telegram
import datetime

import model
import utils
import settings


CACHE={}

def _action_fight(cid, user, content, update, context):
    """
    Mention users for a fight
    """
    header="Just another fight!\n"
    delta_upper=10
    delta_lower=20
    # forbidden champion 
    if b"Forbidden Champion lvl." in content:
        header=u"\U000026A0 Defeat the \U0000269C CHAMPION!\n\U0001F534 Don't join if you can stomp\n"
        delta_upper=1000
        delta_lower=1000
    # ambush with loot locked
    elif b"It's an ambush! Loot is locked till the end of the fight" in content:
        header=u"\U0001F4E6 Ambush with loot locked!\n"
        delta_upper=15
    # ambush without loot
    elif b"It's an ambush!" in content:
        header="Ambush without loot!\n"
        delta_upper=15
    # animals hunt 
    elif b"Bear" in content or b"Boar" in content or b"Wolf" in content:
        header=u"\U0001F417 Wild animals hunt!\n"
    if settings.VERBOSE:
        print("            Hostile creatures:", delta_lower, delta_upper, header)
    # mention users
    users=model.filtered_users(user, delta_upper, delta_lower)
    i=0
    tmp=""
    for u in users[0]:
        if u.id==str(update.effective_user.id):
            continue
        tmp+="@{0} ".format(u.username)
        i+=1
        if not i%3:
            i=0
            try:
                context.bot.send_message(chat_id=cid, 
                                         text=header+tmp,
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
            except Exception as e:
                utils._admin_error(context, "_action_fight: hostile creatures", user=user, error=str(e))
            tmp=""
    if tmp:
        try:
            context.bot.send_message(chat_id=cid, 
                                     text=header+tmp,
                                     parse_mode=telegram.ParseMode.HTML,
                                     disable_web_page_preview=True)
        except Exception as e:
            utils._admin_error(context, "_action_fight: hostile creatures", user=user, error=str(e))
    # stomp message
    if len(users[1]):
        try:
            context.bot.send_message(chat_id=cid, 
                                     text="You can call for help from stronger players to stomp the hostile creatures\n/stomp_{0}_{1}".format(delta_upper, user.id),
                                     parse_mode=telegram.ParseMode.HTML,
                                     disable_web_page_preview=True)
        except Exception as e:
            utils._admin_error(context, "_action_fight: hostile creatures", user=user, error=str(e))

def _action_battle_report(cid, user, content, update, context):
    """
    Update user info from battle report
    """
    if settings.VERBOSE:
        print("            Battle report")
    try:
        user.cw_name=content.split(settings.GUILD_NAME)[1].split(b' \\u2694:')[0].decode("unicode_escape")
        user.cw_level=int(content.split(b' Lvl: ')[1].split(b'\\n')[0].decode("unicode_escape"))
        if user.cw_name and user.cw_level:
            if model.user_by_id(update.effective_user.id):
                status=model.update_user(user)
            else:
                status=model.subscribe(user)
            if settings.VERBOSE:
                print("            {0} Lvl: {1} Status: {2}".format(user.cw_name, user.cw_level, status))
    except Exception as e:
        utils._admin_error(context, "_action_battle_report: battle report", user=user, error=str(e))

def _action_reinforcement(cid, user, content, update, context):
    """
    Detect needed materials for reinforcement
    """
    delta=5*60
    # guild warehouse message
    if content.split(b'\\n')[0]==b'Guild Warehouse:':
        # validate the cache
        if (datetime.datetime.today()-CACHE[user.id]["resources"]["datetime"]).total_seconds()>delta:
            CACHE[user.id]["resources"]["guild"]={}
            CACHE[user.id]["resources"]["reinforcement"]={}
        CACHE[user.id]["resources"]["datetime"]=datetime.datetime.today()
        # process request
        if settings.VERBOSE:
            print("            Guild Warehouse")
        for c in content.split(b'\\n')[1:]:
            tmp_code=c.split(b' ')[0]
            tmp=b' '.join(c.split(b' ')[1:]).split(b' x ')
            # recipe
            if tmp_code.startswith(b'r'):
                CACHE["guild"]["recipes"][tmp[0].decode()]=int(tmp[1])
            # part
            elif tmp_code.startswith(b'k'):
                CACHE["guild"]["parts"][tmp[0].decode()]=int(tmp[1])
            # resource
            else:
                CACHE[user.id]["resources"]["guild"][tmp[0].decode()]=int(tmp[1])
                CACHE["guild"]["resources"][tmp[0].decode()]=int(tmp[1])
    # reinforcement message
    elif content.split(b'\\n')[0].startswith(b'Materials needed for '):
        # validate the cache
        if (datetime.datetime.today()-CACHE[user.id]["resources"]["datetime"]).total_seconds()>delta:
            CACHE[user.id]["resources"]["guild"]={}
            CACHE[user.id]["resources"]["reinforcement"]={}
        CACHE[user.id]["resources"]["datetime"]=datetime.datetime.today()
        # process request
        if settings.VERBOSE:
            if b' reinforcement:' in content:
                print("            Materials needed for reinforcement")
            else:
                print("            Materials needed for repair")
        for c in content.split(b'\\n')[1:]:
            if b' x ' in c:
                tmp=c.split(b' x ')
                CACHE[user.id]["resources"]["reinforcement"][tmp[1].decode()]=int(tmp[0])
    # process reinforcement list
    if CACHE[user.id]["resources"]["guild"] and CACHE[user.id]["resources"]["reinforcement"]:
        if settings.VERBOSE:
            print("            ... PROCESS REINFORCEMENT")
        text=""
        resources=CACHE[user.id]["resources"]
        for (u_res, u_amount) in resources["reinforcement"].items():
            diff=u_amount-resources["guild"].get(u_res, 0)
            if diff>0:
                text+='\n{2} <a href="https://t.me/share/url?url=/g_deposit%20{2}%20{1}">{0}</a> x {1}'.format(u_res, diff, utils.item_by_name(u_res, "resources").get("code", "00"))
        CACHE[user.id]["resources"]["guild"]={}
        CACHE[user.id]["resources"]["reinforcement"]={}
        if text:
            context.bot.send_message(chat_id=cid, 
                                     text="Deposit for repair/reinforcement sponsored by guild:"+text,
                                     parse_mode=telegram.ParseMode.HTML,
                                     disable_web_page_preview=True)
        else:
            context.bot.send_message(chat_id=cid, 
                                     text="All resources are in the Guild Warehouse!",
                                     parse_mode=telegram.ParseMode.HTML,
                                     disable_web_page_preview=True)
    else:
        if settings.VERBOSE:
            print("            ... MISSING DATA")

def _action_crafting_list(cid, user, content, update, context):
    """
    Update crafting list
    """
    data={"parts": {}, "recipes": {}, "datetime": None}
    today=datetime.datetime.today().isoformat()
    for c in content.split(b'\\n'):
        tmp=c
        # check false positive messages
        if b':' in tmp:
            continue
        # recipe
        if c.startswith(b'\\U0001f4c3'):
            tmp=c.split(b'\\U0001f4c3')[1].split(b' /view_r')[0]
            tmp=tmp.split(b' (')
            if len(tmp)==2 and tmp[1].endswith(b')'):
                c_name=tmp[0].decode()
                c_amount=int(tmp[1][:-1])
                data["recipes"][c_name]=c_amount
                data["datetime"]=today
        # part
        else:
            tmp=c.split(b' (')
            if len(tmp)==2 and tmp[1].endswith(b')'):
                c_name=tmp[0].decode()
                c_amount=int(tmp[1][:-1])
                data["parts"][c_name]=c_amount
                data["datetime"]=today
    if data["datetime"]:
        user.crafting=json.dumps(data)
        if model.user_by_id(update.effective_user.id):
            status=model.update_user(user)
            if not status:
                utils._admin_error(context, "_action_crafting_list", user=user, error="update: False", trace=False)
        else:
            utils._admin_error(context, "_action_crafting_list", user=user, error="no registered user", trace=False)
        
def _action_roster(cid, user, content, update, context):
    """
    Show sleepy members
    """
    content=content.split(b'\\n')[1:]
    # chek UTC battle
    utcnow=datetime.datetime.utcnow()
    time_list=[]
    for t in settings.BATTLES:
        time_list.append((utcnow-datetime.datetime(year=utcnow.year,
                                                   month=utcnow.month,
                                                   day=utcnow.day,
                                                   hour=int(t[0:2]),
                                                   minute=int(t[3:5]))).total_seconds()/60.0)
    delta=int(model.get_data("BATTLE_TIME_DELTA_MINUTES", 20))
    time_list=[t>-delta and t<0 for t in time_list]
    print("            Roster", time_list, delta)
    # call to the battle
    if True in time_list:
        i=0
        tmp=""
        header=u'\U0001F4E2 Attention to the battle order\n'
        for player in content:
            if b' [\\u2694] ' not in player and b' [\\U0001f6e1] ' not in player:
                cw_name=b' '.join(player.split(b' ')[3:]).decode()
                user=model.user_by_cw_name(cw_name)
                if user:
                    tmp+="@{0} ".format(user.username)
                    i+=1
                if not i%3:
                    i=0
                    try:
                        if tmp:
                            context.bot.send_message(chat_id=cid, 
                                                     text=header+tmp,
                                                     parse_mode=telegram.ParseMode.HTML,
                                                     disable_web_page_preview=True)
                    except Exception as e:
                        utils._admin_error(context, "_action_roster: attention", user=user, error=str(e))
                    tmp=""
        if tmp:
            try:
                context.bot.send_message(chat_id=cid, 
                                         text=header+tmp,
                                         parse_mode=telegram.ParseMode.HTML,
                                         disable_web_page_preview=True)
            except Exception as e:
                utils._admin_error(context, "_action_roster: attention", user=user, error=str(e))

def _action_deposit(cid, user, content, update, context):
    """
    Modify amount of items after deposit
    """
    item=b' '.join(content.split(b' ')[2:-1]).decode()
    amount=int(content.split(b' ')[-1][1:-1])
    print("            Deposit: {0} x ({1})".format(item, amount))
    item=utils.item_by_name(item)
    if item:
        item_type=""
        if item["code"].startswith('r'):
            item_type="recipes"
        elif item["code"].startswith('k'):
            item_type="parts"
        # modify the crafting data
        if item_type:
            # guild warehouse
            if item["name"] in CACHE["guild"][item_type]:
                CACHE["guild"][item_type][item["name"]]+=amount
            else:
                CACHE["guild"][item_type][item["name"]]=amount
            # user
            u=model.user_by_id(update.effective_user.id)
            if u:
                crafting=json.loads(u.crafting)
                if crafting and len(crafting.keys()):
                    if item["name"] in crafting[item_type]:
                        crafting[item_type][item["name"]]-=amount
                        if crafting[item_type][item["name"]]<1:
                            del crafting[item_type][item["name"]]
                    # store data
                    user.crafting=json.dumps(crafting)
                    if model.user_by_id(update.effective_user.id):
                        status=model.update_user(user)
                        if not status:
                            utils._admin_error(context, "_action_deposit", user=user, error="update: False", trace=False)
                    else:
                        utils._admin_error(context, "_action_deposit", user=user, error="no registered user", trace=False)


# MAIN FUNCTION

def forwarded(update, context):
    """
    Main handler function for forwarded messages
    """
    global CACHE
    # process forward message from Chat Wars
    if update.message.forward_from and update.message.forward_from.id==settings.CW_BOT_ID:
        if settings.VERBOSE:
            print("[Forwarded] from Chat Wars")
        cid=update.message.chat.id
        # telegram user
        user=model.User(id=update.effective_user.id,
                        username=update.effective_user.username,
                        full_name=update.effective_user.full_name,
                        link=update.effective_user.link,
                        is_bot=update.effective_user.is_bot)
        # create cache
        CACHE.setdefault(user.id, {"resources": {"guild": {}, 
                                                 "reinforcement": {},
                                                 "datetime": datetime.datetime.today()}})
        CACHE.setdefault("guild", {"resources": {},
                                   "parts": {},
                                   "recipes": {}})
        # escape content
        content=update.message.text.encode(encoding="unicode_escape")
        
        # hostile creatures
        if b'You met some hostile creatures. Be careful:' in content and b'/fight_' in content:
            _action_fight(cid, user, content, update, context)
            return
        
        # battle report
        if settings.GUILD_NAME in content and b' Lvl: ' in content and b'Your result on the battlefield' in content:
            _action_battle_report(cid, user, content, update, context)
            return
        
        # materials needed for reinforcement (blacksmith's store message)
        if content.split(b'\\n')[0].startswith(b'Materials needed for '):
            _action_reinforcement(cid, user, content, update, context)
            return
        
        # guild warehouse
        if content.split(b'\\n')[0]==b'Guild Warehouse:':
            _action_reinforcement(cid, user, content, update, context)
            return
            
        # guild roster
        if content.split(b'\\n')[0].startswith(settings.GUILD_NAME[:10]) and content.split(b'\\n')[-1].startswith(b'#'):
            _action_roster(cid, user, content, update, context)
            return
            
        # guild deposit
        if content.startswith(b'Deposited successfully: '):
            _action_deposit(cid, user, content, update, context)
            return
            
        # parts and recipes
        _action_crafting_list(cid, user, content, update, context)
        