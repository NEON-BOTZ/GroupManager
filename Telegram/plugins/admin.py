from contextlib import suppress
from time import time
from ..bot import app
from ..Config import config
from .function import extract_user_and_reason,time_converter
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import ChatPermissions, Message, InlineKeyboardMarkup, InlineKeyboardButton
from functools import wraps
from traceback import format_exc as err
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from pyrogram.types import Message
from pyrogram.enums import ChatType
from pyrogram.types import ChatPermissions

async def authorised(func, subFunc2, client, message, *args, **kwargs):
    chatID = message.chat.id
    try:
        await func(client, message, *args, **kwargs)
    except ChatWriteForbidden:
        print("ChatWriteForbidden Error on ",chatID)
    except Exception as e:
        try:
            await message.reply_text(str(e.MESSAGE))
        except AttributeError:
            await message.reply_text(str(e))
        e = err()
        print(str(e))
    return subFunc2

async def unauthorised(message: Message, permission, subFunc2):
    chatID = message.chat.id
    text = (
        "🤷‍♂️ You don't have the required permission to perform this action."
        + f"\n🔐 **Permission:** __{permission}__"
    )
    try:
        await message.reply_text(text)
    except ChatWriteForbidden:
        print("ChatWriteForbidden Error on ",chatID)
    return subFunc2

def adminsOnly(permission):
    def subFunc(func):
        @wraps(func)
        async def subFunc2(client, message: Message, *args, **kwargs):
            chatID = message.chat.id
            if not message.from_user:
                # For anonymous admins
                if message.sender_chat and message.sender_chat.id == message.chat.id:
                    return await authorised(
                        func,
                        subFunc2,
                        client,
                        message,
                        *args,
                        **kwargs,
                    )
                return await unauthorised(message, permission, subFunc2)
            # For admins 
            userID = message.from_user.id
            permissions = await member_permissions(chatID, userID)
            if permission not in permissions:
                return await unauthorised(message, permission, subFunc2)
            return await authorised(func, subFunc2, client, message, *args, **kwargs)

        return subFunc2

    return subFunc

async def member_permissions(chat_id: int, user_id: int):
    perms = []
    try:
        member = (await app.get_chat_member(chat_id, user_id)).privileges
    except Exception:
        return []
    if member.can_post_messages:
        perms.append("can_post_messages")
    if member.can_edit_messages:
        perms.append("can_edit_messages")
    if member.can_delete_messages:
        perms.append("can_delete_messages")
    if member.can_restrict_members:
        perms.append("can_restrict_members")
    if member.can_promote_members:
        perms.append("can_promote_members")
    if member.can_change_info:
        perms.append("can_change_info")
    if member.can_invite_users:
        perms.append("can_invite_users")
    if member.can_pin_messages:
        perms.append("can_pin_messages")
    if member.can_manage_video_chats:
        perms.append("can_manage_video_chats")
    return perms
help_text = """
/ban - Ban A User
/dban - Delete the replied message banning its sender
/tban - Ban A User For Specific Time

/mute - Mute A User
/tmute - Mute A User For Specific Time

/blacklisted - Get All The Blacklisted Words In The Chat.
/blacklist [WORD|SENTENCE] - Blacklist A Word Or A Sentence.
/whitelist [WORD|SENTENCE] - Whitelist A Word Or A Sentence.

/flood [on|off] - Turn flood(spam) detection on or off

/filters To Get All The Filters In The Chat.
/filter [FILTER_NAME] To Save A Filter (Can be a sticker or text).
/stop [FILTER_NAME] To Stop A Filter.

/setwelcome - Reply this to a message containing correct
format for a welcome message.
/delwelcome - Delete the welcome message.
/getwelcome - Get the welcome message.

"""
@app.on_message(filters.command("help"))
async def help_handler(_, message):
    user_id = message.from_user.id
    if message.chat.type == ChatType.PRIVATE:
        await app.send_message(chat_id = message.from_user.id,text = help_text)
        return
    else:
        if not user_id in (await list_admins(message.chat.id)):
            await app.send_message(chat_id = message.chat.id,text = "🤷‍♂️ You don't have the required permission to perform this action.")
        try:
            await app.send_message(chat_id = user_id,text = help_text)
        except:
            await app.send_message(chat_id = message.chat.id,text = "PM Me For More Details")

admins_in_chat = {}

