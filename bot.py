import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import FSInputFile

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"media": [], "users": []}, f, indent=4)


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ────────────────────────────────────────────────
# /start
# ────────────────────────────────────────────────

@dp.message(Command("start"))
async def start(msg: types.Message):
    data = load_data()

    # Save user
    if msg.from_user.id not in data["users"]:
        data["users"].append(msg.from_user.id)
        save_data(data)

    # FIRST PHOTO + CLICKABLE CAPTION
    photo_path = "start_photo.jpg"  # <---- apni photo ka filename yaha rakho
    if os.path.exists(photo_path):

        caption = (
            "▶️➡️ [𝘾𝙇𝙄𝘾𝙆 𝙃𝙀𝙍𝙀 𝙏𝙊 𝙒𝘼𝙏𝘾𝙃 𝘿𝙀𝙈𝙊 𝙋𝙍𝙊𝙊𝙁](https://your-link.com)\n\n"
            "😬 INTERESTED TO BUY VIDEOS ❓❓\n\n"
            "𝗔𝗻𝘆 𝗜𝘀𝘀𝘂𝗲, 𝗗𝗼𝘂𝗯𝘁 𝗼𝗿 𝗤𝘂𝗲𝘀𝘁𝗶𝗼𝗻 𝗙𝗲𝗲𝗹 𝗙𝗿𝗲𝗲 𝗧𝗼 𝗔𝘀𝗸 😬\n"
            "𝗛𝘆 𝗛𝘆𝗹𝗼 𝗯𝗿𝗼𝗼 𝙒𝙖𝙣𝙣𝙖 𝘽𝙪𝙮 𝙑𝙞𝙙𝙚𝙤𝙨 ???"
        )

        await msg.answer_photo(
            photo=FSInputFile(photo_path),
            caption=caption,
            parse_mode=ParseMode.MARKDOWN
        )

    # SEND SAVED MESSAGES
    for m in data["media"]:
        if m["type"] == "text":
            await msg.answer(m["data"])
        elif m["type"] == "photo":
            await msg.answer_photo(FSInputFile(m["data"]))
        elif m["type"] == "video":
            await msg.answer_video(FSInputFile(m["data"]))


# ────────────────────────────────────────────────
# /add (Admin only)
# ────────────────────────────────────────────────

@dp.message(Command("add"))
async def add_cmd(msg: types.Message):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply("⛔ Only admin can use this!")

    await msg.reply("📥 Send the photo/video/text you want to ADD.")


@dp.message()
async def save_media(msg: types.Message):
    data = load_data()

    if msg.from_user.id != OWNER_ID:
        return  # only admin can add

    # PHOTO
    if msg.photo:
        file_id = msg.photo[-1].file_id
        file_path = f"media/photo_{file_id}.jpg"
        await bot.download(msg.photo[-1], file_path)

        data["media"].append({"type": "photo", "data": file_path})
        save_data(data)
        return await msg.reply("✅ Photo added!")

    # VIDEO
    if msg.video:
        file_id = msg.video.file_id
        file_path = f"media/video_{file_id}.mp4"
        await bot.download(msg.video, file_path)

        data["media"].append({"type": "video", "data": file_path})
        save_data(data)
        return await msg.reply("✅ Video added!")

    # TEXT
    if msg.text and not msg.text.startswith("/"):
        data["media"].append({"type": "text", "data": msg.text})
        save_data(data)
        return await msg.reply("✅ Text added!")


# ────────────────────────────────────────────────
# /demo → send all saved
# ────────────────────────────────────────────────

@dp.message(Command("demo"))
async def demo(msg: types.Message):
    data = load_data()

    for m in data["media"]:
        if m["type"] == "text":
            await msg.answer(m["data"])
        elif m["type"] == "photo":
            await msg.answer_photo(FSInputFile(m["data"]))
        elif m["type"] == "video":
            await msg.answer_video(FSInputFile(m["data"]))


# ────────────────────────────────────────────────
# /broadcast → admin → all users
# ────────────────────────────────────────────────

@dp.message(Command("broadcast"))
async def bc(msg: types.Message):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply("⛔ Only admin can broadcast!")

    data = load_data()

    text = msg.text.replace("/broadcast", "").strip()
    if not text:
        return await msg.reply("👉 Usage: /broadcast your message")

    count = 0
    for uid in data["users"]:
        try:
            await bot.send_message(uid, text)
            count += 1
        except:
            pass

    await msg.reply(f"📢 Broadcast sent to {count} users!")


# ────────────────────────────────────────────────
# RUN
# ────────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
