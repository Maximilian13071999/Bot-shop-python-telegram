import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.utils.markdown import *
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import pandas as pd
import json


from aiogram.dispatcher import filters

import sqlite3

storage = MemoryStorage()

def connect_db(db_name):
    connect = sqlite3.connect(db_name)
    cursor = connect.cursor()
    return (connect, cursor)

bot = Bot(token="5524310251:AAGvbs_w24cCNsPp2DiBqdBiBqUxF87aoeA")
dp = Dispatcher(bot , storage = storage)

start_kb = ReplyKeyboardMarkup()
categorys = []
df = pd.read_csv("Table.csv").to_dict()
for title in df["Category"]:
    categorys.append(df["Category"][title])
unique_categorys = list(set(categorys))
for title in unique_categorys:
    start_kb.add(title)

start_kb.add("Корзина")

kor = {}
korzina1 = {}

@dp.message_handler(commands=["start"])
async def start(message:types.Message):
    with open("data_file.json", "r") as write_file:
        korzina1 = json.load(write_file)
    if not message.chat.id in korzina1:
        korzina1[message.chat.id] = []
    await message.reply("Добрый день, это бот для заказа и покупки одежды \n"
                        "\n"
                        "Для того что бы купить футболку, нажмите <b>Футболки</b>.  \n" 
                        "Для того что бы купить штаны, нажмите <b>Штаны</b>. \n"
                        "Для того что бы купить кофту, нажмите <b>Кофты</b>. \n"
                        "Для того что бы купить шорты, нажмите <b>Шорты</b>. \n"
                        , parse_mode='HTML' , reply_markup=start_kb )

async def category(mesage: types.Message , name_of_category , something):
    kb = ReplyKeyboardMarkup()
    for title in df["Title"].values():
        if name_of_category in title.lower():
            kb.add(title)
    kb.add("Назад")
    await mesage.reply(f"Выберете {something}" , reply_markup = kb)

@dp.message_handler(filters.Text(contains=["Футболки👕"] , ignore_case=True))
async def tshirt(message:types.Message):
    await category(message , 'футболка' , 'футболку')

@dp.message_handler(filters.Text(contains=["Штаны👖"] , ignore_case=True))
async def pants(message:types.Message):
    await category(message, 'штаны', 'штаны')

@dp.message_handler(filters.Text(contains=["Кофты👕"] , ignore_case=True))
async def hoodi(message:types.Message):
    await category(message, 'кофта', 'кофту')

@dp.message_handler(filters.Text(contains=["Шорты🩳"] , ignore_case=True))
async def shorts(message:types.Message):
    await category(message, 'шорты', 'шорты')

@dp.message_handler(filters.Text(contains="Назад" , ignore_case=True))
async def back(mesage:types.Message):
    await mesage.answer("Вы вернулись назад." , reply_markup=start_kb)

@dp.callback_query_handler(text="Korzina")
async def korzina(callback : types.CallbackQuery):
    size_kb = ReplyKeyboardMarkup()
    for size in kor[callback.message.chat.id]["size"].split(","):
        size_kb.add(size)
    size_kb.add("Назад")
    await callback.message.answer("Выберете размер", reply_markup=size_kb)

@dp.message_handler(filters.Text(contains="Корзина" , ignore_case=True))
async def korzina2(message: types.Message):
    for elem in korzina1[message.chat.id]:
        del_kb = InlineKeyboardMarkup()
        del_kb.add(InlineKeyboardButton(text = "    удалить" , callback_data='delete' , user = message.chat.id , item = elem))
        await bot.send_photo(message.chat.id , photo = elem["photo"] , caption = f"Наименование: {elem['title']} \n"
                                                                                f"Цена: {elem['price']} \n")

@dp.message_handler()
async def item(message):
    global kor
    if message.text in df["Title"].values():
        item = list(df["Title"].keys())[list(df["Title"].values()).index(message.text)]
        buy_kb = InlineKeyboardMarkup()
        buy_kb.add(InlineKeyboardButton(text="В корзину", callback_data="Korzina"))
        kor[message.chat.id] = {"title": df["Title"][item], "price": df['Price'][item] , "size": df['Size'][item] , "material": df['Material'][item] , "photo": df['Image'][item]}
        await bot.send_photo(message.chat.id, photo= df["Image"][item] , caption=f"Цена: {df['Price'][item]} \n"
                                                                                 f"Размеры в наличии: {df['Size'][item]} \n"
                                                                                 f"Материал: {df['Material'][item]}" , reply_markup=buy_kb)
    if message.text in ["S","M","L","XL"]:
        kor[message.chat.id]["selectedsize"] = message.text
        await message.reply("Товар добавлен в корзину.")
        if not message.chat.id in korzina1:
            korzina1[message.chat.id] = []
        korzina1[message.chat.id].append(kor[message.chat.id])
        with open("data_file.json", "w") as write_file:
            json.dump(korzina1, write_file)
        kor[message.chat.id] = {}

executor.start_polling(dp, skip_updates=True)
