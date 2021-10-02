from datetime import timedelta
from aiogram import types
from main import dp
import datetime
from modules.geo import adres_to_cords
from modules import sqLite, geo
from modules.keyboards import phone_kb, geo_kb, new_trip_kb, confirm_kb, info_kb, mark_kb, back_kb, my_deal_kb, \
    driver_msg_to_admin, driver_finish_trip_kb, yes_no_kb, taxi_driver_kb
from modules.dispatcher import bot, client_Form, start_Form, driver_Form, admin_Form
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Client menu
@dp.callback_query_handler(state=client_Form.change_distant, text='back')
@dp.callback_query_handler(state=client_Form.change_trip_confirm, text='back')
@dp.callback_query_handler(state=client_Form.show_all_trips, text='back')
@dp.callback_query_handler(state=client_Form.client_confirm_trip, text='back')
@dp.callback_query_handler(state=admin_Form.admin_first_menu, text='client')
@dp.callback_query_handler(state=start_Form.first_menu, text='client')
async def start_menu(call: types.CallbackQuery):
    client = sqLite.read_all_values_in_db(table='client', telegram_id=call.from_user.id)
    if client is None:
        await call.message.answer(text='Добрый день клиент. Тебя нет в базе данных. '
                                       'Для регистрации введи своё имя.\n'
                                       'Пожалуйста вводите реальные данные иначе ваш аккаунт '
                                       'в последствии может быть заблокирован!')
        await client_Form.client_reg_name.set()
    elif client[3] is None:
        await call.message.answer(text='Добрый день клиент. Ты зарегистрировался не до конца. '
                                       'Для регистрации введи своё имя.\n'
                                       'Пожалуйста вводите реальные данные иначе ваш аккаунт '
                                       'в последствии может быть заблокирован!')
        await client_Form.client_reg_name.set()
    else:
        await call.message.answer(text=f'Добрый день <b>{client[2]}</b>. \nЧем могу помочь?',
                                  reply_markup=new_trip_kb, parse_mode='html')
        await client_Form.client_first_menu.set()


# receive the user's name
@dp.message_handler(state=client_Form.client_reg_name)
async def name(message: types.Message):
    client = sqLite.read_all_values_in_db(table='client', telegram_id=message.from_user.id)
    if client is None:
        sqLite.insert_first_note(table='client', telegram_id=message.from_user.id)
        sqLite.insert_info(table='client', name='name', data=message.text, telegram_id=message.from_user.id)
    else:
        sqLite.insert_info(table='client', name='name', data=message.text, telegram_id=message.from_user.id)
    await message.answer('Для работы в сервисе отправьте нам свой номер телефона', reply_markup=phone_kb)
    await client_Form.client_reg_phone.set()


# receive the user's phone
@dp.message_handler(content_types=['contact'], state=client_Form.client_reg_phone)
async def loc_handler(message: types.Message):
    await message.answer('Вы успешно зарегистрированы')
    data = message.contact.phone_number
    if '+' in str(data):
        pass
    else:
        data = f'+{data}'
    sqLite.insert_info(table='client', name='phone', data=data,
                       telegram_id=message.from_user.id)
    client = sqLite.read_all_values_in_db(table='client', telegram_id=message.from_user.id)
    await message.answer(text=f'Добрый день <b>{client[2]}</b>. \nЧем могу помочь?',
                         reply_markup=new_trip_kb, parse_mode='html')
    await client_Form.client_first_menu.set()


# receive the user's phone
@dp.message_handler(state=client_Form.client_reg_phone)
async def loc_handler(message: types.Message):
    await message.answer('Поделится номером нужно нажав кнопку ниже.', reply_markup=phone_kb)


