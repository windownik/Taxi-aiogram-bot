from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from modules import sqLite

taxi_driver = InlineKeyboardButton(text=f'Вы клиент', callback_data='client')
client = InlineKeyboardButton(text=f'Вы водитель', callback_data='taxi_driver')
back = InlineKeyboardButton(text=f'Назад', callback_data='back')

start_kb = InlineKeyboardMarkup().add(taxi_driver, client)
back_kb = InlineKeyboardMarkup().add(back)

geo = KeyboardButton(text=f'🧭 Поделится местоположением', request_location=True)

geo_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(geo)

phone = KeyboardButton(text=f'📞 Поделится телефоном', request_contact=True)

phone_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(phone)

msg_admin = InlineKeyboardButton(text=f'Написать администратору', callback_data='msg_admin')


def taxi_driver_start_kb():

    taxi_driver_change = InlineKeyboardButton(text=f'Изменить учетную запись', callback_data='change')
    taxi_driver_find = InlineKeyboardButton(text=f'Найти заказ', callback_data='find_trip')

    driver_pay = InlineKeyboardButton(text=f'Пополнить баланс', callback_data='driver_pay')
    taxi_driver_start_kb = InlineKeyboardMarkup().add(taxi_driver_find)
    taxi_driver_start_kb.add(taxi_driver_change)
    if '1' in str(sqLite.read_all_value_bu_name(name='pay_mod', table='admin')[0][0]):
        taxi_driver_start_kb.add(driver_pay)
    else:
        pass
    taxi_driver_start_kb.add(back)
    return taxi_driver_start_kb


driver_msg_to_admin = InlineKeyboardMarkup()
driver_msg_to_admin.add(back)


taxi_driver_1 = InlineKeyboardButton(text=f'Найти заказы в радиусе 1км', callback_data='taxi_driver_1')
taxi_driver_3 = InlineKeyboardButton(text=f'Найти заказы в радиусе 3км', callback_data='taxi_driver_3')
taxi_driver_5 = InlineKeyboardButton(text=f'Найти заказы в радиусе 5км', callback_data='taxi_driver_5')
taxi_driver_10 = InlineKeyboardButton(text=f'Найти заказы в радиусе 10км', callback_data='taxi_driver_10')
taxi_driver_2000 = InlineKeyboardButton(text=f'Найти заказы в радиусе свыше 10км', callback_data='taxi_driver_2000')

taxi_driver_kb = InlineKeyboardMarkup().add(taxi_driver_1)
taxi_driver_kb.add(taxi_driver_3)
taxi_driver_kb.add(taxi_driver_5)
taxi_driver_kb.add(taxi_driver_10)
taxi_driver_kb.add(taxi_driver_2000)
taxi_driver_kb.add(back)

new_trip = InlineKeyboardButton(text=f'Новая поездка', callback_data='new_trip')
my_trip = InlineKeyboardButton(text=f'Изменить поездку', callback_data='change_trip')
new_trip_kb = InlineKeyboardMarkup().add(new_trip)
new_trip_kb.add(my_trip)
new_trip_kb.add(back)

yes_all_good = InlineKeyboardButton(text=f'Да, все верно!', callback_data='yes_all_good')
confirm_kb = InlineKeyboardMarkup().add(yes_all_good)
confirm_kb.add(back)

without_info = InlineKeyboardButton(text=f'Без информации', callback_data='without_info')
info_kb = InlineKeyboardMarkup().add(without_info)

take_deal = InlineKeyboardButton(text=f'Взять заказ', callback_data='take_deal')
take_deal_kb = InlineKeyboardMarkup().add(take_deal)

good_deal = InlineKeyboardButton(text=f'Заказ выполнен', callback_data='good_deal')
bad_deal = InlineKeyboardButton(text=f'Отменить заказ', callback_data='bad_deal')
start_deal_kb = InlineKeyboardMarkup().add(good_deal)
start_deal_kb.add(bad_deal)

good_deal_d = InlineKeyboardButton(text=f'Заказ выполнен', callback_data='good_deal_d')
bad_deal_d = InlineKeyboardButton(text=f'Отменить заказ', callback_data='bad_deal_d')
start_driver_deal_kb = InlineKeyboardMarkup()
start_driver_deal_kb.add(bad_deal_d)

m_1 = KeyboardButton(text=f'1')
m_2 = KeyboardButton(text=f'2')
m_3 = KeyboardButton(text=f'3')
m_4 = KeyboardButton(text=f'4')
m_5 = KeyboardButton(text=f'5')

mark_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).insert(m_1)
mark_kb.insert(m_2)
mark_kb.insert(m_3)
mark_kb.insert(m_4)
mark_kb.insert(m_5)

