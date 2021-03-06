import datetime

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import timedelta

from main import dp
from modules import sqLite
from modules.dispatcher import bot, start_Form, driver_Form, client_Form, admin_Form
from modules.keyboards import geo_kb, phone_kb, taxi_driver_start_kb, confirm_kb, \
    start_driver_deal_kb, update_live_kb, back_kb, update_live_off_kb


# Client menu
@dp.callback_query_handler(state='*', text='back_driver')
@dp.callback_query_handler(state=driver_Form.msg_admin_confirm, text='back')
@dp.callback_query_handler(state=driver_Form.driver_receive_geo, text='back')
@dp.callback_query_handler(state=driver_Form.driver_pay, text='back')
@dp.callback_query_handler(state=driver_Form.driver_first_menu, text='back')
@dp.callback_query_handler(state=driver_Form.driver_find_trip, text='back')
@dp.callback_query_handler(state=admin_Form.admin_first_menu, text='taxi_driver')
@dp.callback_query_handler(state=start_Form.first_menu, text='taxi_driver')
async def start_menu(call: types.CallbackQuery):
    client = sqLite.read_all_values_in_db(table='drivers', telegram_id=call.from_user.id)
    if client is None:
        await call.message.answer(text='Добрый день водитель. Тебя нет в базе данных. '
                                       'Для регистрации введи своё имя.\n'
                                       'Пожалуйста вводите реальные данные иначе ваш аккаунт в '
                                       'последствии может быть заблокирован!')
        await driver_Form.driver_reg_name.set()

    elif client[4] is None:
        await call.message.answer(text='Добрый день. Ты зарегистрировался не до конца. '
                                       'Для регистрации введи своё имя.\n'
                                       'Пожалуйста вводите реальные данные иначе ваш аккаунт в '
                                       'последствии может быть заблокирован!')
        await driver_Form.driver_reg_name.set()
    else:
        rating = round(float(client[6]), 1)
        await call.message.answer(text=f'Добрый день <b>{client[2]}</b>. Твой рейтинг <b>{rating}</b>. \n'
                                       f'Чем могу помочь?',
                                  reply_markup=taxi_driver_start_kb(), parse_mode='html')
        await driver_Form.driver_first_menu.set()


# Change username
@dp.callback_query_handler(state=driver_Form.driver_first_menu, text='change')
async def start_menu(call: types.CallbackQuery):
    await call.message.answer(text='Для начала введи своё имя и фамилию.')
    await driver_Form.driver_reg_name.set()


# receive the user's name
@dp.message_handler(state=driver_Form.driver_reg_name)
async def name(message: types.Message):
    client = sqLite.read_all_values_in_db(table='drivers', telegram_id=message.from_user.id)
    if client is not None:
        sqLite.insert_info(table='drivers', name='name', data=message.text, telegram_id=message.from_user.id)
    else:
        sqLite.insert_first_note(table='drivers', telegram_id=message.from_user.id)
        sqLite.insert_info(table='drivers', name='name', data=message.text, telegram_id=message.from_user.id)
    await message.answer('Для работы в сервисе отправьте нам свой номер телефона. \n'
                         'Для этого нажми на кнопку ниже', reply_markup=phone_kb)
    await driver_Form.driver_reg_phone.set()


# receive the user's phone
@dp.message_handler(content_types=['contact'], state=driver_Form.driver_reg_phone)
async def loc_handler(message: types.Message):
    await message.answer('Введите госномер вашего автомобиля.')
    data = message.contact.phone_number
    if '+' in str(data):
        pass
    else:
        data = f'+{data}'
    sqLite.insert_info(table='drivers', name='phone', data=data,
                       telegram_id=message.from_user.id)
    await driver_Form.driver_reg_car.set()


# receive the user's phone
@dp.message_handler(state=driver_Form.driver_reg_phone)
async def loc_handler(message: types.Message):
    await message.answer('Поделится номером нужно нажав кнопку ниже.', reply_markup=phone_kb)


# receive the user's car
@dp.message_handler(state=driver_Form.driver_reg_car)
async def loc_handler(message: types.Message):
    await message.answer('Введите описание вашего автомобиля: марка, модель, цвет')
    sqLite.insert_info(table='drivers', name='car_number', data=message.text,
                       telegram_id=message.from_user.id)
    await driver_Form.driver_reg_type_car.set()


