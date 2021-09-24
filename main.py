from aiogram import executor
from modules.dispatcher import dp
from modules.server import cleaner
import threading


if __name__ == '__main__':
    t = threading.Thread(target=cleaner, name="Thread")
    t.start()
    executor.start_polling(dp)
