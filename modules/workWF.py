
def write_pay_mod(status: str = "False"):
    with open('modules/pay_mod.txt', 'w') as file:
        file.write(status)
        file.close()


def read_pay_mod():
    with open('modules/pay_mod.txt', 'r') as file:
        mod = file.read()
        file.close()
        return str(mod)


def write_price(price: str):
    with open('modules/price.txt', 'w') as file:
        file.write(price)
        file.close()


def read_price():
    with open('modules/price.txt', 'r') as file:
        price = file.read()
        file.close()
        return str(price)


def write_y_token(token: str):
    with open('modules/price.txt', 'w') as file:
        file.write(token)
        file.close()


def read_y_token():
    with open('modules/yo_token.txt', 'r') as file:
        token = file.read()
        file.close()
        return str(token)


def write_sber_token(token: str):
    with open('modules/sber_token.txt', 'w') as file:
        file.write(token)
        file.close()


def read_sber_token():
    with open('modules/sber_token.txt', 'r') as file:
        token = file.read()
        file.close()
        return str(token)