# receive the user's car
@dp.message_handler(state=driver_Form.driver_reg_type_car)
async def loc_handler(message: types.Message):
    client = sqLite.read_all_values_in_db(table='drivers', telegram_id=message.from_user.id)
    await message.answer('Вы успешно зарегистрировались как водитель.\n'
                         'Ваш счет пополнен на 100 RUR')
    sqLite.insert_info(table='drivers', name='car', data=message.text,
                       telegram_id=message.from_user.id)
    rating = round(float(client[6]), 1)
    await message.answer(text=f'Добрый день <b>{client[2]}</b>. Твой рейтинг <b>{rating}</b>. \n'
                              f'Чем могу помочь?',
                         reply_markup=taxi_driver_start_kb(), parse_mode='html')
    await driver_Form.driver_first_menu.set()


# Start searching deal
@dp.callback_query_handler(state=driver_Form.driver_first_menu, text='find_trip')
async def loc_handler(call: types.CallbackQuery):
    pay_mod = sqLite.read_all_value_bu_name(name='pay_mod', table='admin')[0][0]
    data = sqLite.read_all_values_in_db(table='drivers', telegram_id=call.from_user.id)
    if '.' in str(data[16]):
        lust_deal = str(data[16]).split('.')[0]
    else:
        lust_deal = str('2021-09-20 00:34:51')
    lust_deal = datetime.datetime.strptime(str(lust_deal), "%Y-%m-%d %H:%M:%S")
    if str(data[16]) == 'active':
        if '1' in str(pay_mod):
            lust_descr = str(data[19]).split('###')
            lust_descr = str(lust_descr[len(lust_descr) - 2]).split('    ')[0]
            if data[20] == 1:
                await call.message.answer(f'На вас подали жалобу. Ваши реальные данные не соответствуют данным '
                                          f'указанным при регистрации. Пожалуйста исправьте ваши данные в профиле на '
                                          f'реальные. При повторном  сообщении о несоответсвии вы будете заблокированы.\n'
                                          f'Если вы несогласноы напишите @taxiadmin. Вот текст жалобы от клиента\n\n'
                                          f'<b>{lust_descr}</b>', parse_mode='html')
                sqLite.insert_info(table='drivers', name='lust_bed_descr', data=0,
                                   telegram_id=call.from_user.id)

            else:
                pass
            await call.message.answer(f'Ваш баланс сейчас составляет {data[9]} RUR\n'
                                      f'Что бы найти заказ отправьте нам ваше место положение, \n'
                                      f'Для отмены нажмите /cancel',
                                      reply_markup=geo_kb)
            await driver_Form.driver_find_trip.set()
        else:
            await call.message.answer('Что бы найти заказ отправьте нам ваше место положение, \n'
                                      'Для отмены нажмите /cancel',
                                      reply_markup=geo_kb)
            await driver_Form.driver_find_trip.set()
    else:
        hours = sqLite.read_all_value_bu_name(table='admin', name='time_delta')[0][0]
        lust_deal = lust_deal + timedelta(hours=hours) + timedelta(minutes=15)
        await call.message.edit_text(f'Вы заблокированы до <b>{lust_deal}</b>.'
                                     f'по всем вопросам обращаться @taxiadmin',
                                     parse_mode='html', reply_markup=back_kb)
        await driver_Form.msg_admin_confirm.set()


