from ..bot import app,db
from pyrogram import filters
from ..Config import config

chatsdb = db.chats
noadsdb = db.chats

@app.on_message(filters.command("status") & filters.user(config.DEV))
async def status_handler(_, message):
    chat = message.chat.id
    count = await chatsdb.count_documents({})
    await app.send_message(chat_id = chat,text = f"Total chats count is : {count}")

@app.on_message(filters.command("add") & filters.user(config.DEV))
async def status_handler(_, message):
    chat = message.chat.id
    prompt = message.text.split(None, 1)[1].strip()
    chat = await noadsdb.find_one({"chat_id": message.chat.id})
    if not chat:
            await noadsdb.insert_one({"chat_id": message.chat.id})
    await app.send_message(chat_id = chat,text = f"This chat will no longer display our ads")

@app.on_message(filters.command("ads") & filters.user(config.DEV))
async def ads_handler(_, message):
    if not message.reply_to_message:
        await message.reply_text("Please reply to ad message")
        return
    raw_text = message.reply_to_message_id 
    sent = 0
    async for chat in chatsdb.find({"chat_id": {"$lt": 0}}):
        try:
            async for add in noadsdb.find({"chat_id": {"$lt": 0}}):
                if chat["chat_id"] == add["chat_id"]:
                    continue
                await app.copy_message(chat_id=chat["chat_id"],from_chat_id=message.chat.id,message_id=raw_text)
                sent += 1
        except:
            pass
    await message.reply_text(f"Broadcast completed with {sent} chats")