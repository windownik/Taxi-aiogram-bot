from aiogram import types
from aiogram.types.message import ContentTypes

from main import dp
from modules import sqLite, workWF
from modules.dispatcher import bot, driver_Form
from modules.keyboards import pay_one_month_kb, taxi_driver_start_kb


# Pay for using
@dp.callback_query_handler(state=driver_Form.driver_first_menu, text='driver_pay')
async def start_menu(call: types.CallbackQuery):
    client = sqLite.read_all_values_in_db(table='drivers', telegram_id=call.from_user.id)
    if "None" in str(client[9]):
        lust_deal = '0'
    else:
        lust_deal = client[9]

    await call.message.edit_text(text=f'У вас на счету сейчас <b>{lust_deal} RUR</b>\n'
                                      'Введите сумму которую хотите положить. Балансс не может привышать 100 RUR',
                                 parse_mode='html')
    await driver_Form.driver_pay.set()


@dp.message_handler(state=driver_Form.driver_pay)
async def input_money(message: types.Message):
    if message.text.isdigit():
        payments_type = sqLite.read_all_value_bu_name(table='admin', name='*')[0][9]
        if str(payments_type) == 'y_kassa':
            pay_token = workWF.read_y_token()
        elif str(payments_type) == 'sber_kassa':
            pay_token = workWF.read_sber_token()
        price = f'{message.text}00'
        driver_balance = sqLite.read_all_values_in_db(table='drivers', telegram_id=message.from_user.id)[9]
        if (100 - int(driver_balance)) >= int(message.text):
            with open('document.pdf', 'rb') as file:
                await bot.send_document(chat_id=message.from_user.id, document=file,
                                        caption='Оплачивая подписку вы соглашаетесь с правилами и условиями изложенными в '
                                                'данном документе')
            await bot.send_invoice(chat_id=message.from_user.id, title='Оплата за пользование ботом', currency='RUB',
                                   description=f'Вы ложите {message.text} RUR на свой счет в бот', payload='bot_pay',
                                   provider_token=pay_token, start_parameter='bot_pay',
                                   prices=[{"label": 'Руб', "amount": int(price)}])
            file.close()
            sqLite.insert_info(table='drivers', name='data', data=message.text,
                               telegram_id=message.from_user.id)
        else:
            await message.answer('Баланс не может превышать 100 RUR. Сумма пополнения должна быть меньше')
    else:
        await message.answer('Введите только цифры.')


# # Pay for using
# @dp.callback_query_handler(state=driver_Form.driver_pay, text='pay_one_month')
# async def start_menu(call: types.CallbackQuery):
#     price = f'{workWF.read_price().split("#")[0]}00'
#     y_token = workWF.read_y_token()
#     with open('document.pdf', 'rb') as file:
#         await bot.send_document(chat_id=call.from_user.id, document=file,
#                                 caption='Оплачивая подписку вы соглашаетесь с правилами и условиями изложенными в '
#                                         'данном документе')
#     await bot.send_invoice(chat_id=call.from_user.id, title='Оплата за 1 месяц пользования', currency='RUB',
#                            description=f'Оплата за 1 месяц пользования телеграм ботом', payload='month_pay',
#                            provider_token=y_token, start_parameter='month_pay',
#                            prices=[{"label": 'Руб', "amount": int(price)}])
#
#     file.close()
#
#
# # Pay for using
# @dp.callback_query_handler(state=driver_Form.driver_pay, text='pay_day')
# async def start_menu(call: types.CallbackQuery):
#     price = f'{workWF.read_price().split("#")[1]}'
#     await call.message.answer(f"Оплата за один день сейчас составляет <b>{price} RUR</b>\n"
#                               f"Введите количество дней которое вы хотите оплатить.\n"
#                               f"Только цифры", parse_mode='html')
#     await driver_Form.driver_for_day.set()
#
#
# @dp.message_handler(state=driver_Form.driver_for_day)
# async def pay_for_day(message: types.Message):
#     if message.text.isdigit():
#         y_token = workWF.read_y_token()
#         price = f'{workWF.read_price().split("#")[1]}00'
#         price_days = int(price) * int(message.text)
#         sqLite.insert_info(table='drivers', name='number', data=message.text,
#                            telegram_id=message.from_user.id)
#         with open('document.pdf', 'rb') as file:
#             await bot.send_document(chat_id=message.from_user.id, document=file,
#                                     caption='Оплачивая подписку вы соглашаетесь с правилами и условиями изложенными в '
#                                             'данном документе')
#         await bot.send_invoice(chat_id=message.from_user.id, title='Оплата за 1 месяц пользования', currency='RUB',
#                                description=f"Вы хотите заплатить за количество дней: {message.text}, "
#                                            f"это будет стоить {str(price_days)[:-2]} RUR", payload='days_pay',
#                                provider_token=y_token, start_parameter='days_pay',
#                                prices=[{"label": 'Руб', "amount": int(price_days)}])
#         file.close()
#
#     else:
#         await message.answer('Введите только числа')


