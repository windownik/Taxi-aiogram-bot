from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

import logging

with open('modules/telegram_token.txt', 'r') as file:
    telegram_token = file.read()
    file.close()


storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(telegram_token)
dp = Dispatcher(bot, storage=storage)


# Welcome form
class start_Form(StatesGroup):
    first_menu = State()

    pay_menu = State()

    set_price = State()

    set_admin = State()

    set_doc = State()


# Welcome form
class client_Form(StatesGroup):
    client_first_menu = State()

    client_reg_name = State()
    client_reg_phone = State()

    client_start_trip = State()
    client_end_trip_point = State()
    client_price_trip = State()
    client_info_trip = State()
    client_confirm_trip = State()
    client_white_driver = State()

    delete_deal = State()

    mark_for_driver = State()
    bed_description_driver = State()
    bed_description_msg = State()

    show_all_trips = State()

    change_trip = State()
    change_trip_confirm = State()
    send_msg_admin = State()

    change_distant = State()


class driver_Form(StatesGroup):
    driver_first_menu = State()

    driver_reg_name = State()
    driver_reg_phone = State()
    driver_reg_car = State()
    driver_reg_type_car = State()

    driver_find_trip = State()
    driver_receive_geo = State()
    deal_list = State()
    take_deal = State()
    take_geo_live = State()
    work_deal = State()
    work_deal_confirm = State()

    driver_pay = State()
    driver_for_day = State()

    mark = State()

    msg_admin = State()
    msg_admin_confirm = State()


class admin_Form(StatesGroup):
    admin_first_menu = State()
    admin_black_list = State()
    admin_black_list_phone = State()
    admin_users = State()
    admin_ban = State()
    admin_ban_time = State()
    admin_ban_time_confirm = State()

    admin_pay_mod = State()

    dilay_time = State()

    admin_send_msg_one = State()
    admin_send_msg_one_confirm = State()

    admin_set_pay = State()
    admin_set_confirm = State()

    admin_send_msg = State()
    admin_send_msg_confirm = State()

    admin_set_payments_type = State()

    admin_set_small = State()

    admin_set_big = State()