# receive the your geo
@dp.message_handler(content_types=['location'], state=driver_Form.driver_find_trip)
async def loc_handler(message: types.Message):
    x = message.location.latitude
    y = message.location.longitude
    sqLite.insert_info(table='drivers', name='geo', data=f'{x} {y}', telegram_id=message.from_user.id)
    await message.answer('Отлично я получил ваше расположение.', reply_markup=types.ReplyKeyboardRemove())
    sqLite.insert_info(table='drivers', name='time_geo', data='0',
                       telegram_id=message.from_user.id)
    geo = sqLite.read_value_bu_name(name='geo', table='drivers', telegram_id=message.from_user.id)[0]
    x = str(geo).split(' ')[0]
    y = str(geo).split(' ')[1]

    trip = sqLite.read_all_value_bu_name(table='connections', name='*')
    sqLite.insert_info(table='drivers', name='range_geo', data='5', telegram_id=message.from_user.id)
    for i in trip:

        x_left = float(x) + 0.0088 * int(i[7])
        x_right = float(x) - 0.0088 * int(i[7])
        y_up = float(y) + 0.015187 * int(i[7])
        y_down = float(y) - 0.015187 * int(i[7])

        ix = str(i[3]).split('GEO#')[0]
        ix = str(ix).split(' ')
        if x_right < float(ix[0]) < x_left:
            if y_down < float(ix[1]) < y_up:
                if str(i[6]) == 'active':
                    k = i[0]
                    take_deal = InlineKeyboardButton(text=f'Подробнее', callback_data=f'{k}')
                    take_deal_kb = InlineKeyboardMarkup().add(take_deal)
                    start = str(i[3]).split('GEO#')[1]
                    end = str(i[4]).split('GEO#')[1]

                    hours = sqLite.read_all_value_bu_name(table='admin', name='time_delta')[0][0]
                    lust_deal = datetime.datetime.strptime(str(i[9]).split(".")[0],
                                                           "%Y-%m-%d %H:%M:%S")
                    lust_deal = lust_deal + timedelta(hours=hours)
                    distant = round((((float(x) - float(ix[0])) / 0.0088) ** 2 +
                                     ((float(y) - float(ix[1])) / 0.015187)**2) ** 0.5, 2)
                    await message.answer(f'<b>№{str(i[0])}</b> Место отправления <b>{start}</b>\n'
                                         f'Место прибытия <b>{end}</b>\n'
                                         f'Растояние до заказа <b>{distant} км</b>\n'
                                         f'Дата создания <b>{lust_deal}</b>. \n'
                                         f'Стоимость <b>{str(i[8])}</b> RUR', parse_mode='html',
                                         reply_markup=take_deal_kb)
        else:
            pass
    await message.answer('Вот все заказы которые есть поблизости от вас', reply_markup=update_live_kb)
    await driver_Form.deal_list.set()


# receive the start trip point
@dp.message_handler(state=driver_Form.driver_find_trip)
async def loc_handler(message: types.Message):
    await message.answer('Отправьте свое местоположение с помощью кнопки', reply_markup=geo_kb)


# receive the your geo
@dp.callback_query_handler(state=driver_Form.deal_list, text='back')
@dp.callback_query_handler(state=driver_Form.take_deal, text='back')
async def loc_handler(call: types.CallbackQuery):
    sqLite.insert_info(table='drivers', name='time_geo', data='0',
                       telegram_id=call.from_user.id)
    geo = sqLite.read_value_bu_name(name='geo', table='drivers', telegram_id=call.from_user.id)[0]
    x = str(geo).split(' ')[0]
    y = str(geo).split(' ')[1]

    trip = sqLite.read_all_value_bu_name(table='connections', name='*')
    sqLite.insert_info(table='drivers', name='range_geo', data='1', telegram_id=call.from_user.id)
    for i in trip:

        x_left = float(x) + 0.0088 * int(i[7])
        x_right = float(x) - 0.0088 * int(i[7])
        y_up = float(y) + 0.015187 * int(i[7])
        y_down = float(y) - 0.015187 * int(i[7])

        ix = str(i[3]).split('GEO#')[0]
        ix = str(ix).split(' ')
        if x_right < float(ix[0]) < x_left:
            if y_down < float(ix[1]) < y_up:
                if str(i[6]) == 'active':
                    k = i[0]
                    take_deal = InlineKeyboardButton(text=f'Подробнее', callback_data=f'{k}')
                    take_deal_kb = InlineKeyboardMarkup().add(take_deal)
                    start = str(i[3]).split('GEO#')[1]
                    end = str(i[4]).split('GEO#')[1]

                    hours = sqLite.read_all_value_bu_name(table='admin', name='time_delta')[0][0]
                    lust_deal = datetime.datetime.strptime(str(i[9]).split(".")[0],
                                                           "%Y-%m-%d %H:%M:%S")
                    lust_deal = lust_deal + timedelta(hours=hours)
                    distant = round((((float(x) - float(ix[0])) / 0.0088) ** 2 +
                                     ((float(y) - float(ix[1])) / 0.015187)**2) ** 0.5, 2)
                    await call.message.answer(f'<b>№{str(i[0])}</b> Место отправления <b>{start}</b>\n'
                                              f'Место прибытия <b>{end}</b>\n'
                                              f'Растояние до заказа <b>{distant} км</b>\n'
                                              f'Дата создания <b>{lust_deal}</b>. Стоимость '
                                              f'<b>{str(i[8])}</b> RUR', parse_mode='html',
                                              reply_markup=take_deal_kb)
        else:
            pass
    await call.message.answer('Вот все заказы которые есть поблизоссти от вас', reply_markup=update_live_kb)
    await driver_Form.deal_list.set()


