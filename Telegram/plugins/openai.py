import openai
import os
import time
from ..Config import config
from ..bot import app
from pyrogram import filters
from gtts import gTTS
from pyrogram.types import InputMediaPhoto
from pyrogram import enums

openai.api_key = config.OPEN_AI_KEY

def generate_image(prompt):
    response = openai.Image.create(prompt=prompt,model="image-alpha-001",size="1024x1024")
    return response

@app.on_message(filters.command("ask"))
async def ask_command_handler(_,message):

    if len(message.command) < 2:
        await app.send_message(
            chat_id = message.chat.id,
            text = "Please end your command with a dot (.) or question mark (?)")
        return 
        
    # Check if the prompt ends with a dot or question mark
    if not message.text.endswith(".") and not message.text.endswith("?"):
        await message.reply_text("Please end your command with a dot (.) or question mark (?)")
        return
    
    prompt = message.text.split(None, 1)[1].strip()
    
    # Use ChatGPT to generate a response
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        temperature=0.1,
    ).choices[0].text

    link1 = '<a href="https://t.me/attackonshiba">Join ATOS</a>'
    link2 = '<a href="https://www.dextools.io/app/en/ether/pair-explorer/0x8a6fc18e27338876810e1770f9158a1a271f90abchart">Chart</a>'
    link3 = '<a href="https://app.uniswap.org/#/swap?outputCurrency=0xf0a3a52eef1ebe77bb2743f53035b5813afe721f">Buy ATOS</a>'
    links = f"{link1} | {link2} | {link3}"
    response_with_links = f"{response}\n\n{links}"
    await app.send_chat_action(
            chat_id = message.chat.id,
            action = enums.ChatAction.TYPING)
    # Send the response to the user
    await message.reply_text(response_with_links,disable_web_page_preview=True)

@app.on_message(filters.command("speech"))
async def voice_command_handler(_,message):

    # Get the text to speak from the command arguments
    text = message.text.split(None, 1)[1].strip()

    # Generate the audio file
    audio = gTTS(text=text, lang='ja')

    # Send the audio file to the user
    first_name = message.from_user.first_name
    username = message.from_user.username
    file_name = f"{first_name}.mp3"
    audio.save(file_name)
    with open(file_name, 'rb') as f:
        link1 = '<a href="https://t.me/attackonshiba">Join ATOS</a>'
        link2 = '<a href="https://www.dextools.io/app/en/ether/pair-explorer/0x8a6fc18e27338876810e1770f9158a1a271f90abchart">Chart</a>'
        link3 = '<a href="https://app.uniswap.org/#/swap?outputCurrency=0xf0a3a52eef1ebe77bb2743f53035b5813afe721f">Buy ATOS</a>'
        links = f"\n\n{link1} | {link2} | {link3}"
        caption_with_links = f"You can also do this by typing /speech command\n\n@{username} generated this voice{links}"
        await app.send_chat_action(
            chat_id = message.chat.id,
            action = enums.ChatAction.RECORD_AUDIO)
        await app.send_voice(chat_id=message.chat.id, voice=f, caption=caption_with_links)
    
    os.remove(file_name)
        
@app.on_message(filters.command("commands"))
async def command_handler(_,m):
    link1 = '<a href="https://t.me/attackonshiba">Join ATOS</a>'
    link2 = '<a href="https://www.dextools.io/app/en/ether/pair-explorer/0x8a6fc18e27338876810e1770f9158a1a271f90abchart">Chart</a>'
    link3 = '<a href="https://app.uniswap.org/#/swap?outputCurrency=0xf0a3a52eef1ebe77bb2743f53035b5813afe721f">Buy ATOS</a>'
    links = f"{link1} | {link2} | {link3}"

    message = "Available commands:\n\n"
    message += "/ask - Ask Jimmy a question.\n"
    message += "/img - Tell Jimmy to Create an image\n"
    message += "/speech - Write a text to make it into Japanese Voice\n"
    message += "/commands - Show available commands\n"

    # Send the response to the user
    await m.reply_text(message + f"\n\n{links}",disable_web_page_preview=True)

user_time = {}

@app.on_message(filters.command("img"))
async def img_command_handler(_,message):
    global user_time
    now = time.time()
    user_id = message.from_user.id
    if user_id  in user_time:
        last_call = user_time[message.from_user.id]["last_updated_at"]
        if now - last_call < 90:
            remaining_time = 90 - (now - last_call)
            message = await message.reply_text(f"You can use the `/img` command again in {int(remaining_time)} seconds. \n\nThis is to prevent spam and abuse of the bot.")
            while True:
                time.sleep(10)
                remaining_time -= 10
                if remaining_time <= 0:
                    username = user_time[message.from_user.id]["username"]
                    await app.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=message.id,
                        text=f"You can now use /img again. @{username}")
                    break
                else:
                    await app.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message.id,
                    text=f"You can use the `/img` command again in {int(remaining_time)} seconds.\n\nThis is to prevent spam and abuse of the bot."
                )
            return
    user_time[message.from_user.id] = {
        "last_updated_at": now,
        "username": message.from_user.username
    }
    prompt = message.text.split(None, 1)[1].strip()

    try:
        response = generate_image(prompt)

        link1 = '<a href="https://t.me/attackonshiba">Join ATOS</a>'
        link2 = '<a href="https://www.dextools.io/app/en/ether/pair-explorer/0x8a6fc18e27338876810e1770f9158a1a271f90abchart">Chart</a>'
        link3 = '<a href="https://app.uniswap.org/#/swap?outputCurrency=0xf0a3a52eef1ebe77bb2743f53035b5813afe721f">Buy ATOS</a>'
        links = f"\n\n{link1} | {link2} | {link3}"
        caption = f"Hello @{message.from_user.username}.\n\nYou can generate again in 1:30 Minutes{links}"

        input_media = InputMediaPhoto(
            media=response.data[0].url,
            caption=caption,
        )

        await message.reply_media_group([input_media])

    except openai.error.InvalidRequestError as e:
        await message.reply_text(str(e)) 
        print("Error:", str(e))