# Start trip
@dp.callback_query_handler(state=client_Form.client_first_menu, text='new_trip')
async def name(call: types.CallbackQuery):
    client = sqLite.read_all_values_in_db(table='client', telegram_id=call.from_user.id)
    all_deals = sqLite.read_all_value_bu_name(name='*', table='connections')
    lust_deal_number = int(client[13])
    if '.' in str(client[15]):
        lust_deal = str(client[15]).split('.')[0]
    else:
        lust_deal = str('2021-09-20 00:34:51')
    lust_deal = datetime.datetime.strptime(str(lust_deal), "%Y-%m-%d %H:%M:%S")
    n = 0
    for z in all_deals:
        if 'active' in str(z[6]):
            if str(z[1]) == str(call.from_user.id):
                n = 1
            else:
                pass
        else:
            pass
    if n == 0:
        if str(client[5]) != 'active':
            block_data = str(client[5]).split('.')[0]
            block_data = datetime.datetime.strptime(str(block_data), "%Y-%m-%d %H:%M:%S")
            if block_data > datetime.datetime.now():
                hours = sqLite.read_all_value_bu_name(table='admin', name='time_delta')[0][0]
                block_data = block_data + timedelta(hours=hours)
                await call.message.edit_text(f'<b>Вы звблокированы до {block_data}</b>, '
                                             f'по всем вопросам обращаться @taxiadmin', parse_mode='html',
                                             reply_markup=back_kb)
            else:
                sqLite.insert_info(table='client', telegram_id=call.from_user.id, name='status', data='active')
                await call.message.answer(f"Ваш рейтинг {client[4]}\nВведите адрес <b>ОТПРАВЛЕНИЯ</b>, отправьте "
                                          f"геопозицию отправления, либо нажмите кнопку",
                                          reply_markup=geo_kb, parse_mode='html')
                await client_Form.client_start_trip.set()
        else:
            await call.message.answer(f"Ваш рейтинг {client[4]}\nВведите адрес <b>ОТПРАВЛЕНИЯ</b>, отправьте "
                                      f"геопозицию отправления, либо нажмите кнопку",
                                      reply_markup=geo_kb, parse_mode='html')
            await client_Form.client_start_trip.set()
    elif n == 1:
        await call.message.answer('У вас есть активная заявка, перед тем как подать новую заявку удалите старую.',
                                  reply_markup=back_kb)
    # else:
    #     hours = sqLite.read_all_value_bu_name(table='admin', name='time_delta')[0][0]
    #     lust_deal = lust_deal + timedelta(hours=hours) + timedelta(minutes=15)
    #     await call.message.edit_text(f'Вы уже подали 2 заявки за последние 15 минут, вы заблокированы до '
    #                                  f'<b>{lust_deal}</b>', parse_mode='html', reply_markup=back_kb)


# receive the start trip point
@dp.message_handler(content_types=['location'], state=client_Form.client_start_trip)
async def loc_handler(message: types.Message):
    x = message.location.latitude
    y = message.location.longitude
    adres = geo.cords_to_address(x=x, y=y)
    sqLite.insert_info(table='client', name='start_geo', data=f'{x} {y}GEO#{adres}', telegram_id=message.from_user.id)
    await message.answer(text="Введите адрес <b>НАЗНАЧЕНИЯ</b> или отправьте геопозицию назначения.",
                         parse_mode='html', reply_markup=geo_kb)
    await client_Form.client_end_trip_point.set()


# receive the start trip point
@dp.message_handler(state=client_Form.client_start_trip)
async def loc_handler(message: types.Message):
    y = str(adres_to_cords(message.text))
    if y == 'Eror':
        await message.answer('Я не могу распознать введенные вами данные. Попробуйте еще раз')
    else:
        y = y.split(' ')
        sqLite.insert_info(table='client', name='start_geo', data=f'{y[1]} {y[0]}GEO#{message.text}',
                           telegram_id=message.from_user.id)
        await message.answer_location(latitude=float(y[1]), longitude=float(y[0]))
        await message.answer(text="Вот точка на карте что мне удалось найти по заданному адресу")
        await message.answer(text="Введите адрес <b>НАЗНАЧЕНИЯ</b> или отправьте геопозицию назначения.",
                             parse_mode='html', reply_markup=geo_kb)
        await client_Form.client_end_trip_point.set()


# receive the start trip point
@dp.message_handler(content_types=['location'], state=client_Form.client_end_trip_point)
async def loc_handler(message: types.Message):
    x = message.location.latitude
    y = message.location.longitude
    adres = geo.cords_to_address(x=x, y=y)
    sqLite.insert_info(table='client', name='end_geo', data=f'{x} {y}GEO#{adres}', telegram_id=message.from_user.id)
    await message.answer(text="Введите цену за которую вы хотите доехать в RUR. \nТолько цифры",
                         reply_markup=types.ReplyKeyboardRemove())
    await client_Form.client_price_trip.set()


# receive the start trip point
@dp.message_handler(state=client_Form.client_end_trip_point)
async def loc_handler(message: types.Message):
    user_id = message.from_user.id
    y = str(adres_to_cords(message.text))
    if y == 'Error':
        await message.answer('Я не могу распознать введенные вами данные. Попробуйте еще раз')
    else:
        y = y.split(' ')
        sqLite.insert_info(table='client', name='end_geo', data=f'{y[1]} {y[0]}GEO#{message.text}',
                           telegram_id=message.from_user.id)
        await message.answer(text="Вот точка на карте что мне удалось найти по заданному адресу",
                             reply_markup=types.ReplyKeyboardRemove())
        await message.answer_location(latitude=float(y[1]), longitude=float(y[0]))
        await bot.send_message(chat_id=user_id, text="Введите цену за которую вы хотите доехать в RUR. \n"
                                                     "Только цифры")
        await client_Form.client_price_trip.set()


