from pyrogram import Client,filters
from .Config import config
from .plugins import ALL_MODULES
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

print("Initializing MongoDB client")
mongo_client = MongoClient(config.MONGO_URL)
db = mongo_client.groupmanager
HELPMENU = {}
app = Client("Client",api_id = config.API_ID,api_hash = config.API_HASH,bot_token = config.BOT_TOKEN,plugins={"root": "Telegram/plugins"})

@app.on_message(filters.command("start"))
async def start_handler(_, message):
    await app.send_message(
        chat_id = message.chat.id,
        text = "Hey there! I'm here to help you manage your groups! Hit /help to find out more about how to use me to my full potential.")

async def start_bot():
    global HELPMENU

    for module in ALL_MODULES:
        imported_module = importlib.import_module("wbb.modules." + module)
        if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
            imported_module.__MODULE__ = imported_module.__MODULE__
            if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
                HELPMENU[
                    imported_module.__MODULE__.replace(" ", "_").lower()
                ] = imported_module
    bot_modules = ""
    j = 1
    for i in ALL_MODULES:
        if j == 4:
            bot_modules += "|{:<15}|\n".format(i)
            j = 0
        else:
            bot_modules += "|{:<15}".format(i)
        j += 1
