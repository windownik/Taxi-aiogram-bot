from aiogram import types
from aiogram.types import ContentType
from main import dp
from aiogram.dispatcher.filters import Text
import logging
from aiogram.dispatcher import FSMContext
from modules.keyboards import start_kb, admin_kb
from modules.dispatcher import bot, start_Form, client_Form, driver_Form, admin_Form
from modules import workWF, sqLite


# Start menu
@dp.message_handler(commands=['start'], state='*')
async def start_menu(message: types.Message):
    admin_id = sqLite.read_all_value_bu_name(table='admin', name='*')[0][1]
    if admin_id == message.from_user.id:
        await message.answer('Привет администратор. Чем тебе помочь', reply_markup=admin_kb)
        await admin_Form.admin_first_menu.set()
    else:
        await message.answer(text='Добрый день. Перед вами телеграм бот таксист. Здесь вы можите заказать такси.',
                             reply_markup=start_kb)
        await start_Form.first_menu.set()


# Start menu callback
@dp.callback_query_handler(state=admin_Form.admin_first_menu, text='back')
@dp.callback_query_handler(state=admin_Form.admin_send_msg_one_confirm, text='back')
@dp.callback_query_handler(state=admin_Form.admin_set_pay, text='back')
@dp.callback_query_handler(state=admin_Form.admin_set_confirm, text='back')
@dp.callback_query_handler(state=admin_Form.admin_send_msg_one, text='back')
@dp.callback_query_handler(state=admin_Form.admin_ban_time_confirm, text='back')
@dp.callback_query_handler(state=admin_Form.admin_ban_time, text='back')
@dp.callback_query_handler(state=admin_Form.admin_ban, text='back')
@dp.callback_query_handler(state=admin_Form.admin_send_msg_confirm, text='back')
@dp.callback_query_handler(state=admin_Form.admin_send_msg, text='back')
@dp.callback_query_handler(state=start_Form.first_menu, text='back')
@dp.callback_query_handler(state=driver_Form.driver_first_menu, text='back')
@dp.callback_query_handler(state=client_Form.client_first_menu, text='back')
async def start_menu_call(call: types.CallbackQuery):
    admin_id = sqLite.read_all_value_bu_name(table='admin', name='*')[0][1]
    if admin_id == call.from_user.id:
        await call.message.edit_text('Привет администратор. Чем тебе помочь', reply_markup=admin_kb)
        await admin_Form.admin_first_menu.set()
    else:
        await call.message.edit_text(text='Добрый день. Перед вами телеграм бот таксист. Здесь вы можите заказать '
                                          'такси.', reply_markup=start_kb)
        await start_Form.first_menu.set()


# Help menu
@dp.message_handler(commands=['help'], state='*')
async def start_menu(message: types.Message):
    await message.answer(text='Привет! Ты попал в Телеграм бот для подачи заявки на заказ выездного бара.\n'
                              'Этот бот поможет заполнить форму с простыми вопросами. \n'
                              'После заполнения формы ты можешь проверить данные своего мероприятия в '
                              'соответствующем меню.\nРедактировать данные заявки к сожелению нельзя '
                              '(возможно появится в будущем), но зато заявку можно удалить и создать заново.\n'
                              'Для отмены всех действий в любой момент нажмите /cancel')


# Cancel all process
@dp.message_handler(state='*', commands=['cancel'])
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    await message.reply('Процес отменен. Все данные стерты. Что бы начать все с начала нажми /start',
                        reply_markup=types.ReplyKeyboardRemove())
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()


# Pay mod
@dp.message_handler(state='*', commands=['payments'])
async def cancel_handler(message: types.Message):
    await message.answer('Для включения платного мода нажмите /pay_on\n'
                         'Для отключения платного мода нажмите /pay_off\n'
                         'Для выхода нажмите /cancel')
    await start_Form.pay_menu.set()


# Pay mod on
@dp.message_handler(state=start_Form.pay_menu, commands=['pay_on'])
async def cancel_handler(message: types.Message):
    workWF.write_pay_mod(status="True")
    await message.answer('Платный мод ВКЛЮЧЕН\n'
                         'Для выхода нажмите /cancel')
    await start_Form.pay_menu.set()


# Pay mod off
@dp.message_handler(state=start_Form.pay_menu, commands=['pay_off'])
async def cancel_handler(message: types.Message):
    workWF.write_pay_mod()
    await message.answer('Платный мод ОТКЛЮЧЕН\n'
                         'Для выхода нажмите /cancel')
    await start_Form.pay_menu.set()


# Take data base
@dp.message_handler(commands=['take_db'], state='*')
async def start_menu(message: types.Message):
    chat_id = message.from_user.id
    with open('modules/database.db', 'rb') as file:
        await bot.send_document(chat_id=chat_id, document=file, caption='Отправил')

    await start_Form.first_menu.set()


# Set price
@dp.message_handler(commands=['price'], state='*')
async def start_menu(message: types.Message):
    price = workWF.read_price()
    await message.answer(f'Ценник сейчас составляет <b>{price}</b> RUR. \n'
                         f'Введиет новый ценник в RUR в формате (цена за месяц)<b>#</b>(цена за день).\n'
                         f'Только в таком формате\n\n'
                         f'Для отмены нажмите /cancel', parse_mode='html')
    await start_Form.set_price.set()


# Set price
@dp.message_handler(state=start_Form.set_price)
async def cancel_handler(message: types.Message):
    if '#' in message.text:
        workWF.write_price(price=message.text)
        await message.answer(f'Ценник установлен в размере {message.text} RUR\n'
                             f'Для отмены нажмите /cancel или /start')
        await start_Form.pay_menu.set()
    else:
        await message.answer('Вы пропустили знак   #')


# Set admin
@dp.message_handler(commands=['set_admin'], state='*')
async def start_menu(message: types.Message):
    await message.answer(f'Отправьте мне телеграм ID нового администратора\n'
                         f'Для отмены нажмите /cancel или /start')
    await start_Form.set_admin.set()


# Set admin
@dp.message_handler(state=start_Form.set_admin)
async def cancel_handler(message: types.Message):
    if message.text.isdigit():
        sqLite.insert_info(table='admin', name='telegram_id', data=int(message.text), telegram_id=1, id_name='id')
        await message.answer(f'Новый админ задан\n'
                             f'Для отмены нажмите /cancel или /start')
        await start_Form.pay_menu.set()
    else:
        await message.answer('Введите только цифры')


# Set doc
@dp.message_handler(commands=['set_doc'], state='*')
async def start_menu(message: types.Message):
    await message.answer(f'Отправьте мне новый документ договора\n'
                         f'Для отмены нажмите /cancel или /start')
    await start_Form.set_doc.set()


# Set doc
@dp.message_handler(content_types=ContentType.DOCUMENT, state=start_Form.set_doc)
async def photo_handler(message: types.Message):
    await message.document.download(f'document.pdf')
    await message.answer('Файл загужен\n'
                         f'Для отмены нажмите /cancel или /start')