# Info for a trip
@dp.message_handler(state=client_Form.client_price_trip)
async def loc_handler(message: types.Message):
    if message.text.isdigit():
        sqLite.insert_info(table='client', name='price', data=message.text,
                           telegram_id=message.from_user.id)
        await message.answer(f'Оставьте дополнительную информацию для водителя.', reply_markup=info_kb)
        await client_Form.client_info_trip.set()
    else:
        await message.answer('Введите только цифры')


# receive the start trip point
@dp.message_handler(state=client_Form.client_info_trip)
async def loc_handler(message: types.Message):
    client = sqLite.read_all_values_in_db(table='client', telegram_id=message.from_user.id)
    sqLite.insert_info(table='client', name='info', data=message.text,
                       telegram_id=message.from_user.id)
    await message.answer(f'Вы хотите доехать из точки А в точку Б за цену <b>{client[8]}</b> RUR.\n'
                         f'Дополнительная информация - <b>{message.text}</b>.',
                         parse_mode='html', reply_markup=confirm_kb)
    await client_Form.client_confirm_trip.set()


# receive the start trip point
@dp.callback_query_handler(state=client_Form.client_info_trip, text='without_info')
async def loc_handler(call: types.CallbackQuery):
    client = sqLite.read_all_values_in_db(table='client', telegram_id=call.from_user.id)
    sqLite.insert_info(table='client', name='info', data='Без информации',
                       telegram_id=call.from_user.id)
    await call.message.answer(f'Вы хотите доехать из точки А в точку Б за цену <b>{client[8]}</b> RUR.\n'
                              f'\nЕсли вы отмените две заявки за 24 часа вы будете заблокированы на сутки.',
                              parse_mode='html', reply_markup=confirm_kb)
    await client_Form.client_confirm_trip.set()


# Confirm new trip
@dp.callback_query_handler(state=client_Form.client_confirm_trip, text='yes_all_good')
async def loc_handler(call: types.CallbackQuery):
    user_id = call.from_user.id
    client = sqLite.read_all_values_in_db(table='client', telegram_id=user_id)
    sqLite.insert_info(table='client', name='status', data='active',
                       telegram_id=call.from_user.id)
    sqLite.insert_first_note(table='connections', telegram_id=user_id)
    trip = sqLite.read_all_value_bu_name(table='connections', name='*')
    all_trips = ''
    index = 0
    for i in trip:
        if i[1] == user_id:
            all_trips = all_trips + str(i) + '\n'
            index = i[0]
        else:
            pass
    sqLite.insert_info(table='connections', name='price', data=client[8],
                       telegram_id=index, id_name='id')
    sqLite.insert_info(table='connections', name='go_from', data=client[6],
                       telegram_id=index, id_name='id')
    sqLite.insert_info(table='connections', name='go_to', data=client[7],
                       telegram_id=index, id_name='id')
    sqLite.insert_info(table='connections', name='info', data=client[9],
                       telegram_id=index, id_name='id')
    sqLite.insert_info(table='connections', name='date', data=datetime.datetime.now(),
                       telegram_id=index, id_name='id')
    sqLite.insert_info(table='connections', name='status', data='active',
                       telegram_id=index, id_name='id')
    data_user = sqLite.read_values_in_db_by_phone(table='client', name='telegram_id', data=user_id)[13]
    previous_deal_time = str(sqLite.read_values_in_db_by_phone(table='client', name='telegram_id', data=user_id)[12])
    sqLite.insert_info(table='client', name='pr_deal_time', data=previous_deal_time,
                       telegram_id=user_id, id_name='telegram_id')
    sqLite.insert_info(table='client', name='deal_time', data=datetime.datetime.now(),
                       telegram_id=user_id, id_name='telegram_id')
    sqLite.insert_info(table='client', name='deal_number', data=str(int(data_user) + 1),
                       telegram_id=user_id, id_name='telegram_id')
    await call.message.answer(f'Ваша заявка сформирована. Ждите подтверждение от водителя.\n'
                              f'Перед вами таймер подачи вашей заявки, если ваш заказ долго не принимают '
                              f'возможно стоит увеличить цену', reply_markup=new_trip_kb)

    data_drivers = sqLite.read_all_value_bu_name(name='*', table='drivers')

    geolocation = str(client[6]).split('GEO#')[0]
    x = str(geolocation).split(' ')[0]
    y = str(geolocation).split(' ')[1]

    x_left_5 = float(x) + 0.0088 * 5
    x_right_5 = float(x) - 0.0088 * 5
    y_up_5 = float(y) + 0.0088 * 5
    y_down_5 = float(y) - 0.0088 * 5

    start = str(client[6]).split('GEO#')[1]
    end = str(client[7]).split('GEO#')[1]

    hours = sqLite.read_all_value_bu_name(table='admin', name='time_delta')[0][0]
    lust_deal = datetime.datetime.strptime(str(datetime.datetime.now()).split(".")[0], "%Y-%m-%d %H:%M:%S")
    lust_deal = lust_deal + timedelta(hours=hours)

    take_deal = InlineKeyboardButton(text=f'Взять заказ', callback_data=f'{index}')
    take_deal_kb = InlineKeyboardMarkup().add(take_deal)

    time_now = datetime.datetime.now()
    for i in data_drivers:
        if str(i[14]) == '0':
            pass
        else:
            driver_time = datetime.datetime.strptime(str(i[14]), "%Y-%m-%d %H:%M:%S")
            if time_now < driver_time:
                ix = str(i[7]).split(' ')
                if x_right_5 < float(ix[0]) < x_left_5:
                    if y_down_5 < float(ix[1]) < y_up_5:
                        distant = round((((float(x) - float(ix[0])) / 0.0088) ** 2 +
                                         ((float(y) - float(ix[1])) / 0.015187) ** 2) ** 0.5, 2)

                        text = f'<b>№{index}</b> Место отправления <b>{start}</b>\nМесто прибытия <b>{end}</b>\n' \
                               f'Расстояние до клиента <b>{distant} км</b>.\n Дата создания <b>' \
                               f'{lust_deal}</b>. Стоимость <b>{str(client[8])}</b> RUR'

                        await bot.send_message(chat_id=i[1], text=text, parse_mode='html',
                                               reply_markup=take_deal_kb)
                        await driver_Form.deal_list.set()

            else:
                pass
    await client_Form.client_first_menu.set()