# Confirm deal
@dp.callback_query_handler(state=driver_Form.deal_list, text='update_live')
async def loc_handler(call: types.CallbackQuery):
    await call.message.answer('Вы будете получать заявки на лету в течении 15 мин', reply_markup=update_live_off_kb)
    time_15 = datetime.datetime.now() + timedelta(minutes=15)
    sqLite.insert_info(table='drivers', name='time_geo', data=str(time_15).split('.')[0],
                       telegram_id=call.from_user.id)
    sqLite.insert_send_data(telegram_id=call.from_user.id,
                            text='15 минут истекло. Нажмите кнопку ниже если хотите продлить режим ожидания.',
                            send_data=str(time_15).split('.')[0])
    await driver_Form.driver_first_menu.set()


# Confirm deal
@dp.callback_query_handler(state=driver_Form.work_deal_confirm, text='back')
@dp.callback_query_handler(state=driver_Form.take_deal, text='yes_all_good')
async def loc_handler(call: types.CallbackQuery):
    d_data = sqLite.read_values_in_db_by_phone(table='drivers', name='telegram_id', data=call.from_user.id)

    data = sqLite.read_values_in_db_by_phone(table='connections', name='id', data=int(d_data[8]))
    client = sqLite.read_values_in_db_by_phone(table='client', name='telegram_id', data=data[1])
    admin = sqLite.read_all_value_bu_name(name='*', table='admin')[0]
    procent = int(int(data[8]) * int(admin[10]) / 100)
    if procent > int(admin[11]):
        procent = int(admin[11])

    if (data[6] == 'active' and int(d_data[9]) >= procent) or call.data == 'back':
        sqLite.insert_info(table='connections', name='driver', data=call.from_user.id,
                           telegram_id=int(d_data[8]), id_name='id')
        sqLite.insert_info(table='connections', name='status', data='work',
                           telegram_id=int(d_data[8]), id_name='id')
        good_deal = InlineKeyboardButton(text=f'Заказ выполнен', callback_data=f'good_|_{d_data[8]}')
        bad_deal = InlineKeyboardButton(text=f'Отменить заказ', callback_data=f'bad_|_{d_data[8]}')
        start_deal_kb = InlineKeyboardMarkup().add(good_deal)
        start_deal_kb.add(bad_deal)
        sqLite.insert_info(table='connections', name='status', data='work',
                           telegram_id=int(d_data[8]), id_name='id')

        lust_deal = datetime.datetime.now()
        lust_deal = lust_deal + timedelta(hours=1)
        sqLite.insert_info(table='drivers', name='status', data=lust_deal, telegram_id=call.from_user.id)
        sqLite.insert_info(table='drivers', name='time_geo', data='0',
                           telegram_id=call.from_user.id)
        old_balance = int(d_data[9])
        new_balance = old_balance - procent
        sqLite.insert_info(table='drivers', name='pay_line', data=new_balance, telegram_id=call.from_user.id)
        sqLite.insert_info(table='drivers', name='data', data=str(procent), telegram_id=call.from_user.id)
        rating = round(float(d_data[6]), 1)
        await bot.send_message(text=f'К вам едет водитель <b>{d_data[2]}</b>\n'
                                    f'<b>{d_data[4]}</b>\nГосномер авто: <b>{d_data[5]}</b>\n'
                                    f'Телефонный номер водителя <b>{d_data[3]}</b>\n'
                                    f'Его рейтинг - <b>{rating}</b>',
                               reply_markup=start_deal_kb, parse_mode='html', chat_id=data[1])
        xy = str(str(data[3]).split("GEO#")[0]).split(' ')
        await call.message.answer(f'Клиент ждет вас его телефон {str(client[3])}! Вы можете построить маршрут просто '
                                  f'нажав на карту с низу')
        await bot.send_location(chat_id=call.from_user.id, latitude=xy[0], longitude=xy[1])
        await call.message.answer(f'В конце поездки напомните клиенту подтвердить выполнение заказа, если клиент не '
                                  f'подтвердит заказ. Система автоматически закроет заказ в вашу пользу через 1 час '
                                  f'после принятия его вами к исполнению.\n\n'
                                  f'Комисия за эту поездку составляет {procent} RUR', reply_markup=start_driver_deal_kb)
        await driver_Form.work_deal.set()
    else:
        client = sqLite.read_all_values_in_db(table='drivers', telegram_id=call.from_user.id)
        await call.message.answer('Заказ уже забрали, либо у вас не достаточно средств для оплаты комисии')
        rating = round(float(client[6]), 1)
        await call.message.answer(text=f'Добрый день <b>{client[2]}</b>. Твой рейтинг <b>{rating}</b>. \n'
                                       f'Чем могу помочь?',
                                  reply_markup=taxi_driver_start_kb(), parse_mode='html')
        await driver_Form.driver_first_menu.set()