pay_one_month = InlineKeyboardButton(text=f'Оплатить за 1 месяц', callback_data='pay_one_month')
pay_day = InlineKeyboardButton(text=f'Оплата по дням', callback_data='pay_day')
pay_one_month_kb = InlineKeyboardMarkup().add(pay_one_month)
pay_one_month_kb.add(pay_day)
pay_one_month_kb.add(back)

change_price = InlineKeyboardButton(text=f'Изменить цену', callback_data='change_price')
delete_deal = InlineKeyboardButton(text=f'Удалить', callback_data='delete_deal')
my_deal_kb = InlineKeyboardMarkup().add(change_price)
my_deal_kb.add(delete_deal)
my_deal_kb.add(back)


update_live = InlineKeyboardButton(text=f'Получать заявки на лету', callback_data='update_live')
update_live_kb = InlineKeyboardMarkup().add(update_live)
update_live_kb.add(back)


driver_finish_trip = InlineKeyboardButton(text=f'Поставить оценку', callback_data='driver_finish_trip')
driver_finish_trip_kb = InlineKeyboardMarkup().add(driver_finish_trip)
driver_finish_trip_kb.add(back)

drivers = InlineKeyboardButton(text=f'Водители', callback_data='drivers')
clients = InlineKeyboardButton(text=f'Клиенты', callback_data='clients')
admin_set = InlineKeyboardButton(text=f'Настройки', callback_data='admin_set')
find_user = InlineKeyboardButton(text=f'Найти человека', callback_data='find_user')

admin_kb = InlineKeyboardMarkup().add(find_user)
admin_kb.add(clients)
admin_kb.add(drivers)
admin_kb.add(admin_set)
admin_kb.add(taxi_driver, client)


price_small = InlineKeyboardButton(text=f'Процент коммисии', callback_data='price_small')
price_big = InlineKeyboardButton(text=f'Задать максимальную коммисию', callback_data='price_big')
payments_type = InlineKeyboardButton(text=f'Тип платежной системы', callback_data='payments_type')
dilay_time = InlineKeyboardButton(text=f'Время задержки сервера', callback_data='dilay_time')
pay_mod = InlineKeyboardButton(text=f'Платный мод', callback_data='pay_mod')

admin_set_kb = InlineKeyboardMarkup().add(pay_mod)
admin_set_kb.add(payments_type)
admin_set_kb.add(price_small)
admin_set_kb.add(price_big)
admin_set_kb.add(dilay_time)
admin_set_kb.add(back)


by_phone = InlineKeyboardButton(text=f'Найти по номеру телефона', callback_data='by_phone')
show_list = InlineKeyboardButton(text=f'Показать весь список', callback_data='show_list')
admin_black_kb = InlineKeyboardMarkup().add(by_phone)
admin_black_kb.add(show_list)


ban_client = InlineKeyboardButton(text=f'Изменить статус', callback_data='ban_client')
pay_time = InlineKeyboardButton(text=f'Изменить баланс', callback_data='pay_time')
send_msg = InlineKeyboardButton(text=f'Отправить сообщение', callback_data='send_msg')
admin_driver_kb = InlineKeyboardMarkup().add(ban_client)
admin_driver_kb.add(pay_time)
admin_driver_kb.add(send_msg)
admin_driver_kb.add(back)


ban_client_c = InlineKeyboardButton(text=f'Изменить статус', callback_data='ban_client_c')
send_msg_c = InlineKeyboardButton(text=f'Отправить сообщение', callback_data='send_msg_c')
admin_client_kb = InlineKeyboardMarkup().add(ban_client_c)
admin_client_kb.add(send_msg_c)
admin_client_kb.add(back)

ban_min = InlineKeyboardButton(text=f'Бан на минуты', callback_data='ban_min')
ban_hours = InlineKeyboardButton(text=f'Бан на часы', callback_data='ban_hours')
ban_days = InlineKeyboardButton(text=f'Бан на дни', callback_data='ban_days')
unban = InlineKeyboardButton(text=f'Разбанить', callback_data='unban')
admin_ban_kb = InlineKeyboardMarkup().add(ban_min)
admin_ban_kb.add(ban_hours)
admin_ban_kb.add(ban_days)
admin_ban_kb.add(unban)
admin_ban_kb.add(back)


y_kassa = InlineKeyboardButton(text=f'Ю-касса', callback_data='y_kassa')
sber_kassa = InlineKeyboardButton(text=f'Сбер-касса', callback_data='sber_kassa')
payments_type_kb = InlineKeyboardMarkup().add(y_kassa)
payments_type_kb.add(sber_kassa)
payments_type_kb.add(back)
