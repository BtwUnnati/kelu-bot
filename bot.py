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
# -----------------------------------------

DATA_FILE = "data.json"

# Create data.json if missing
if not os.path.exists(DATA_FILE):
    initial = {
        "owner_id": OWNER_ID,
        "welcome_photo": TELEGRAPH_PHOTO_URL,
        "welcome_caption": "▶️➡️ <a href='https://t.me/Shelbypreviewbot?start=BQADAQADKw0AAkOGaESa3PDa4Iv_JRYE'>CLICK HERE TO WATCH DEMO PROOF</a>",
        "welcome_msg1": "😬 INTERESTED TO BUY VIDEOS 😀😀",
        "welcome_msg2": "𝗔𝗻𝘆 𝗜𝘀𝘀𝘂𝗲 𝗼𝗿 𝗗𝗼𝘂𝗯𝘁\n😬𝗛𝘆 𝗛𝘆𝗹𝗼 𝗯𝗿𝗼𝗼 Want To Buy Videos ???",
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

# ---------------- START ----------------
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    try:
        data = load_data()
        uid = message.from_user.id

        if uid not in data["users"]:
            data["users"].append(uid)
            save_data(data)

        # Send welcome photo with caption
        await message.reply_photo(
            data["welcome_photo"],
            caption=data["welcome_caption"],
            parse_mode=ParseMode.HTML
        )
       
        await message.reply_photo(
            url="",
            caption="welcome_caption",
            parse_mode=ParseMode.HTML
        )
      
        # Send text messages
        await message.reply_text(data["welcome_msg1"])
        await message.reply_text(data["welcome_msg2"])

    except Exception:
        traceback.print_exc()

# -------- ADD MODE ON/OFF (OWNER ONLY) --------
@app.on_message(filters.command("add") & filters.user(OWNER_ID))
async def add_on(client, message):
    data = load_data()
    data["add_mode"] = True
    save_data(data)
    await message.reply_text("🟢 Add mode ON.\nSend photo/video/text now.\nUse /addoff to stop.")

@app.on_message(filters.command("addoff") & filters.user(OWNER_ID))
async def add_off(client, message):
    data = load_data()
    data["add_mode"] = False
    save_data(data)
    await message.reply_text("🔴 Add mode OFF.")

# -------- DEMO (OWNER + USERS BOTH) --------
@app.on_message(filters.command("demo") & filters.private)
async def demo_handler(client, message):
    try:
        data = load_data()
        materials = data.get("materials", [])

        if not materials:
            return await message.reply_text("No demo items added yet.")

        for item in materials:
            if item["type"] == "photo":
                await message.reply_photo(item["file_id"], caption=item.get("caption", ""))
            elif item["type"] == "video":
                await message.reply_video(item["file_id"], caption=item.get("caption", ""))
            elif item["type"] == "text":
                await message.reply_text(item["text"])

    except Exception:
        traceback.print_exc()

# -------- BROADCAST (OWNER ONLY) --------
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_handler(client, message):
    try:
        msg = message.text.split(" ", 1)
        if len(msg) < 2:
            return await message.reply_text("Usage:\n/broadcast your message")

        text = msg[1]
        data = load_data()
        users = data["users"]
        sent = 0
        fail = 0

        for u in users:
            try:
                await client.send_message(u, text)
                sent += 1
            except:
                fail += 1

        await message.reply_text(f"Broadcast Done\nSent: {sent}\nFailed: {fail}")

    except Exception:
        traceback.print_exc()

# -------- STATUS (OWNER ONLY) --------
@app.on_message(filters.command("status") & filters.user(OWNER_ID))
async def status_cmd(client, message):
    data = load_data()
    stats = (
        f"👤 Users: {len(data['users'])}\n"
        f"📦 Materials: {len(data['materials'])}\n"
        f"🟢 Add Mode: {data['add_mode']}"
    )
    await message.reply_text(stats)

# -------- MEDIA CAPTURE (ONLY OWNER) --------
@app.on_message(filters.private & filters.user(OWNER_ID))
async def capture_media(client, message):
    try:
        data = load_data()

        # IGNORE commands (important!)
        if message.text and message.text.startswith("/"):
            return

        if not data["add_mode"]:
            return

        # PHOTO
        if message.photo:
            data["materials"].append({
                "type": "photo",
                "file_id": message.photo.file_id,
                "caption": message.caption or ""
            })
            save_data(data)
            return await message.reply_text("📸 Photo saved.")

        # VIDEO
        if message.video:
            data["materials"].append({
                "type": "video",
                "file_id": message.video.file_id,
                "caption": message.caption or ""
            })
            save_data(data)
            return await message.reply_text("🎥 Video saved.")

        # TEXT
        if message.text:
            data["materials"].append({
                "type": "text",
                "text": message.text
            })
            save_data(data)
            return await message.reply_text("📝 Text saved.")

    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    print("Bot starting…")
    app.run()
