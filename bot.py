import json
from pyrogram import Client, filters

API_ID = 21705136
API_HASH = "78730e89d196e160b0f1992018c6cb19"
BOT_TOKEN = "8395895550:AAE8ucM2C_YZ76vAxcA7zInt1Nv41Fcm6NQ"

# -------------------------
# Load Data
# -------------------------
def load_data():
    with open("data.json") as f:
        return json.load(f)

def save_data(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

data = load_data()
OWNER = data["owner_id"]

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# -------------------------
# START MESSAGE
# -------------------------
@app.on_message(filters.command("start"))
async def start_handler(_, msg):

    uid = msg.from_user.id
    if uid not in data["users"]:
        data["users"].append(uid)
        save_data(data)

    # 1️⃣ Photo with clickable caption
    await msg.reply_photo(
        data["welcome_photo"],
        caption=data["caption"],
        parse_mode="html"
    )

    # 2️⃣ Text 1
    await msg.reply_text(data["msg1"])

    # 3️⃣ Text 2
    await msg.reply_text(data["msg2"])


# -------------------------
# ADD MODE ON
# -------------------------
@app.on_message(filters.command("add"))
async def add_cmd(_, msg):
    if msg.from_user.id != OWNER:
        return

    data["add_mode"] = True
    save_data(data)
    await msg.reply("ADD MODE ON — अब जो भी photo/video/text भेजोगे वो demo में add होगा.")


# -------------------------
# ADD MODE OFF
# -------------------------
@app.on_message(filters.command("addoff"))
async def addoff_cmd(_, msg):
    if msg.from_user.id != OWNER:
        return

    data["add_mode"] = False
    save_data(data)
    await msg.reply("ADD MODE OFF हो गया।")


# -------------------------
# CAPTURE MEDIA/TEXT IF ADD MODE IS ON
# -------------------------
@app.on_message(filters.all & filters.private)
async def capture(_, msg):
    if not data["add_mode"]:
        return

    content = None

    if msg.photo:
        content = {"type": "photo", "file_id": msg.photo.file_id, "caption": msg.caption or ""}
    elif msg.video:
        content = {"type": "video", "file_id": msg.video.file_id, "caption": msg.caption or ""}
    elif msg.text:
        content = {"type": "text", "text": msg.text}

    if content:
        data["demo"].append(content)
        save_data(data)
        await msg.reply("Added ✔")


# -------------------------
# DEMO SEND (ALL USERS CAN USE)
# -------------------------
@app.on_message(filters.command("demo"))
async def demo_handler(_, msg):

    if not data["demo"]:
        return await msg.reply("Demo empty hai")

    for d in data["demo"]:
        if d["type"] == "photo":
            await msg.reply_photo(d["file_id"], caption=d["caption"])
        elif d["type"] == "video":
            await msg.reply_video(d["file_id"], caption=d["caption"])
        elif d["type"] == "text":
            await msg.reply_text(d["text"])


# -------------------------
# BROADCAST
# -------------------------
@app.on_message(filters.command("broadcast"))
async def broadcast_cmd(_, msg):
    if msg.from_user.id != OWNER:
        return

    if len(msg.command) < 2:
        return await msg.reply("Usage: /broadcast your message")

    text = msg.text.split(" ", 1)[1]

    sent = 0
    for uid in data["users"]:
        try:
            await app.send_message(uid, text)
            sent += 1
        except:
            pass

    await msg.reply(f"Broadcast sent to {sent} users")


# -------------------------
# RUN BOT
# -------------------------
app.run()
