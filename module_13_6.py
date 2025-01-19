from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ""
bot = Bot(token = api)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
kb.add(button1, button2)

kb_1 = InlineKeyboardMarkup()
button3 = InlineKeyboardButton(text = 'Рассчитать норму калорий', callback_data='calories')
button4 = InlineKeyboardButton(text = 'Формула расчёта', callback_data='formulas')
kb_1.add(button3, button4)

start = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text='Рассчитать'),
        KeyboardButton(text='Информация')
        ],
    ],     resize_keyboard=True
)

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup = kb)

@dp.message_handler(text='Рассчитать')
async def message_handler(message):
    await message.answer("Выберите опцию:", reply_markup = kb_1)

@dp.callback_query_handler(text="formulas")
async def callback_query_handler(call):

    await call.message.answer(
        f'Норма (муж.): 10 * вес(кг) + 6.25 * рост(см) - 5 * возраст(лет) + 5.\n'
        f'Норма (жен.): 10 * вес(кг) + 6.25 * рост(см) - 5 * возраст(лет) - 161')
    await call.answer()


@dp.callback_query_handler(text="calories")
async def set_age(call):
    await call.message.answer("Введите свой возраст(полных лет):")
    await UserState.age.set()
    await call.answer()

@dp.message_handler(text='Информация')
async def info(message):
    await message.answer("Я бот помогающий твоему здоровью.")

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age = message.text)
    await message.answer("Введите свой рост(см):")
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth = message.text)
    await message.answer("Введите свой вес(кг):")
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    try:
        age = float(data['age'])
        growth = float(data['growth'])
        weight = float(data['weight'])
    except ValueError:
        await message.answer("Ошибка: ввести можно только цифры.")
        await state.finish()
        return
    calories_man = 10 * weight + 6.25 * growth - 5 * age + 5
    calories_wom = 10 * weight + 6.25 * growth - 5 * age - 161
    await message.answer(f'Норма (муж.): {calories_man} ккал')
    await message.answer(f'Норма (жен.): {calories_wom} ккал')
    await state.finish()


@dp.message_handler()
async def all_messages(message):
    await message.answer("Введите команду /start, чтобы начать общение.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