# Show trips
@dp.callback_query_handler(state=client_Form.client_first_menu, text='change_trip')
@dp.callback_query_handler(state=client_Form.client_first_menu, text='change_trip')
async def name(call: types.CallbackQuery):
    client = sqLite.read_all_value_bu_name(table='connections', name='*')
    n = 0
    for i in client:
        if i[6] == 'active' and i[1] == call.from_user.id:
            await call.message.answer(f"Место отправления <b>{str(i[3]).split('GEO#')[1]}</b>\n"
                                      f"Место назначения <b>{str(i[4]).split('GEO#')[1]}</b>\n"
                                      f"Стоимость поездки <b>{str(i[8])} RUR</b>\n",
                                      reply_markup=my_deal_kb, parse_mode='html')
            sqLite.insert_info(table='client', name='number', data=f'{i[0]}',
                               telegram_id=call.from_user.id)
            n = 1
        else:
            pass
    if n == 0:
        await call.message.answer(f"У вас нет поездки", reply_markup=back_kb)
    await client_Form.show_all_trips.set()


# Change distant
@dp.callback_query_handler(state=client_Form.show_all_trips, text='change_distant')
async def name(call: types.CallbackQuery):
    await call.message.answer("Выберите на каком растоянии искать водителя", reply_markup=taxi_driver_kb)
    await client_Form.change_distant.set()


# Change distant
@dp.callback_query_handler(state=client_Form.change_distant)
async def name(call: types.CallbackQuery):
    range_search = int(call.data)
    user_id = call.from_user.id
    client = sqLite.read_all_values_in_db(table='client', telegram_id=user_id)
    data = sqLite.read_all_values_in_db(table='client', telegram_id=call.from_user.id)
    sqLite.insert_info(table='connections', name='range', data=str(call.data),
                       telegram_id=data[10], id_name='id')
    price = sqLite.read_all_values_in_db(table='connections', id_name='id', telegram_id=data[10])[8]
    await call.message.answer(f'Ваша заявка сформирована. Ждите подтверждение от водителя', reply_markup=new_trip_kb)
    data_drivers = sqLite.read_all_value_bu_name(name='*', table='drivers')

    geolocation = str(client[6]).split('GEO#')[0]
    x = str(geolocation).split(' ')[0]
    y = str(geolocation).split(' ')[1]
    x_left_1 = float(x) + 0.0088 * range_search
    x_right_1 = float(x) - 0.0088 * range_search
    y_up_1 = float(y) + 0.0088 * range_search
    y_down_1 = float(y) - 0.0088 * range_search

    start = str(client[6]).split('GEO#')[1]
    end = str(client[7]).split('GEO#')[1]

    hours = sqLite.read_all_value_bu_name(table='admin', name='time_delta')[0][0]
    lust_deal = datetime.datetime.strptime(str(datetime.datetime.now()).split(".")[0], "%Y-%m-%d %H:%M:%S")
    lust_deal = lust_deal + timedelta(hours=hours)

    take_deal = InlineKeyboardButton(text=f'Взять заказ', callback_data=f'{data[10]}')
    take_deal_kb = InlineKeyboardMarkup().add(take_deal)

    for i in data_drivers:
        if str(i[14]) != '0':
            ix = str(i[7]).split(' ')
            if str(i[13]) == '5':
                if x_right_1 < float(ix[0]) < x_left_1:
                    if y_down_1 < float(ix[1]) < y_up_1:
                        distant = round((((float(x) - float(ix[0])) / 0.0088) ** 2 +
                                         ((float(y) - float(ix[1])) / 0.015187) ** 2) ** 0.5, 2)

                        text = f'<b>№{data[10]}</b> Место отправления <b>{start}</b>\nМесто прибытия <b>{end}</b>\n' \
                               f'Расстояние до клиента <b>{distant} км</b>.\n Дата создания <b>' \
                               f'{lust_deal}</b>. Стоимость <b>{str(price)}</b> RUR'

                        await bot.send_message(chat_id=i[1], text=text, parse_mode='html', reply_markup=take_deal_kb)
                        await driver_Form.deal_list.set()
        else:
            pass
    await client_Form.client_first_menu.set()


