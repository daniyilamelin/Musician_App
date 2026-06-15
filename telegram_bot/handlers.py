
from google import genai
import pylast
from motor.motor_asyncio import AsyncIOMotorClient
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards import menu
import json
import os
from redis_connect import redis_client
from database import find_id


client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DATABASE")]
collection = db[os.getenv("MONGO_COLLECTION")]

network = pylast.LastFMNetwork(
    api_key = os.getenv("LASTFM_API_KEY"),
    api_secret = os.getenv("LASTFM_API_SECRET"),
)
ai_client = genai.Client(api_key= os.getenv("GENAI_API_KEY"))
music_router = Router()

@music_router.message(Command("start"))
async def start(message: Message):
    await message.answer("Вітаємо в боті Musician!\n"
                         "Меню бота із всім функціоналом /menu\n"
                         "Приємного використання!\n"
                         "Не забудьте відразу зареєструватися на сайті"
                         "для доступу до всього функціоналу\n")

@music_router.message(Command("menu"))
async def show_menu(message: Message):
    await message.answer("Основне меню з усіма командами", reply_markup = menu)

class Add_Music(StatesGroup):
    song = State()


@music_router.message(F.text == "Додати пісню")
async def add(message: Message, state: FSMContext):
    await state.set_state(Add_Music.song)
    await message.answer("Введіть пісню яку ви хочете добавити за таким форматом\n"
                         "Автор - Назва пісні")

@music_router.message(Add_Music.song)
async def add_song(message: Message, state: FSMContext):
    await state.update_data(song = message.text)
    i = message.text.split(" - ")
    print(i[0])
    print(i[1])

    artist = network.get_artist(i[0])
    artist_tag = artist.get_top_tags(limit=5)
    song = network.get_track(i[0], i[1])
    song_tag = song.get_top_tags(limit=5)
    tags = []
    for tag in artist_tag:
        tags.append(tag.item.get_name())
    for tag in song_tag:
        tags.append(tag.item.get_name())
    genres = song_tag[0].item.name
    response = ai_client.models.generate_content(
        model = "gemini-flash-latest",
        contents = f"""
        You are a music analyst. Analyze the following song and return ONLY a JSON object, no extra text.
        Song: {song}
        Artist: {artist}
        Genre: {genres}
        Tags: {tags}
        
        Return this exact JSON structure:
        {{
            "mood": "Return ONLY one of these exact mood values:
happy, sad, energetic, calm, melancholic, nostalgic, focused, romantic, angry, chill",
            "energy": "one single word, lowercase (e.g. low, high, ,medium)",
            "mood_description": "",
            "recommended_for": []
        }}
        """
    )
    data = json.loads(response.text)
    documents = {
        "user_id": message.from_user.id,
        "song": i[1],
        "artist": i[0],
        "tags": list(set(tags)),
        "genre": genres,
        **data
    }


    print(documents)
    await collection.insert_one(documents)
    await message.answer(f"Добавлено пісню: {message.text}")
    await state.clear()


@music_router.message(F.text == "Показати плейлист")
async def show_songs(message: Message):

    cu = collection.find({"user_id": message.from_user.id})
    songs = await cu.to_list()

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard = [
            [InlineKeyboardButton(text = f"{n}. {doc['song']} - {doc['artist']}",
                                  callback_data = f"song_{doc['song']}")]for n, doc in enumerate(songs, start = 1)]
    )
    await message.answer("Ось ваш плейлист", reply_markup = inline_kb)


@music_router.callback_query(F.data.startswith("song_"))
async def one_song(callback: CallbackQuery):
    i = callback.data.split("_")
    print(i[1])
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard = [
            [
                InlineKeyboardButton(text = "Видалити пісню", callback_data = f"del_{i[1]}")
            ]

        ]
    )
    song = await collection.find_one({"song" : i[1]})
    if song:
        await callback.message.answer(f"Назва: {song['song']}\n"
                             f"Автор: {song['artist']}\n"
                             f"Настрій: {song['mood']}\n"
                             f"Опис: {song['mood_description']}", reply_markup = inline_keyboard)

@music_router.callback_query(F.data.startswith("del_"))
async def del_song(callback: CallbackQuery):
    i = callback.data.split("_")
    await collection.delete_one({"song": i[1]})
    await callback.message.answer("Пісню видано з плейлисту")

@music_router.message(Command("verify"))
async def verify(message: Message):
    telegram_id = message.from_user.id
    token = message.text.split(" ")[1]
    if token:
        user_id = await redis_client.get(f"verify:{token}")
        await find_id(telegram_id, user_id)
        await message.answer("Дякуємо за реєстрацію. Використовуйте додаток на повну")
    else:
        await message.answer("Ми не змогли знайти ваш код. Спробуйте новий")






