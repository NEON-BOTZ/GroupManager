import asyncio
import os
from datetime import datetime
from random import shuffle
from telegraph import upload_file
from pyrogram import filters
from pyrogram.types import Chat,Message
from ..bot import app,db
from .admin import adminsOnly
from .function import ikb,extract_text_and_keyb
from ..Config import config

welcomedb = db.welcome_text
chatsdb = db.chats

async def get_welcome(chat_id: int) -> str:
    text = await welcomedb.find_one({"chat_id": chat_id})
    if not text:
        return ""
    return text

async def set_welcome(chat_id: int, text: str,type:str,media:str):
    return await welcomedb.update_one(
        {"chat_id": chat_id}, {"$set": {"text": text, "type":type, "media":media}}, upsert=True
    )

async def del_welcome(chat_id: int):
    return await welcomedb.delete_one({"chat_id": chat_id})

@app.on_message(filters.new_chat_members, group=5)
async def welcome(_, message: Message):
    for member in message.new_chat_members:
        chat = await chatsdb.find_one({"chat_id": message.chat.id})
        if not chat:
            await chatsdb.insert_one({"chat_id": message.chat.id})
        await send_welcome_message(message.chat, member.id, True)


async def send_welcome_message(chat: Chat, user_id: int, delete: bool = False):
    data = await get_welcome(chat.id)
    if not data:
        return
    raw_text = data["text"]
    type = data["type"]
    media = data["media"]
    try:
        text, keyb = extract_text_and_keyb(ikb, raw_text)
        if "{chat}" in text:
            text = text.replace("{chat}", chat.title)
        if "{name}" in text:
            text = text.replace("{name}", (await app.get_users(user_id)).mention)
        async def _send_wait_delete():
            if type == "text":
                m = await app.send_message(chat.id,text=text,reply_markup=keyb,disable_web_page_preview=True)
            if type == "photo":
                m = await app.send_photo(chat.id,photo = media,caption=text,reply_markup=keyb)
            if type == "video":
                m = await app.send_video(chat.id,video = media,caption=text,reply_markup=keyb)
            await asyncio.sleep(300)
            await m.delete()
    except:
        if "{chat}" in raw_text:
            raw_text = raw_text.replace("{chat}", chat.title)
        if "{name}" in raw_text:
            raw_text = raw_text.replace("{name}", (await app.get_users(user_id)).mention)
        async def _send_wait_delete():
            if type == "text":
                m = await app.send_message(chat.id,text=raw_text,disable_web_page_preview=True)
            if type == "photo":
                m = await app.send_photo(chat.id,photo = media,caption=raw_text)
            if type == "video":
                m = await app.send_video(chat.id,video = media,caption=raw_text)
            await asyncio.sleep(300)
            await m.delete()
    asyncio.create_task(_send_wait_delete())


@app.on_message(filters.command("setwelcome") & ~filters.private)
@adminsOnly("can_change_info")
async def setwelcome_handler(_, message):
    chat_id = message.chat.id
    usage = "You need to reply to a text, check the Greetings module in /help"
    if not message.reply_to_message:
        await message.reply_text(usage)
        return
    
    if message.reply_to_message.photo:
        if not message.reply_to_message.caption:
            return await message.reply_text("Where is caption text ?")
        raw_text = message.reply_to_message.caption.markdown
        if "~" in raw_text.lower():
            if not (extract_text_and_keyb(ikb, raw_text)):
                return await message.reply_text("Wrong formating, check help section.")
            path = (f"./DOWNLOADS/{chat_id}.mp4")
            path = await app.download_media(message=message.reply_to_message.photo, file_name=path)
            tlink = upload_file(path)

            await set_welcome(chat_id, raw_text,type="photo",media = f"https://telegra.ph{tlink[0]}")
            os.remove(path)  
            await message.reply_text("Welcome message has been successfully set.")
        else:
            path = (f"./DOWNLOADS/{chat_id}.mp4")
            path = await app.download_media(message=message.reply_to_message.photo, file_name=path)
            tlink = upload_file(path)

            await set_welcome(chat_id, raw_text,type="photo",media = f"https://telegra.ph{tlink[0]}")
            os.remove(path)  
            await message.reply_text("Welcome message has been successfully set.")
        
    if message.reply_to_message.animation:
        if not message.reply_to_message.caption:
            return await message.reply_text("Where is caption text ?")
        raw_text = message.reply_to_message.caption.markdown
        if "~" in raw_text.lower():
            if not (extract_text_and_keyb(ikb, raw_text)):
                return await message.reply_text("Wrong formating, check help section.")
            path = (f"./DOWNLOADS/{chat_id}.mp4")
            path = await app.download_media(message=message.reply_to_message.animation, file_name=path)
            tlink = upload_file(path)

            await set_welcome(chat_id, raw_text,type="video",media = f"https://telegra.ph{tlink[0]}")
            os.remove(path)  
            await message.reply_text("Welcome message has been successfully set.")
        else:
            path = (f"./DOWNLOADS/{chat_id}.mp4")
            path = await app.download_media(message=message.reply_to_message.animation, file_name=path)
            tlink = upload_file(path)

            await set_welcome(chat_id, raw_text,type="video",media = f"https://telegra.ph{tlink[0]}")
            os.remove(path)  
            await message.reply_text("Welcome message has been successfully set.")

    if message.reply_to_message.video:
        if not message.reply_to_message.caption:
            return await message.reply_text("Where is caption text ?")
        raw_text = message.reply_to_message.caption.markdown
        if "~" in raw_text.lower():
            if not (extract_text_and_keyb(ikb, raw_text)):
                return await message.reply_text("Wrong formating, check help section.")
            path = (f"./DOWNLOADS/{chat_id}.mp4")
            path = await app.download_media(message=message.reply_to_message.video, file_name=path)
            tlink = upload_file(path)

            await set_welcome(chat_id, raw_text,type="video",media = f"https://telegra.ph{tlink[0]}")
            os.remove(path)  
            await message.reply_text("Welcome message has been successfully set.")
        else:
            path = (f"./DOWNLOADS/{chat_id}.mp4")
            path = await app.download_media(message=message.reply_to_message.video, file_name=path)
            tlink = upload_file(path)

            await set_welcome(chat_id, raw_text,type="video",media = f"https://telegra.ph{tlink[0]}")
            os.remove(path)  
            await message.reply_text("Welcome message has been successfully set.")

    if message.reply_to_message.text:
        raw_text = message.reply_to_message.text.markdown
        if "~" in raw_text.lower():
            if not (extract_text_and_keyb(ikb, raw_text)):
                return await message.reply_text("Wrong formating, check help section.")
            await set_welcome(chat_id, raw_text,type="text",media = f"no media")
            await message.reply_text("Welcome message has been successfully set.")
        else:
            await set_welcome(chat_id, raw_text,type="text",media = f"no media")
            await message.reply_text("Welcome message has been successfully set.")


@app.on_message(filters.command("delwelcome") & ~filters.private)
@adminsOnly("can_change_info")
async def delwelcome_handler(_, message):
    chat_id = message.chat.id
    await del_welcome(chat_id)
    await message.reply_text("Welcome message has been deleted.")

@app.on_message(filters.command("getwelcome") & ~filters.private)
@adminsOnly("can_change_info")
async def getwelcome_handler(_, message):
    chat = message.chat
    welcome = await get_welcome(chat.id)
    if not welcome:
        return await message.reply_text("No welcome message set.")
    if not message.from_user:
        return await message.reply_text("You're anon, can't send welcome message.")
    await send_welcome_message(chat, message.from_user.id)