async def list_admins(chat_id: int):
    global admins_in_chat
    admins_in_chat[chat_id] = {
        "last_updated_at": time(),
        "data": [
            member.user.id
            async for member in app.get_chat_members(
                chat_id, filter=ChatMembersFilter.ADMINISTRATORS
            )
        ],
    }
    if chat_id in admins_in_chat:
        interval = time() - admins_in_chat[chat_id]["last_updated_at"]
        if interval < 3600:
            return admins_in_chat[chat_id]["data"]

    return admins_in_chat[chat_id]["data"]

@app.on_message(filters.command(["ban", "dban", "tban"]) & ~filters.private)
@adminsOnly("can_restrict_members")
async def ban_handler(_, message: Message):
    user_id, reason = await extract_user_and_reason(message, sender_chat=True)
    if not user_id:
        return await message.reply_text("I can't find that user.")
    if user_id == config.BOT_ID:
        return await message.reply_text("I can't ban myself.")
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text("I can't ban an admin")
    try:
        mention = (await app.get_users(user_id)).mention
    except IndexError:
        mention = (
            message.reply_to_message.sender_chat.title
            if message.reply_to_message
            else "Anon"
        )
    msg = (
        f"**Banned User:** {mention}\n"
        f"**Banned By:** {message.from_user.mention if message.from_user else 'Anon'}\n"
    )
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    if message.command[0] == "tban":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_ban = await time_converter(message, time_value)
        msg += f"**Banned For:** {time_value}\n"
        if temp_reason:
            msg += f"**Reason:** {temp_reason}"
        with suppress(AttributeError):
            if len(time_value[:-1]) < 3:
                await message.chat.ban_member(user_id, until_date=temp_ban)
                await message.reply_text(msg)
            else:
                await message.reply_text("You can't use more than 99")
        return
    if reason:
        msg += f"**Reason:** {reason}"
    await message.chat.ban_member(user_id)
    await message.reply_text(msg)


@app.on_message(filters.command("unmute") & ~filters.private)
@adminsOnly("can_restrict_members")
async def unmute_handler(_, message: Message):
    prompt = message.text.split(None, 1)[1].strip()
    if prompt == "all":
        await app.set_chat_permissions(
            message.chat.id,
            ChatPermissions(
                    can_send_messages = True,
                    can_send_media_messages = True,
                    can_send_other_messages = True,
                    can_send_polls = True,
                    can_invite_users = True,
                    can_pin_messages = True,

    ))
        return await message.reply_text("All users unmuted",)
    
@app.on_message(filters.command(["mute", "tmute"]) & ~filters.private)
@adminsOnly("can_restrict_members")
async def mute_handler(_, message: Message):
    prompt = message.text.split(None, 1)[1].strip()
    if prompt == "all":
        # Completely restrict chat
        callback_button = InlineKeyboardButton(f"Unmute All", callback_data=f"unmute_all")  
        keyboard = InlineKeyboardMarkup([[callback_button]])
        await app.set_chat_permissions(message.chat.id, ChatPermissions())
        return await message.reply_text("All users muted",reply_markup=keyboard)
    
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("I can't find that user.")
    if user_id == config.BOT_ID:
        return await message.reply_text("I can't mute myself.")
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text("I can't mute an admin.")
    mention = (await app.get_users(user_id)).mention
    callback_button = InlineKeyboardButton(f"Unmute 🔊", callback_data=f"unmute_{user_id}")  
    keyboard = InlineKeyboardMarkup([[callback_button]])
    msg = (
        f"**Muted User:** {mention}\n"
        f"**Muted By:** {message.from_user.mention if message.from_user else 'Anon'}\n"
    )
    if message.command[0] == "tmute":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_mute = await time_converter(message, time_value)
        msg += f"**Muted For:** {time_value}\n"
        if temp_reason:
            msg += f"**Reason:** {temp_reason}"
        try:
            if len(time_value[:-1]) < 3:
                await message.chat.restrict_member(user_id,permissions=ChatPermissions(),until_date=temp_mute,)
                await message.reply_text(msg, reply_markup=keyboard)
            else:
                await message.reply_text("You can't use more than 99")
        except AttributeError:
            pass
        return
    if reason:
        msg += f"**Reason:** {reason}"
    await message.chat.restrict_member(user_id, permissions=ChatPermissions())
    await message.reply_text(msg, reply_markup=keyboard)