# Show trips
@dp.callback_query_handler(state=client_Form.show_all_trips, text='change_price')
async def name(call: types.CallbackQuery):
    await call.message.answer("Введите новую цену в RUR\n"
                              "Только цифры")
    await client_Form.change_trip.set()


# Show trips
@dp.message_handler(state=client_Form.change_trip)
async def name(message: types.Message):
    if message.text.isdigit():
        sqLite.insert_info(table='client', name='data', data=message.text,
                           telegram_id=message.from_user.id)
        await message.answer(f"Поменять цену поездки на <b>{message.text}</b> RUR\n"
                             f"Только цифры", reply_markup=confirm_kb, parse_mode='html')
        await client_Form.change_trip_confirm.set()
    else:
        await message.answer('Введите только цифры')


# Show trips
@dp.callback_query_handler(state=client_Form.change_trip_confirm, text='yes_all_good')
async def name(call: types.CallbackQuery):
    user_id = call.from_user.id
    client = sqLite.read_all_values_in_db(table='client', telegram_id=user_id)
    data = sqLite.read_all_values_in_db(table='client', telegram_id=call.from_user.id)
    sqLite.insert_info(table='connections', name='price', data=data[14],
                       telegram_id=data[10], id_name='id')
    range_search = sqLite.read_all_values_in_db(table='connections', id_name='id', telegram_id=data[10])[8]
    await call.message.answer(f'Ваша заявка сформирована. Ждите подтверждение от водителя', reply_markup=new_trip_kb)
    data_drivers = sqLite.read_all_value_bu_name(name='*', table='drivers')

    geolocation = str(client[6]).split('GEO#')[0]
    x = str(geolocation).split(' ')[0]
    y = str(geolocation).split(' ')[1]
    x_left_1 = float(x) + 0.0088 * range_search
    x_right_1 = float(x) - 0.0088 * range_search
    y_up_1 = float(y) + 0.0088 * range_search
    y_down_1 = float(y) - 0.0088 * range_search

    start = str(client[6]).split('GEO#')[1]
    end = str(client[7]).split('GEO#')[1]

    hours = sqLite.read_all_value_bu_name(table='admin', name='time_delta')[0][0]
    lust_deal = datetime.datetime.strptime(str(datetime.datetime.now()).split(".")[0], "%Y-%m-%d %H:%M:%S")
    lust_deal = lust_deal + timedelta(hours=hours)

    take_deal = InlineKeyboardButton(text=f'Взять заказ', callback_data=f'{data[10]}')
    take_deal_kb = InlineKeyboardMarkup().add(take_deal)

    for i in data_drivers:
        if str(i[14]) != '0':
            ix = str(i[7]).split(' ')
            if str(i[13]) == '5':
                if x_right_1 < float(ix[0]) < x_left_1:
                    if y_down_1 < float(ix[1]) < y_up_1:
                        distant = round((((float(x) - float(ix[0])) / 0.0088) ** 2 +
                                         ((float(y) - float(ix[1])) / 0.015187) ** 2) ** 0.5, 2)

                        text = f'<b>№{data[10]}</b> Место отправления <b>{start}</b>\nМесто прибытия <b>{end}</b>\n' \
                               f'Расстояние до клиента <b>{distant} км</b>.\n Дата создания <b>' \
                               f'{lust_deal}</b>. Стоимость <b>{str(data[14])}</b> RUR'

                        await bot.send_message(chat_id=i[1], text=text, parse_mode='html', reply_markup=take_deal_kb)
                        await driver_Form.deal_list.set()
        else:
            pass

    await client_Form.client_first_menu.set()


