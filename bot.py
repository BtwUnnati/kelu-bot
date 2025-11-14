#!/usr/bin/env python3
import os
import asyncio
import logging
from typing import List

from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ENV
BOT_TOKEN = 
MONGO_URI = 
DB_NAME = "telegram_bot_db"
ADMIN_IDS =  # comma separated Telegram user IDs
START_LINK = 
START_CAPTION_TEXT = os.getenv("START_CAPTION_TEXT", "▶️➡️ [CLICK HERE TO WATCH DEMO PROOF]({link})\n\n😬 INTERESTED TO BUY VIDOES ❓❓\n\n𝗔𝗻𝘆 𝗜𝘀𝘀𝘂𝗲, 𝗗𝗼𝘂𝗯𝘁 𝗼𝗿 𝗤𝘂𝗲𝘀𝘁𝗶𝗼𝗻 𝗙𝗲𝗲𝗹 𝗙𝗿𝗲𝗲 𝗧𝗼 𝗔𝘀𝗸 😬\n𝗛𝘆 𝗛𝘆𝗹𝗼 𝗯𝗿𝗼𝗼 𝙒𝙖𝙣𝙣𝙖 𝘽𝙪𝙮 𝙑𝙞𝙙𝙚𝙤𝙨 ???")
START_PHOTO_FILE_ID =   # optional

if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN missing")

def parse_admins(raw: str) -> List[int]:
    out = []
    for p in (raw or "").split(","):
        try:
            out.append(int(p.strip()))
        except:
            pass
    return out

ADMINS = parse_admins(ADMIN_IDS)

# Bot setup
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Mongo setup
mongo = AsyncIOMotorClient(MONGO_URI)
db = mongo[DB_NAME]
users_col = db["users"]
items_col = db["items"]

class AddState(StatesGroup):
    waiting_for_item = State()

class BroadcastState(StatesGroup):
    waiting_for_broadcast = State()

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

async def register_user(user: types.User):
    await users_col.update_one(
        {"user_id": user.id},
        {"$setOnInsert": {
            "user_id": user.id,
            "first_name": user.first_name,
            "username": user.username
        }},
        upsert=True
    )

# --- Handlers ---

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await register_user(message.from_user)
    caption = START_CAPTION_TEXT.format(link=START_LINK)
    try:
        if START_PHOTO_FILE_ID:
            await bot.send_photo(message.chat.id, START_PHOTO_FILE_ID, caption=caption)
        else:
            await message.reply(caption)
    except Exception as e:
        logger.exception("Failed to send start: %s", e)
        await message.reply(caption)

@dp.message_handler(commands=["add"])
async def cmd_add(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("Sirf admin use kar sakta hai.")
        return
    await message.reply("Add mode activated. Send text/photo/video/document to save. Finish with /done")
    await AddState.waiting_for_item.set()

@dp.message_handler(state=AddState.waiting_for_item, content_types=types.ContentTypes.ANY)
async def add_receive(message: types.Message, state: FSMContext):
    if message.text and message.text.startswith("/done"):
        await state.finish()
        await message.reply("Add mode finished.")
        return

    doc = {"created_at": types.datetime.datetime.now()}

    if message.text:
        doc.update({"type": "text", "value": message.text})
    elif message.photo:
        doc.update({"type": "photo", "value": message.photo[-1].file_id})
    elif message.video:
        doc.update({"type": "video", "value": message.video.file_id})
    elif message.document:
        doc.update({"type": "document", "value": message.document.file_id, "filename": message.document.file_name})
    else:
        await message.reply("Unsupported type. Send text/photo/video/document or /done")
        return

    await items_col.insert_one(doc)
    await message.reply("Item saved.")

@dp.message_handler(commands=["done"], state=AddState.waiting_for_item)
async def cmd_done(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("Add mode finished.")

@dp.message_handler(commands=["demo"])
async def cmd_demo(message: types.Message):
    await register_user(message.from_user)
    items_cursor = items_col.find().sort("created_at", 1)
    count = await items_col.count_documents({})
    if count == 0:
        await message.reply("No demo items yet.")
        return
    await message.reply(f"Sending {count} demo items...")
    async for item in items_cursor:
        try:
            t = item["type"]
            if t == "text":
                await message.answer(item["value"])
            elif t == "photo":
                await bot.send_photo(message.chat.id, item["value"])
            elif t == "video":
                await bot.send_video(message.chat.id, item["value"])
            elif t == "document":
                await bot.send_document(message.chat.id, item["value"])
            await asyncio.sleep(0.2)
        except:
            continue

@dp.message_handler(commands=["demoall"])
async def cmd_demoall(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("Admin only.")
        return
    users_cursor = users_col.find({})
    items = list(items_col.find().sort("created_at", 1))
    if not items:
        await message.reply("No items saved.")
        return
    async for u in users_cursor:
        uid = u["user_id"]
        for item in items:
            t = item["type"]
            try:
                if t == "text":
                    await bot.send_message(uid, item["value"])
                elif t == "photo":
                    await bot.send_photo(uid, item["value"])
                elif t == "video":
                    await bot.send_video(uid, item["value"])
                elif t == "document":
                    await bot.send_document(uid, item["value"])
                await asyncio.sleep(0.2)
            except:
                continue
    await message.reply("Demo broadcast finished.")

@dp.message_handler(commands=["broadcast"])
async def cmd_broadcast(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("Admin only.")
        return
    await BroadcastState.waiting_for_broadcast.set()
    await message.reply("Send message (text/photo/video/document) to broadcast. /cancel to abort.")

@dp.message_handler(state=BroadcastState.waiting_for_broadcast, content_types=types.ContentTypes.ANY)
async def handle_broadcast(message: types.Message, state: FSMContext):
    if message.text and message.text.startswith("/cancel"):
        await state.finish()
        await message.reply("Broadcast cancelled.")
        return

    users_cursor = users_col.find({})
    async for u in users_cursor:
        uid = u["user_id"]
        try:
            if message.text:
                await bot.send_message(uid, message.text, parse_mode=ParseMode.MARKDOWN)
            elif message.photo:
                await bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption or "")
            elif message.video:
                await bot.send_video(uid, message.video.file_id, caption=message.caption or "")
            elif message.document:
                await bot.send_document(uid, message.document.file_id, caption=message.caption or "")
        except:
            continue
        await asyncio.sleep(0.2)
    await state.finish()
    await message.reply("Broadcast finished.")

@dp.message_handler(content_types=types.ContentTypes.ANY)
async def catch_all(message: types.Message):
    await register_user(message.from_user)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