@dp.callback_query_handler(state=driver_Form.work_deal, text='bad_deal_d')
async def loc_handler(call: types.CallbackQuery):
    await call.message.answer('Вы уверены что хотите отказатся от заказа? \n\nПостарайтесь выполнить заказ в любом '
                              'случае. Если вы сейчас откажитесь от заказа ваш рейтинг понизится, '
                              'так же комиссия за поездку не будет возвращена\n\n'
                              'Напаминаем если вы отмените 2 '
                              'заявки в течении 24 часа то вы будете заблокированы на сутки. После трех блакировок на '
                              'сутки вы будете заблокированы на месяц!',
                              reply_markup=confirm_kb)
    await driver_Form.work_deal_confirm.set()


# Confirm deal
@dp.callback_query_handler(state=driver_Form.work_deal_confirm, text='yes_all_good')
async def loc_handler(call: types.CallbackQuery):
    d_data = sqLite.read_values_in_db_by_phone(table='drivers', name='telegram_id', data=call.from_user.id)
    sqLite.insert_info(table='connections', name='status', data='active',
                       telegram_id=int(d_data[8]), id_name='id')
    data = sqLite.read_values_in_db_by_phone(table='connections', name='id', data=d_data[8])
    await bot.send_message(chat_id=data[1], text='Водитель отказался от заказа, мы применем к нему меры!',
                           reply_markup=back_kb)
    await call.message.edit_text('Вы отказались от заказа.')

    block_period_day = datetime.datetime.now() - timedelta(days=1)
    try:
        lust_bed_data = str(d_data[22]).split('.')[0]
        block_lust = datetime.datetime.strptime(str(lust_bed_data), "%Y-%m-%d %H:%M:%S")
    except:
        block_lust = datetime.datetime.strptime('2021-01-20 00:34:51', "%Y-%m-%d %H:%M:%S")
    if block_period_day < block_lust:
        block_data = datetime.datetime.now() + timedelta(days=1)
        sqLite.insert_info(table='drivers', telegram_id=call.from_user.id, name='status', data=str(block_data))
        sqLite.insert_info(table='drivers', telegram_id=call.from_user.id, name='lust_block_day',
                           data=datetime.datetime.now())
        block_number = int(d_data[21]) + 1
        if block_number == 3:
            block_period_day = datetime.datetime.now() + timedelta(days=30)
            sqLite.insert_info(table='drivers', telegram_id=call.from_user.id, name='status',
                               data=str(block_period_day))
            block_number = 0
        sqLite.insert_info(table='drivers', telegram_id=call.from_user.id, name='block_number_month',
                           data=block_number)
    else:
        sqLite.insert_info(table='drivers', telegram_id=call.from_user.id, name='lust_block_day',
                           data=datetime.datetime.now())

    old_rating = sqLite.read_value_bu_name(name='rating', table='drivers', telegram_id=call.from_user.id)[0]
    rating_number = sqLite.read_value_bu_name(name='rating_number', table='drivers', telegram_id=call.from_user.id)[0]
    new_rating = str(round((float(old_rating) * float(rating_number)) / (float(rating_number) + 1), 3))

    sqLite.insert_info(table='drivers', name='rating', data=new_rating,
                       telegram_id=call.from_user.id)
    sqLite.insert_info(table='drivers', name='rating_number', data=(rating_number + 1),
                       telegram_id=call.from_user.id)
    client = sqLite.read_all_values_in_db(table='drivers', telegram_id=call.from_user.id)
    rating = round(float(client[6]), 1)
    await call.message.answer(text=f'Добрый день <b>{client[2]}</b>. Твой рейтинг <b>{rating}</b>. \n'
                                   f'Чем могу помочь?',
                              reply_markup=taxi_driver_start_kb(), parse_mode='html')
    await driver_Form.driver_first_menu.set()