# Delete trip
@dp.callback_query_handler(state=client_Form.show_all_trips)
async def name(call: types.CallbackQuery):
    user_id = call.from_user.id
    index = sqLite.read_all_values_in_db(table='client', telegram_id=user_id)[10]
    sqLite.insert_info(table='connections', name='status', data='delete',
                       telegram_id=int(index), id_name='id')
    await call.message.answer('Заявка удалена')
    client = sqLite.read_all_values_in_db(table='client', telegram_id=call.from_user.id)
    await call.message.answer(text=f'Добрый день <b>{client[2]}</b>. \nЧем могу помочь?',
                              reply_markup=new_trip_kb, parse_mode='html')
    await client_Form.client_first_menu.set()


@dp.callback_query_handler(state=client_Form.delete_deal, text='back')
async def loc_handler(call: types.CallbackQuery):
    index = sqLite.read_values_in_db_by_phone(table='client', name='telegram_id', data=call.from_user.id)
    good_deal = InlineKeyboardButton(text=f'Заказ выполнен', callback_data=f'good_|_{index[10]}')
    bad_deal = InlineKeyboardButton(text=f'Отменить заказ', callback_data=f'bad_|_{index[10]}')
    start_deal_kb = InlineKeyboardMarkup().add(good_deal)
    start_deal_kb.add(bad_deal)
    driver_data = sqLite.read_values_in_db_by_phone(table='connections', name='id', data=index[10])
    d_data = sqLite.read_values_in_db_by_phone(table='drivers', name='telegram_id', data=driver_data[2])
    await call.message.edit_text("Пожалуйста после окончания поездки, подтвердите выполнение заказа. \n"
                                 "Если это не сделать водитель не сможет взять новый заказ")
    await call.message.answer(text=f'К вам выехал автомобиль:\n'
                                   f'<b>{d_data[4]}</b>\nГосномер авто: <b>{d_data[5]}</b>\n'
                                   f'Телефонный номер водителя <b>{d_data[3]}</b>\n'
                                   f'Его рейтинг - <b>{d_data[6]}</b>',
                              reply_markup=start_deal_kb, parse_mode='html')


# Finish trip
@dp.callback_query_handler(state=client_Form.delete_deal, text='yes_all_good')
async def loc_handler(call: types.CallbackQuery):
    client = sqLite.read_all_values_in_db(table='client', telegram_id=call.from_user.id)
    block_period_day = datetime.datetime.now() - timedelta(days=1)
    try:
        lust_bed_data = str(client[17]).split('.')[0]
        block_lust = datetime.datetime.strptime(str(lust_bed_data), "%Y-%m-%d %H:%M:%S")
    except:
        block_lust = datetime.datetime.strptime('2021-01-20 00:34:51', "%Y-%m-%d %H:%M:%S")
    if block_period_day < block_lust:
        block_data = datetime.datetime.now() + timedelta(days=1)
        sqLite.insert_info(table='client', telegram_id=call.from_user.id, name='status', data=str(block_data))
        sqLite.insert_info(table='client', telegram_id=call.from_user.id, name='lust_block_day',
                           data=datetime.datetime.now())
        block_number = int(client[16]) + 1
        if block_number == 3:
            block_period_day = datetime.datetime.now() + timedelta(days=30)
            sqLite.insert_info(table='client', telegram_id=call.from_user.id, name='status', data=str(block_period_day))
            block_number = 0
        sqLite.insert_info(table='client', telegram_id=call.from_user.id, name='block_number_month',
                           data=block_number)
    else:
        sqLite.insert_info(table='client', telegram_id=call.from_user.id, name='lust_block_day',
                           data=datetime.datetime.now())

    data = sqLite.read_values_in_db_by_phone(table='connections', name='id', data=int(client[10]))
    sqLite.insert_info(table='connections', name='status', data='close',
                       telegram_id=int(client[10]), id_name='id')

    old_rating = sqLite.read_value_bu_name(name='rating', table='client', telegram_id=data[1])[0]
    rating_number = sqLite.read_value_bu_name(name='rating_number', table='client', telegram_id=data[1])[0]
    new_rating = str(round((float(old_rating) * float(rating_number)) / (float(rating_number) + 1), 3))
    sqLite.insert_info(table='client', name='rating', data=new_rating,
                       telegram_id=data[1])
    sqLite.insert_info(table='client', name='rating_number', data=(rating_number + 1),
                       telegram_id=data[1])

    d_data = sqLite.read_values_in_db_by_phone(table='drivers', name='telegram_id', data=data[2])
    new_balance = int(d_data[9]) + int(d_data[15])
    sqLite.insert_info(table='drivers', name='pay_line', data=new_balance, telegram_id=data[2])
    sqLite.insert_info(table='drivers', name='status', data='active', telegram_id=data[2])
    await call.message.answer('Вы отменили заявку после того как водитель ее принял. Напаминаем если вы отмените 2 '
                              'заявки в течении 24 часа то вы будете заблокированы на сутки. После трех блакировок на '
                              'сутки вы будете заблокированы на месяц!')
    await call.message.answer(text=f'Добрый день <b>{client[2]}</b>. \nЧем могу помочь?',
                              reply_markup=new_trip_kb, parse_mode='html')
    await bot.send_message(text=f'Заявка <b>№{client[10]}</b> отменена. Комиссия за этот заказ возвращена. '
                                f'Вы можете оставить жалобу в нашем канале \n\n'
                                'https://t.me/sports2day/ ',
                           chat_id=data[2], parse_mode='html', reply_markup=driver_msg_to_admin)
    await client_Form.client_first_menu.set()