@dp.pre_checkout_query_handler(state='*')
async def pre_check_query(pre_check: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_check.id, ok=True)


@dp.message_handler(state='*', content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def got_payment(message: types.Message):
    if message.successful_payment.invoice_payload == 'bot_pay':
        await bot.send_message(chat_id=message.from_user.id, text='Поздравляем вы пополнили свой счет на {} {}'.
                               format(message.successful_payment.total_amount / 100,
                                      message.successful_payment.currency),
                               parse_mode='Markdown')
        old_balance = sqLite.read_value_bu_name(table='drivers', name='pay_line', telegram_id=message.from_user.id)[0]
        if old_balance is None:
            old_balance = 0
        else:
            pass
        new_balance = int(old_balance) + int(message.successful_payment.total_amount / 100)
        client = sqLite.read_all_values_in_db(table='drivers', telegram_id=message.from_user.id)
        sqLite.insert_info(table='drivers', name='pay_line', data=int(new_balance),
                           telegram_id=message.from_user.id)
        await message.answer(text=f'Добрый день <b>{client[2]}</b>. Твой рейтинг <b>{client[6]}</b>. \n'
                                  f'Чем могу помочь?',
                             reply_markup=taxi_driver_start_kb(), parse_mode='html')
        await driver_Form.driver_first_menu.set()

    # elif message.successful_payment.invoice_payload == 'days_pay':
    #     days = sqLite.read_value_bu_name(table='drivers', name='number', telegram_id=message.from_user.id)[0]
    #     await bot.send_message(chat_id=message.from_user.id, text='Поздравляем вы оплатили {} дней подписки за {} {}'.
    #                            format(days, message.successful_payment.total_amount / 100,
    #                                   message.successful_payment.currency),
    #                            parse_mode='Markdown')
    #     old_pay_data = sqLite.read_value_bu_name(table='drivers', name='pay_line', telegram_id=message.from_user.id)[0]
    #     if old_pay_data == 'None':
    #         old_pay_data = str(datetime.datetime.now()).split('.')[0]
    #     else:
    #         pass
    #     if datetime.datetime.strptime(str(old_pay_data), "%Y-%m-%d %H:%M:%S") > datetime.datetime.now():
    #         today = datetime.datetime.strptime(str(old_pay_data), "%Y-%m-%d %H:%M:%S")
    #     else:
    #         today = datetime.datetime.now()
    #
    #     next_month_date = today + timedelta(days=int(days))
    #     client = sqLite.read_all_values_in_db(table='drivers', telegram_id=message.from_user.id)
    #     sqLite.insert_info(table='drivers', name='pay_line', data=str(next_month_date).split('.')[0],
    #                        telegram_id=message.from_user.id)
    #     await message.answer(text=f'Добрый день <b>{client[2]}</b>. Твой рейтинг <b>{client[6]}</b>. \n'
    #                               f'Чем могу помочь?',
    #                          reply_markup=taxi_driver_start_kb(), parse_mode='html')
    #     await driver_Form.driver_first_menu.set()
