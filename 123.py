from aiogram import executor, types
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import logging

with open('modules/telegram_token.txt', 'r') as file:
    telegram_token = file.read()
    file.close()


storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(telegram_token)
dp = Dispatcher(bot, storage=storage)


# Start menu
@dp.message_handler(commands=['start'])
async def start_menu(message: types.Message):
    back = InlineKeyboardButton(text=f'Назад на сообщение {message.message_id-20}',
                                url=f'https://t.me/my_test_freelance_tg_bot/{message.message_id-20}')

    start_kb = InlineKeyboardMarkup().add(back)
    await message.answer(f'Привет администратор. Чем тебе помочь {message.message_id}', reply_markup=start_kb)


@dp.callback_query_handler()
async def start_menu(call: types.CallbackQuery):
    await call.answer('Ничем')


if __name__ == '__main__':
    executor.start_polling(dp)