# Finish trip
@dp.callback_query_handler(state=client_Form.bed_description_driver, text='yes_btn')
async def loc_handler(call: types.CallbackQuery):
    client = sqLite.read_all_values_in_db(table='client', telegram_id=call.from_user.id)
    await call.message.answer('Спасибо за отзыв')
    await call.message.answer(text=f'Добрый день <b>{client[2]}</b>. \nЧем могу помочь?',
                              reply_markup=new_trip_kb, parse_mode='html')
    await client_Form.client_first_menu.set()


# Finish trip
@dp.callback_query_handler(state=client_Form.bed_description_driver, text='no_btn')
async def loc_handler(call: types.CallbackQuery):
    client = sqLite.read_all_values_in_db(table='client', telegram_id=call.from_user.id)
    await call.message.answer('Напишите нам в сообщении что не соответствует.')
    await client_Form.bed_description_msg.set()


# Finish trip
@dp.message_handler(state=client_Form.bed_description_msg)
async def loc_handler(message: types.Message):
    client = sqLite.read_all_values_in_db(table='client', telegram_id=message.from_user.id)
    deal_id = sqLite.read_all_values_in_db(table='client', telegram_id=message.from_user.id)[10]
    driver_id = sqLite.read_all_values_in_db(table='connections', telegram_id=int(deal_id), id_name='id')[2]
    d_data = sqLite.read_all_values_in_db(table='drivers', telegram_id=driver_id)
    time_now = str(datetime.datetime.now()).split('.')[0]
    if d_data[19] is None:
        new_data = str(message.text) + f'    {time_now}###'
    else:
        new_data = str(d_data[19]) + str(message.text) + f'    {time_now}###'

    one_day = datetime.datetime.strptime(str(time_now), "%Y-%m-%d %H:%M:%S") - timedelta(days=1)
    try:
        lust_descr_data = str(d_data[19]).split('###')
        lust_descr_data = str(lust_descr_data[len(lust_descr_data) - 2]).split('    ')[1]
        lust_descr_data = datetime.datetime.strptime(lust_descr_data)
    except:
        lust_descr_data = datetime.datetime.strptime('2021-10-01 17:32:42', "%Y-%m-%d %H:%M:%S")
    if one_day < lust_descr_data:
        new_number_day = int(d_data[17]) + 1
    else:
        new_number_day = 1
    new_number = int(d_data[18]) + 1

    sqLite.insert_info(table='drivers', name='msg_bad_description', data=new_data,
                       telegram_id=driver_id)
    sqLite.insert_info(table='drivers', name='lust_bed_descr', data=1,
                       telegram_id=driver_id)
    sqLite.insert_info(table='drivers', name='bad_description_day', data=new_number_day,
                       telegram_id=driver_id)
    sqLite.insert_info(table='drivers', name='bad_description', data=new_number,
                       telegram_id=driver_id)
    await message.answer('Спасибо за отзыв')
    await message.answer(text=f'Добрый день <b>{client[2]}</b>. \nЧем могу помочь?',
                         reply_markup=new_trip_kb, parse_mode='html')
    await client_Form.client_first_menu.set()