# Confirm deal
@dp.callback_query_handler(state=driver_Form.work_deal, text='good_deal_d')
async def loc_handler(call: types.CallbackQuery):
    driver = sqLite.read_all_values_in_db(table='drivers', telegram_id=call.from_user.id)
    d_data = sqLite.read_values_in_db_by_phone(table='drivers', name='telegram_id', data=call.from_user.id)
    sqLite.insert_info(table='connections', name='status', data='close',
                       telegram_id=int(d_data[8]), id_name='id')
    await call.message.answer('Поздравляем заказ выполнен')
    rating = round(float(driver[6]), 1)
    await call.message.answer(text=f'Добрый день <b>{driver[2]}</b>. Твой рейтинг <b>{rating[6]}</b>. \n'
                                   f'Чем могу помочь?',
                              reply_markup=taxi_driver_start_kb(), parse_mode='html')
    await driver_Form.driver_first_menu.set()


# Confirm deal
@dp.callback_query_handler(state=client_Form.client_first_menu, text='msg_admin')
async def loc_handler(call: types.CallbackQuery):
    await call.message.answer('Введите текст сообщения')
    await driver_Form.msg_admin.set()


# Menu investor send msg
@dp.message_handler(state=driver_Form.msg_admin)
async def add_person_start(message: types.Message):
    await message.answer(text="Вот ваше сообщение. Отправить?")
    await message.answer(text=message.text, reply_markup=confirm_kb)
    sqLite.insert_info(table='drivers', name=f'data', data=message.text, telegram_id=message.from_user.id)
    await driver_Form.msg_admin_confirm.set()


# Menu investor send msg
@dp.callback_query_handler(state=driver_Form.msg_admin_confirm, text='yes_all_good')
async def add_person_start(call: types.CallbackQuery):
    client = sqLite.read_all_values_in_db(table='drivers', telegram_id=call.from_user.id)
    admin_id = sqLite.read_all_value_bu_name(table='admin', name='*')[0][1]
    driver = sqLite.read_value_bu_name(name='*', table='drivers', telegram_id=call.from_user.id)
    text = sqLite.read_value_bu_name(name='data', table='drivers', telegram_id=call.from_user.id)[0]
    await bot.send_message(chat_id=admin_id, text=f'Вам сообщение от <b>{driver[2]}</b>, телефонный номер '
                                                  f'<b>{driver[3]}</b> \n\n{text}',
                           parse_mode='html')
    await call.message.answer('Ваше сообщение отправлено')
    rating = round(float(client[6]), 1)
    await call.message.answer(text=f'Добрый день <b>{client[2]}</b>. Твой рейтинг <b>{rating}</b>. \n'
                                   f'Чем могу помочь?',
                              reply_markup=taxi_driver_start_kb(), parse_mode='html')
    await driver_Form.driver_first_menu.set()


# receive the start trip point
@dp.message_handler(state=driver_Form.mark)
async def loc_handler(message: types.Message):
    if message.text.isdigit():
        if 1 <= int(message.text) <= 5:
            client = sqLite.read_all_values_in_db(table='drivers', telegram_id=message.from_user.id)
            index = sqLite.read_values_in_db_by_phone(table='drivers', name='telegram_id', data=message.from_user.id)
            data = sqLite.read_values_in_db_by_phone(table='connections', name='id', data=index[8])

            old_rating = sqLite.read_value_bu_name(name='rating', table='client', telegram_id=data[1])[0]
            rating_number = sqLite.read_value_bu_name(name='rating_number', table='drivers', telegram_id=data[1])[0]
            new_rating = str(round((float(old_rating) * float(rating_number) +
                                    float(message.text)) / (float(rating_number) + 1), 3))
            sqLite.insert_info(table='client', name='rating', data=new_rating,
                               telegram_id=data[1])
            sqLite.insert_info(table='client', name='rating_number', data=(int(rating_number) + 1),
                               telegram_id=data[1])
            await message.answer('Спасибо за отзыв')
            rating = round(float(client[6]), 1)
            await message.answer(text=f'Добрый день <b>{client[2]}</b>. Твой рейтинг <b>{rating}</b>. \n'
                                      f'Чем могу помочь?',
                                 reply_markup=taxi_driver_start_kb(), parse_mode='html')
            await driver_Form.driver_first_menu.set()
        else:
            await message.answer('Нажмите на кнопку')
    else:
        await message.answer('Нажмите на кнопку')
