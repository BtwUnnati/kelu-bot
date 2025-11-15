#!/usr/bin/env python3
import os
import json
import traceback
from pyrogram import Client, filters
from pyrogram.enums import ParseMode

# ---------------- CONFIG ----------------
API_ID = 21705136
API_HASH = "78730e89d196e160b0f1992018c6cb19"
BOT_TOKEN = "8395895550:AAE8ucM2C_YZ76vAxcA7zInt1Nv41Fcm6NQ"
OWNER_ID = 8294942940

TELEGRAPH_PHOTO_URL = "https://ar-hosting.pages.dev/1763193798506.jpg"
# ----------------------------------------

DATA_FILE = "data.json"

# Initialize if not exists
if not os.path.exists(DATA_FILE):
    initial = {
        "owner_id": OWNER_ID,
        "welcome_photo": TELEGRAPH_PHOTO_URL,
        "welcome_caption": "▶️➡️ <a href='https://t.me/Shelbypreviewbot?start=BQADAQADKw0AAkOGaESa3PDa4Iv_JRYE'>𝘾𝙇𝙄𝘾𝙆 𝙃𝙀𝙍𝙀 𝙏𝙊 𝙒𝘼𝙏𝘾𝙃 𝘿𝙀𝙈𝙊 𝙋𝙍𝙊𝙊𝙁</a>",
        "welcome_msg1": "😬 INTERESTED TO BUY VIDOES 😀😀",
        "welcome_msg2": (
            "𝗔𝗻𝘆 𝗜𝘀𝘀𝘂𝗲, 𝗗𝗼𝘂𝗯𝘁 𝗼𝗿 𝗤𝘂𝗲𝘀𝘁𝗶𝗼𝗻 𝗙𝗲𝗲𝗹 𝗙𝗿𝗲𝗲 𝗧𝗼 𝗔𝘀𝗸\n"
            "😬𝗛𝘆 𝗛𝘆𝗹𝗼 𝗯𝗿𝗼𝗼 𝙒𝙖𝙣𝙣𝙖 𝘽𝙪𝙮 𝙑𝙞𝙙𝙚𝙤𝙨 ???"
        ),
        "users": [],
        "add_mode": False,
        "materials": []
    }
    with open(DATA_FILE, "w") as f:
        json.dump(initial, f, indent=4)


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


app = Client("telegraph_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ---------------- START HANDLER ----------------
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    try:
        data = load_data()
        uid = message.from_user.id

        if uid not in data["users"]:
            data["users"].append(uid)
            save_data(data)

        # 1) Send welcome photo with working clickable caption
        await client.send_photo(
            chat_id=message.chat.id,
            photo=data["welcome_photo"],
            caption=data["welcome_caption"],
            parse_mode=ParseMode.HTML
        )

        # 2) Send welcome line 1
        await message.reply_text(data["welcome_msg1"])

        # 3) Send welcome line 2
        await message.reply_text(data["welcome_msg2"])

    except Exception as e:
        print("Start Error:", e)
        traceback.print_exc()

# ---------------- ADD ON ----------------
@app.on_message(filters.command("add") & filters.user(OWNER_ID))
async def add_on(client, message):
    data = load_data()
    data["add_mode"] = True
    save_data(data)
    await message.reply_text("✅ Add Mode ON. Send photo/video/text.")


# ---------------- ADD OFF ----------------
@app.on_message(filters.command("addoff") & filters.user(OWNER_ID))
async def add_off(client, message):
    data = load_data()
    data["add_mode"] = False
    save_data(data)
    await message.reply_text("🔴 Add Mode OFF.")


# ---------------- CAPTURE MEDIA IN ADD MODE ----------------
@app.on_message(filters.private & filters.user(OWNER_ID))
async def capture_media(client, message):
    try:
        data = load_data()
        if not data["add_mode"]:
            return

        if message.photo:
            data["materials"].append({
                "type": "photo",
                "file_id": message.photo.file_id,
                "caption": message.caption or ""
            })
            save_data(data)
            return await message.reply_text("📸 Photo Saved.")

        if message.video:
            data["materials"].append({
                "type": "video",
                "file_id": message.video.file_id,
                "caption": message.caption or ""
            })
            save_data(data)
            return await message.reply_text("🎥 Video Saved.")

        if message.text and not message.text.startswith("/"):
            data["materials"].append({
                "type": "text",
                "text": message.text
            })
            save_data(data)
            return await message.reply_text("📝 Text Saved.")

    except Exception:
        traceback.print_exc()


# ---------------- DEMO ----------------
@app.on_message(filters.command("demo") & filters.private)
async def demo_handler(client, message):
    try:
        data = load_data()
        for m in data["materials"]:
            if m["type"] == "photo":
                await client.send_photo(message.chat.id, m["file_id"], caption=m["caption"])
            elif m["type"] == "video":
                await client.send_video(message.chat.id, m["file_id"], caption=m["caption"])
            elif m["type"] == "text":
                await message.reply_text(m["text"])
    except Exception:
        traceback.print_exc()


# ---------------- BROADCAST ----------------
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_handler(client, message):
    try:
        text = message.text.split(" ", 1)[1]
        data = load_data()

        sent = 0
        failed = 0

        for uid in data["users"]:
            try:
                await client.send_message(uid, text)
                sent += 1
            except:
                failed += 1

        await message.reply_text(f"📢 Broadcast Done\nSent: {sent}\nFailed: {failed}")

    except:
        await message.reply_text("Usage: /broadcast your message")


# ---------------- STATUS ----------------
@app.on_message(filters.command("status") & filters.user(OWNER_ID))
async def status(client, message):
    d = load_data()
    await message.reply_text(
        f"Users: {len(d['users'])}\n"
        f"Materials: {len(d['materials'])}\n"
        f"Add Mode: {d['add_mode']}"
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    print("Bot Running...")
    app.run()