# Finish trip
@dp.callback_query_handler(state='*')
async def loc_handler(call: types.CallbackQuery):
    if '_|_' in str(call.data):
        index = str(call.data).split('_|_')
        data = sqLite.read_values_in_db_by_phone(table='connections', name='id', data=index[1])
        sqLite.insert_info(table='client', name='number', data=index[1],
                           telegram_id=data[2])
        if index[0] == 'good':
            sqLite.insert_info(table='client', name='deal_number', data='0',
                               telegram_id=call.from_user.id)
            sqLite.insert_info(table='drivers', name='status', data='active',
                               telegram_id=data[2])

            sqLite.insert_info(table='connections', name='status', data='close',
                               telegram_id=int(index[1]), id_name='id')
            await call.message.answer('Оцените работу водителя от 1-5', reply_markup=mark_kb)
            await bot.send_message(text='Заказ выполнен, вы можете оставить жалобу в нашем канале \n\n'
                                        'https://t.me/sports2day/ ', chat_id=data[2],
                                   reply_markup=driver_finish_trip_kb)
            await client_Form.mark_for_driver.set()
        else:
            await call.message.answer("Если вы отмените заявку дважды за сутки, то вы будете заблокированы на 24 часа. "
                                      "Отменить?", reply_markup=confirm_kb)
            await client_Form.delete_deal.set()
    elif str(call.data).isdigit():
        index = str(call.data)
        sqLite.insert_info(table='drivers', name='number', data=f'{index}', telegram_id=call.from_user.id)
        data = sqLite.read_values_in_db_by_phone(table='connections', name='id', data=index)
        client = sqLite.read_values_in_db_by_phone(table='client', name='telegram_id', data=data[1])
        if client[1] == call.from_user.id:
            await call.answer(text='Нельзя заказывать у себя', show_alert=True)
        else:
            xy = str(str(data[3]).split("GEO#")[0]).split(' ')
            admin = sqLite.read_all_value_bu_name(name='*', table='admin')[0]
            procent = int(int(data[8]) * int(admin[10]) / 100)
            if procent > int(admin[11]):
                procent = int(admin[11])
            await bot.send_location(chat_id=call.from_user.id, latitude=xy[0], longitude=xy[1])
            await call.message.answer(f'Вы точно хотите взять заказ <b>№{index}</b>\n'
                                      f'Забрать человека нужно по адресу:\n<b>{str(data[3]).split("GEO#")[1]}</b>\n'
                                      f'Конечный пункт: <b>{str(data[4]).split("GEO#")[1]}</b>\n'
                                      f'Дополнительная информация от клиента - <b>{str(data[5])}</b>\n'
                                      f'Телефон заказчика <b>{str(client[3])}</b>\n'
                                      f'Рейтинг заказчика <b>{str(client[4])}</b>\n'
                                      f'Стоимость поездки - <b>{str(data[8])} RUR</b>\n'
                                      f'Коммисия по этому заказу составит <b>{procent} RUR</b>',
                                      reply_markup=confirm_kb, parse_mode='html')
            sqLite.insert_info(table='client', name='number', data=f'{index}', telegram_id=data[1])
            await driver_Form.take_deal.set()
    elif str(call.data) == 'driver_finish_trip':
        await call.message.answer('Оцените клиента от 1-5', reply_markup=mark_kb)
        await driver_Form.mark.set()
    elif str(call.data) == 'msg_admin':
        await call.message.answer('Введите текст сообщения')
        await driver_Form.msg_admin.set()
    elif str(call.data) == 'update_live':
        time_15 = datetime.datetime.now() + timedelta(minutes=15)
        sqLite.insert_info(table='drivers', name='time_geo', data=str(time_15).split('.')[0],
                           telegram_id=call.from_user.id)
        sqLite.insert_send_data(telegram_id=call.from_user.id,
                                text='15 минут истекло. Нажмите кнопку ниже если хотите продлить режим ожидания.',
                                send_data=str(time_15).split('.')[0])
        await call.message.answer('Режим ожидания продлен на 15 минут')
    else:
        pass


# receive the start trip point
@dp.message_handler(state=client_Form.mark_for_driver)
async def loc_handler(message: types.Message):
    if message.text.isdigit():
        if 1 <= int(message.text) <= 5:
            client = sqLite.read_all_values_in_db(table='client', telegram_id=message.from_user.id)
            index = sqLite.read_values_in_db_by_phone(table='client', name='telegram_id', data=message.from_user.id)
            data = sqLite.read_values_in_db_by_phone(table='connections', name='id', data=index[10])

            old_rating = sqLite.read_value_bu_name(name='rating', table='drivers', telegram_id=data[2])[0]
            rating_number = sqLite.read_value_bu_name(name='rating_number', table='drivers', telegram_id=data[2])[0]
            new_rating = str(round((float(old_rating) * float(rating_number) +
                                    float(message.text)) / (float(rating_number) + 1), 3))

            sqLite.insert_info(table='drivers', name='rating', data=new_rating,
                               telegram_id=data[2])
            sqLite.insert_info(table='drivers', name='rating_number', data=(rating_number + 1),
                               telegram_id=data[2])
            await message.answer('Соответствует ли описание водителя реальному?', reply_markup=yes_no_kb)
            await client_Form.bed_description_driver.set()
        else:
            await message.answer('Нажмите на кнопку')
    else:
        await message.answer('Нажмите на кнопку')
