from asyncio import get_running_loop, sleep
from time import time
from pyrogram import filters
from pyrogram.types import CallbackQuery,ChatPermissions,InlineKeyboardButton,InlineKeyboardMarkup,Message

from ..bot import app,db
from .admin import list_admins, member_permissions,adminsOnly

flooddb = db.flood

async def is_flood_on(chat_id: int) -> bool:
    chat = await flooddb.find_one({"chat_id": chat_id})
    if not chat:
        return True
    return False

async def flood_on(chat_id: int):
    is_flood = await is_flood_on(chat_id)
    if is_flood:
        return
    return await flooddb.delete_one({"chat_id": chat_id})

async def flood_off(chat_id: int):
    is_flood = await is_flood_on(chat_id)
    if not is_flood:
        return
    return await flooddb.insert_one({"chat_id": chat_id})

DB = {}  

def reset_flood(chat_id, user_id=0):
    for user in DB[chat_id].keys():
        if user != user_id:
            DB[chat_id][user] = 0

@app.on_message(~filters.service & ~filters.me & ~filters.private & ~filters.channel & ~filters.bot,group=2,)
async def flood_handler(_, message: Message):
    if not message.chat:
        return
    chat_id = message.chat.id
    if not (await is_flood_on(chat_id)):
        return
    if chat_id not in DB:
        DB[chat_id] = {}
    if not message.from_user:
        reset_flood(chat_id)
        return
    user_id = message.from_user.id
    mention = message.from_user.mention
    if user_id not in DB[chat_id]:
        DB[chat_id][user_id] = 0
    reset_flood(chat_id, user_id)
    mods = await list_admins(chat_id)
    if user_id in mods:
        return
    if DB[chat_id][user_id] >= 10:
        DB[chat_id][user_id] = 0
        try:
            await message.chat.restrict_member(
                user_id,
                permissions=ChatPermissions(),
                until_date=int(time() + 3600),
            )
        except Exception:
            return
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="Unmute 🔊",callback_data=f"unmute_{user_id}")]])
        m = await message.reply_text(f"Imagine flooding the chat in front of me, Muted {mention} for an hour!",reply_markup=keyboard)
        async def delete():
            await sleep(3600)
            try:
                await m.delete()
            except Exception:
                pass
        loop = get_running_loop()
        return loop.create_task(delete())
    DB[chat_id][user_id] += 1


@app.on_callback_query(filters.regex("unmute_"))
async def flood_callback_func(_, cq: CallbackQuery):
    from_user = cq.from_user
    permissions = await member_permissions(cq.message.chat.id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            "You don't have enough permissions to perform this action.\n"
            + f"Permission needed: {permission}",
            show_alert=True,
        )
    user_id = cq.data.split("_")[1]
    if user_id == "all":
        # Chat members can only send text messages and media messages
        await app.set_chat_permissions(
            cq.message.chat.id,
            ChatPermissions(
                    can_send_messages = True,
                    can_send_media_messages = True,
                    can_send_other_messages = True,
                    can_send_polls = True,
                    can_invite_users = True,
                    can_pin_messages = True))
        text = cq.message.text.markdown
        text = f"~~{text}~~\n\n"
        text += f"__Unmuted all by {from_user.mention}__"
        await cq.message.edit(text)
        return

    await cq.message.chat.unban_member(user_id)
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += f"__User unmuted by {from_user.mention}__"
    await cq.message.edit(text)

@app.on_message(filters.command("flood") & ~filters.private)
@adminsOnly("can_change_info")
async def flood_Boolean(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: /flood [on|off]")
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status == "on":
        await flood_on(chat_id)
        await message.reply_text("Enabled Flood Checker.")
    elif status == "off":
        await flood_off(chat_id)
        await message.reply_text("Disabled Flood Checker.")
    else:
        await message.reply_text("Unknown Suffix, Use /flood [on|off]")