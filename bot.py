#!/usr/bin/env python3
import os
import json
import traceback
from pyrogram import Client, filters
from pyrogram.enums import ParseMode

# ---------------- CONFIG - CHANGE THESE ----------------
API_ID = 21705136     # <- replace
API_HASH = "78730e89d196e160b0f1992018c6cb19"  # <- replace
BOT_TOKEN = "8395895550:AAE8ucM2C_YZ76vAxcA7zInt1Nv41Fcm6NQ"     # <- replace
OWNER_ID = 8294942940         # <- replace with your Telegram user id
TELEGRAPH_PHOTO_URL = "https://ar-hosting.pages.dev/1763193798506.jpg"  # replace
# -------------------------------------------------------

DATA_FILE = "data.json"

# Initialize data file if not present
if not os.path.exists(DATA_FILE):
    initial = {
        "owner_id": OWNER_ID,
        "welcome_photo": TELEGRAPH_PHOTO_URL,
        "welcome_caption": "▶️➡️ <a href='https://t.me/Shelbypreviewbot?start=BQADAQADKw0AAkOGaESa3PDa4Iv_JRYE'>𝘾𝙇𝙄𝘾𝙆 𝙃𝙀𝙍𝙀 𝙏𝙊 𝙒𝘼𝙏𝘾𝙃 𝘿𝙀𝙈𝙊 𝙋𝙍𝙊𝙊𝙁</a>",
        "welcome_msg1": "😬 INTERESTED TO BUY VIDOES 😀😀",
        "welcome_msg2": ("𝗔𝗻𝘆 𝗜𝘀𝘀𝘂𝗲, 𝗗𝗼𝘂𝗯𝘁 𝗼𝗿 𝗤𝘂𝗲𝘀𝘁𝗶𝗼𝗻 𝗙𝗲𝗲𝗹 𝗙𝗿𝗲𝗲 𝗧𝗼 𝗔𝘀𝗸\n"
                         "😬𝗛𝘆 𝗛𝘆𝗹𝗼 𝗯𝗿𝗼𝗼 𝙒𝙖𝙣𝙣𝙖 𝘽𝙪𝙮 𝙑𝙞𝙙𝙚𝙤𝙨 ???"),
        "users": [],
        "add_mode": False,
        "materials": []  # list of {"type":"photo"/"video"/"text","file_id":..., "caption":...}
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


@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    try:
        data = load_data()
        uid = message.from_user.id
        if uid not in data["users"]:
            data["users"].append(uid)
            save_data(data)

        # 1) Photo from telegraph (or any URL) with clickable caption (HTML)
        if data.get("welcome_photo"):
            await message.reply_photo(
                data["welcome_photo"],
                caption=data.get("welcome_caption", ""),
                parse_mode=ParseMode.HTML
            )

        # 2) Welcome text 1
        if data.get("welcome_msg1"):
            await message.reply_text(data["welcome_msg1"])

        # 3) Welcome text 2
        if data.get("welcome_msg2"):
            await message.reply_text(data["welcome_msg2"])
    except Exception:
        traceback.print_exc()


# Owner-only: enable add mode
@app.on_message(filters.command("add") & filters.user(lambda uid: uid == OWNER_ID))
async def add_on(client, message):
    data = load_data()
    data["add_mode"] = True
    save_data(data)
    await message.reply_text("✅ Add mode ON. Send photo/video/text (owner only). Use /addoff to stop.")


# Owner-only: disable add mode
@app.on_message(filters.command("addoff") & filters.user(lambda uid: uid == OWNER_ID))
async def add_off(client, message):
    data = load_data()
    data["add_mode"] = False
    save_data(data)
    await message.reply_text("🔴 Add mode OFF.")


# Capture media/text when add_mode is ON and message is from owner
@app.on_message(filters.private & filters.user(lambda uid: uid == OWNER_ID))
async def owner_material_capture(client, message):
    try:
        data = load_data()
        if not data.get("add_mode"):
            return  # ignore unless add mode is on

        # photo
        if message.photo:
            file_id = message.photo.file_id
            caption = message.caption or ""
            entry = {"type": "photo", "file_id": file_id, "caption": caption}
            data["materials"].append(entry)
            save_data(data)
            await message.reply_text("✅ Photo saved to demo (with caption).")
            return

        # video
        if message.video:
            file_id = message.video.file_id
            caption = message.caption or ""
            entry = {"type": "video", "file_id": file_id, "caption": caption}
            data["materials"].append(entry)
            save_data(data)
            await message.reply_text("✅ Video saved to demo (with caption).")
            return

        # text
        if message.text and not message.text.startswith("/"):
            entry = {"type": "text", "text": message.text}
            data["materials"].append(entry)
            save_data(data)
            await message.reply_text("✅ Text saved to demo.")
            return
    except Exception:
        traceback.print_exc()


# Demo: send all saved materials to the requester
@app.on_message(filters.command("demo") & filters.private)
async def demo_handler(client, message):
    try:
        data = load_data()
        materials = data.get("materials", [])
        if not materials:
            return await message.reply_text("No demo items available yet.")

        for item in materials:
            if item["type"] == "photo":
                await message.reply_photo(item["file_id"], caption=item.get("caption", ""))
            elif item["type"] == "video":
                await message.reply_video(item["file_id"], caption=item.get("caption", ""))
            elif item["type"] == "text":
                await message.reply_text(item["text"])
    except Exception:
        traceback.print_exc()


# Broadcast: owner-only text broadcast to all saved users
@app.on_message(filters.command("broadcast") & filters.user(lambda uid: uid == OWNER_ID))
async def broadcast_handler(client, message):
    try:
        parts = message.text.split(" ", 1)
        if len(parts) < 2:
            return await message.reply_text("Usage: /broadcast Your message here")

        text = parts[1]
        data = load_data()
        users = list(data.get("users", []))
        sent = 0
        failed = 0
        for uid in users:
            try:
                await client.send_message(uid, text)
                sent += 1
            except Exception:
                failed += 1
        await message.reply_text(f"Broadcast done — Sent: {sent}, Failed: {failed}")
    except Exception:
        traceback.print_exc()


# Helper command to check status (owner-only)
@app.on_message(filters.command("status") & filters.user(lambda uid: uid == OWNER_ID))
async def status_cmd(client, message):
    data = load_data()
    cnt = len(data.get("materials", []))
    users = len(data.get("users", []))
    add_mode = data.get("add_mode", False)
    await message.reply_text(f"Users: {users}\nMaterials: {cnt}\nAdd mode: {add_mode}")


if __name__ == "__main__":
    print("Bot starting...")
    app.run()
