import asyncio
import logging
from os import environ

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from description import BOT_DESCRIPTION, CONVERT_DESCRIPTION, YOUTUBE_DESCRIPTION
from dotenv import load_dotenv

# Custom exc
from exceptions import DownloadError
from service import ConvertUserVideo, YoutubeDownload
from telethon import TelegramClient, events

load_dotenv()

# configs
TOKEN = environ.get("BOT_TOKEN")
API_ID = environ.get("API_ID")
API_HASH = environ.get("API_HASH")
logging.basicConfig(level=logging.INFO)

# aiogram
md = ParseMode.MARKDOWN_V2
bot = Bot(token=TOKEN)
dp = Dispatcher()

# telethon
client = TelegramClient("main_session", API_ID, API_HASH)

# service workers
yt_worker = YoutubeDownload()
ct_worker = ConvertUserVideo()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    convert_button = types.KeyboardButton(text="📹 Конвертировать")
    youtube_button = types.KeyboardButton(text="🔴 YouTube")
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[convert_button, youtube_button]],
        resize_keyboard=True,
        input_field_placeholder="Конвертировать",
    )
    await message.answer(BOT_DESCRIPTION, reply_markup=keyboard, parse_mode=md)


@dp.message(F.text.lower() == "📹 конвертировать")
async def process_convert_button(message: types.Message):
    await message.answer(CONVERT_DESCRIPTION, parse_mode=md)


@dp.message(F.text.lower() == "🔴 youtube")
async def process_youtube_button(message: types.Message):
    await message.answer(YOUTUBE_DESCRIPTION)


@dp.message()
async def download_from_youtube(message: types.Message):
    if message.text:
        url = message.text
        download_message = await message.answer("*Скачиваю\\.\\.\\.*", parse_mode=md)
        try:
            filename = await yt_worker.download_from_youtube(url)
            file = FSInputFile(filename)
            await message.answer_audio(file)
            await yt_worker.delete_file(filename)
        except DownloadError:
            await message.answer("*Неправильная ссылка*", parse_mode=md)

        await bot.delete_message(download_message.chat.id, download_message.message_id)
    elif message.video:
        pass
    else:
        await message.answer("*Неправильный тип данных*", parse_mode=md)


@client.on(events.NewMessage)
async def convert_video(event):
    message = event.message
    sender = await event.get_sender()

    if message.video:
        deleted_message = await client.send_message(sender, "**Исполняю...**")
        path = await message.download_media()
        filename = await ct_worker.convert(path)
        await client.send_file(entity=sender, file=filename, video_note=True)
        await client.delete_messages(entity="me", message_ids=[deleted_message.id])
        await ct_worker.delete_file(filename)


async def main():
    await client.start(bot_token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
