from modules import sqLite
import datetime, calendar, time
import requests


def cleaner():
    today = datetime.datetime.now()
    data = sqLite.read_all_value_bu_name(table='connections', name='*')
    days = calendar.monthrange(today.year, (today.month - 1))[1]
    previous_month_date = today - datetime.timedelta(days=days)
    for i in data:
        deal_data = str(i[9]).split(' ')[0]
        if datetime.datetime.strptime(str(deal_data), "%Y-%m-%d") < previous_month_date:
            sqLite.delete_str(table='connections', data=i[0], name='id')
        else:
            pass


def sender():
    while True:
        with open('modules/telegram_token.txt', 'r') as file:
            telegram_token = file.read()
            file.close()
        API_link = f'https://api.telegram.org/bot{telegram_token}/'
        data = sqLite.read_all_value_bu_name(table='sender', name='*')
        time_now = datetime.datetime.now()
        for d in data:
            line_time = datetime.datetime.strptime(str(d[3]).split('.')[0], "%Y-%m-%d %H:%M:%S")
            if line_time < time_now:
                req_text = API_link + 'sendMessage?chat_id=' + str(d[1]) + '&text=' + str(d[2]) + '&reply_markup={"inline_keyboard":[[{"text":"Получать заявки на лету","callback_data":"update_live"}]]}'
                req_text_5min = API_link + 'sendMessage?chat_id=' + str(d[1]) + '&text=' + str(d[2]) + '&reply_markup={"inline_keyboard":[[{"text":"Изменить поездку","callback_data":"change_trip"}]]}'
                if '15 минут истекло' in str(d[2]):
                    try:
                        requests.post(req_text)
                    except:
                        time.sleep(1)
                        requests.post(req_text)
                elif 'Прошло 5 минут' in str(d[2]):
                    try:
                        status = sqLite.read_values_in_db_by_phone(table='connections', name='id', data=d[4])[6]
                        if 'active' in str(status):
                            try:
                                requests.post(req_text_5min)
                            except:
                                time.sleep(1)
                                requests.post(req_text_5min)
                    except:
                        pass
                else:
                    try:
                        requests.get(API_link + f'sendMessage?chat_id={d[1]}&text={d[2]}').json()
                    except:
                        time.sleep(1)
                        requests.get(API_link + f'sendMessage?chat_id={d[1]}&text={d[2]}').json()
                sqLite.delete_str(table='sender', name='id', data=d[0])
                time.sleep(0.1)
        time.sleep(5)
