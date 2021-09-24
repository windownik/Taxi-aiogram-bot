from modules import sqLite
import datetime, calendar, time


def cleaner():
    while True:
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
        time.sleep(1190)