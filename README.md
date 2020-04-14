# Guild helper bot for ChatWars (Tested on ChatWars v2)

* Free of backdoors and spying code!
* Subscribe (Watch > Releases only / Watching) to keep updated with new features and changes

I love this code. **Do you like it?**
> Do [small actions](https://secure.xsolla.com/paystation2/?access_token=b1ogMalfXDjI7YGg3IYC41fvfDSC99Gx) **x** support this code!

## Features

**Generate ready to craft list or full crafting list for the guild** with a simple command /craft. In order to use this feature the collectors (and others) must forward they crafting list from ChatWars to the guild chat or to this bot. Also someone should forward the recipes  (/g_stock_rec) and parts (/g_stock_parts) of the guild

* List all owners of the crafting data
* Generate the “easy to deposit” links for crafting data 
* Notify outdated crafting data to the respective owner\*
* Track crafting data deposition 
* Reset all crafting data (/craft_reset)

**Call members (according their level) for help on fights, ambushes or to defeat hostile creatures or the Champion**, just forwarding the ChatWars fight message

**Generate the “easy to deposit” missing resources list for repair/reinforce equipment sponsored by guild**, just forwarding the blacksmith's requirement list and the resource list of the guild (/g_stock_res)

**Call to sleepy members to attend the battle orders**, just forwarding the guild's Roster a configurable amount of minutes (default: 20 minutes) before each battle\*

**Pin a message on the guild chat** (even if you are not administrator of the group) with a simple command /pin

**Mention all stronger members** of the guild with a simple command /elite 

**Mention all members of the guild** with a simple command /everybody

Note: It is necessary forward the battle report (/report) to the guild chat or to the bot in order to keep updated  the info of the members on database or to include a new member in guild



## Instructions

### I) Project dependencies
Clone or download the project and install the necessary libraries from `Python Command Line` 

```
$ python -m pip install python-telegram-bot SQLAlchemy
```

or with `pip` tool
```
$ pip install python-telegram-bot SQLAlchemy
```

### II) Create a new bot with BotFather

1. Open [@BotFather](https://telegram.me/BotFather) and create a new bot with the command /newbot
2. Choose a name for the bot
3. Choose an username for the bot (Like *NameBot* or *name_bot*) 
4. Save the generated **access token** and replace the current value of the variable **TOKEN** in settings.py (on the root project folder). See below...
5. Edit the bot, with [@BotFather](https://telegram.me/BotFather), with the command /mybots. Choose the current bot and press the inline button *Edit Commands* (Edit Bot > Edit Commands). Then, copy and paste or write the next commands:
```
    pin - pin a message in the chat
    elite - mention stronger members
    everybody - mention everyone
    craft - generate the crafting list
    craft_reset - clear crafting data
```
6. Optionally set the other info like About, Description, etc.

###  III) Modify the settings.py (on the root project folder)

Edit the next variables:

**ADMIN_ID**: [str] Telegram unique identifier for an administrator. The administrator can be any member of the guild (like "123456789")

**ADMIN_CONTACT**: [str] Telegram username of the administrator (like "@admin")

**TOKEN**: [str] Access token of the bot generated with [@BotFather](https://telegram.me/BotFather) (like "123456789:ABCDEFGH12345678jklmnopq")

**GUILD_NAME**: [bytes] Short name of the guild with the castle emoji as prefix, encoded to bytes. See the list of castle emojis encoded to bytes below (like b"\\U0001f954[ABC]")

* b"\\U0001F954" - Potato Castle
* b"\\U0001F985" - Highnest Castle
* b"\\U0001F98C" - Deerhorn Castle
* b"\\U0001F43A" - Wolfpack Castle
* b"\\U0001F311" - Moonlight Castle
* b"\\U0001F988" - Sharkteeth Castle
* b"\\U0001F409" - Dragonscale Castle

Modify the next variables if you are connected to internet through a proxy server

**PROXY**: [bool] True if you are connected through a proxy

**PROXY_TYPE**: [str] Type of proxy (like "http://")

**PROXY_URL**: [str] Url of the proxy (like "proxy.com:3128")

**PROXY_AUTH**: [str] Autentication if is required (like "username:password")

### IV) Hosting the code (optional)

An internet connection is necessary in order to run the code of the bot. But, if you want to make it persistent maybe you will need a hosting. You can use [PythonAnywhere](https://www.pythonanywhere.com), [Heroku](https://www.heroku.com/) or another hosting service for that purpose...

### V) Run the code

To run the code just execute the next line on the root project folder... and enjoy

```
$ python bot.py
```

## Advanced features for the administrator of the bot

\*There are a lot of advanced features that are only configurable by administrator (like edit, delete or list all registered users, edit bot's variables for manage some features, etc.). If you want to use this (free of charge), please contact me through Telegram [@Toni_SM](https://telegram.me/Toni_SM)
