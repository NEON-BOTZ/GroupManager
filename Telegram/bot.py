from pyrogram import Client,filters
from .Config import config
from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

print("Initializing MongoDB client")
mongo_client = MongoClient(config.MONGO_URL)
db = mongo_client.groupmanager
app = Client("Client",api_id = config.API_ID,api_hash = config.API_HASH,bot_token = config.BOT_TOKEN,plugins={"root": "Telegram/plugins"})
BOT_USERNAME = 


START_BTNS = InlineKeyboardMarkup(
    [
        InlineKeyboardButton(text="help", url="https://t.me/{BOT_USERNAME}?start=help_")
        ]
    )

@app.on_message(filters.command("start"))
async def start_handler(_, message):
    await app.send_message(
        chat_id = message.chat.id,
        text = "Hey there! I'm here to help you manage your groups! Hit /help to find out more about how to use me to my full potential.",
        reply_markup=START_BTNS
        )
