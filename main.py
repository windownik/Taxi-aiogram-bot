from aiogram import executor
from modules.dispatcher import dp
from modules.server import sender
import threading


if __name__ == '__main__':
    b = threading.Thread(target=sender, name="Thread_2")
    b.start()
    executor.start_polling(dp)
