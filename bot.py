#!/usr/bin/env python3
import os
import json
from pyrogram import Client, filters
from pyrogram.enums import ParseMode

# ---------------- CONFIG ----------------
API_ID = 21705136
API_HASH = "78730e89d196e160b0f1992018c6cb19"
BOT_TOKEN = "8395895550:AAE8ucM2C_YZ76vAxcA7zInt1Nv41Fcm6NQ"
OWNER_ID = 8294942940

WELCOME_PHOTO = "https://ar-hosting.pages.dev/1763193798506.jpg"
WELCOME_CAPTION = (
    "▶️➡️ <a href='https://t.me/Shelbypreviewbot?start=BQADAQADKw0AAkOGaESa3PDa4Iv_JRYE'>CLICK HERE TO WATCH DEMO</a>"
)

WELCOME_MSG1 = "😬 INTERESTED TO BUY PACKAGES 😀😀"
WELCOME_MSG2 = "Any Issue, Doubt or Question — Feel Free To Ask!"
# -----------------------------------------

DATA_FILE = "data.json"

# ---------------- LOAD / SAVE ----------------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"users": [], "add_mode": False, "materials": []}, f, indent=4)


def load():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------- BOT ----------------
app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# ---------------- START ----------------
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    data = load()

    if message.from_user.id not in data["users"]:
        data["users"].append(message.from_user.id)
        save(data)

    # 1) Photo + clickable caption
    await message.reply_photo(
        WELCOME_PHOTO,
        caption=WELCOME_CAPTION,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

    # 2) Welcome text 1
    await message.reply_text(WELCOME_MSG1)

    # 3) Welcome text 2
    await message.reply_text(WELCOME_MSG2)


# ---------------- ADD MODE ON ----------------
@app.on_message(filters.command("add") & filters.user(OWNER_ID))
async def add_on(client, message):
    data = load()
    data["add_mode"] = True
    save(data)
    await message.reply_text("✅ Add mode ON — now send photos/videos/text to save.")


# ---------------- ADD MODE OFF ----------------
@app.on_message(filters.command("addoff") & filters.user(OWNER_ID))
async def add_off(client, message):
    data = load()

    if not data["add_mode"]:
        return await message.reply_text("Add mode already OFF.")

    data["add_mode"] = False
    save(data)

    await message.reply_text("❌ Add mode OFF — bot will not save anything now.")


# ---------------- SAVE MATERIAL ----------------
@app.on_message(filters.private & filters.user(OWNER_ID))
async def save_material(client, message):
    data = load()

    if not data["add_mode"]:
        return

    # Photo
    if message.photo:
        data["materials"].append({
            "type": "photo",
            "file_id": message.photo.file_id,
            "caption": message.caption or ""
        })
        save(data)
        return await message.reply_text("📸 Photo saved.")

    # Video
    if message.video:
        data["materials"].append({
            "type": "video",
            "file_id": message.video.file_id,
            "caption": message.caption or ""
        })
        save(data)
        return await message.reply_text("🎥 Video saved.")

    # Text
    if message.text and not message.text.startswith("/"):
        data["materials"].append({
            "type": "text",
            "text": message.text
        })
        save(data)
        return await message.reply_text("📝 Text saved.")


# ---------------- DEMO ----------------
@app.on_message(filters.command("demo") & filters.private)
async def demo_handler(client, message):
    data = load()

    if not data["materials"]:
        return await message.reply_text("No saved demo material found.")

    for item in data["materials"]:
        if item["type"] == "photo":
            await message.reply_photo(item["file_id"], caption=item["caption"])

        elif item["type"] == "video":
            await message.reply_video(item["file_id"], caption=item["caption"])

        elif item["type"] == "text":
            await message.reply_text(item["text"])


# ---------------- BROADCAST ----------------
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_handler(client, message):

    if len(message.text.split()) < 2:
        return await message.reply_text("Usage: /broadcast your_message")

    data = load()
    msg = message.text.split(" ", 1)[1]
    users = data["users"]

    sent = 0
    for u in users:
        try:
            await client.send_message(u, msg)
            sent += 1
        except:
            pass

    await message.reply_text(f"📢 Broadcast sent to {sent} users.")


# ---------------- RUN ----------------
print("Bot is running...")
app.run()
