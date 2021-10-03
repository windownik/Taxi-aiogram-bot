import sqlite3


# Пользователь проверяет все данные о себе по базе данных
def read_all_values_in_db(table: str, telegram_id: int, *, id_name: str = 'telegram_id'):
    connect = sqlite3.connect('modules/database.db')
    curs = connect.cursor()
    for data in curs.execute(f'SELECT * FROM {table} WHERE {id_name}= "{telegram_id}"'):
        return data
    connect.close()


# Пользователь проверяет себя по базе данных
def read_value_bu_name(
        name: str,
        table: str,
        telegram_id: int):
    connect = sqlite3.connect('modules/database.db')
    curs = connect.cursor()
    for data in curs.execute(f'SELECT {name} FROM {table} WHERE telegram_id ="{telegram_id}"'):
        return data
    connect.close()


# Пользователь проверяет себя по базе данных
def read_all_value_bu_name(
        name: str,
        table: str):
    connect = sqlite3.connect('modules/database.db')
    curs = connect.cursor()
    curs.execute(f'SELECT {name} FROM {table}')
    data = curs.fetchall()
    return data


# Создаем первую запись в бд о пользователе в таблице users
def insert_first_note(table: str, telegram_id: int):
    connect = sqlite3.connect('modules/database.db')
    curs = connect.cursor()
    curs.execute(f"INSERT INTO {table} (telegram_id) VALUES ('{telegram_id}')")
    connect.commit()
    connect.close()


# Обновляем любые данные в любую таблицу в файле modules/database.db
def insert_info(
        table: str,
        telegram_id: int,
        name: str,
        data, *, id_name: str = 'telegram_id'):
    connect = sqlite3.connect('modules/database.db')
    curs = connect.cursor()
    curs.execute(f"UPDATE {table} SET {name}= ('{data}') WHERE {id_name}='{telegram_id}'")
    connect.commit()
    connect.close()


# Пользователь проверяет данные о себе по любым данным
def read_values_in_db_by_phone(table: str, name: str, data):
    connect = sqlite3.connect('modules/database.db')
    curs = connect.cursor()
    for d in curs.execute(f'SELECT * FROM {table} WHERE "{name}" = "{data}"'):
        return d
    connect.close()


def insert_first_pool(
        number: int
):
    connect = sqlite3.connect('modules/database.db')
    curs = connect.cursor()
    curs.execute(f"INSERT INTO pools (number) VALUES ('{number}')")
    connect.commit()
    connect.close()


# Обновляем любые данные в таблице pools в файле modules/database.db
def insert_info_pool(
        number: int,
        name: str,
        date):
    connect = sqlite3.connect('modules/database.db')
    curs = connect.cursor()
    curs.execute(f"UPDATE pools SET {name}= ('{date}') WHERE number='{number}'")
    connect.commit()
    connect.close()


# Удаляем данные из таблицы
def delete_str(
        table: str,
        data,
        name: str = 'telegram_id'):
    connect = sqlite3.connect('modules/database.db')
    curs = connect.cursor()
    curs.execute(f"DELETE FROM '{table}' WHERE {name}={data}")
    connect.commit()
    connect.close()


# Созданм новую запись о тратах или доходах в бд в личной таблице
def insert_send_data(telegram_id: str,
                     text: str,
                     send_data: str,
                     *,
                     deal_id: int = 0):
    connect = sqlite3.connect('modules/database.db')
    curs = connect.cursor()
    curs.execute(f"INSERT INTO sender VALUES (?,?,?,?,?)",
                 (None, f'{telegram_id}', f'{text}', f'{send_data}', deal_id))
    connect.commit()
    connect.close()
