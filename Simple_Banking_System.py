import random
import sqlite3


class Database(object):

    cards = """
    CREATE TABLE IF NOT EXISTS card (
        id INTEGER PRIMARY KEY,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0
    )"""

    def __init__(self, filename, contents):

        self.conn = sqlite3.connect(filename)
        self.cursor = self.conn.cursor()
        self.cursor.execute(contents)
        self.conn.commit()

    def get_all_card_numbers(self):
        card_numbers = []

        num_tuple = self.cursor.execute(f"""
            SELECT number 
            FROM card""").fetchall()

        for item in num_tuple:

            card_numbers.append(item[0])

        return card_numbers

    def check_pin(self, card_number, pin):

        correct_pin = self.cursor.execute(f"""
                    SELECT pin 
                    FROM card 
                    WHERE number = {card_number}""").fetchone()[0]

        return pin == correct_pin

    def get_card_balance(self, card_number):

        return self.cursor.execute(f"""
            SELECT balance 
            FROM card 
            WHERE number = {card_number}""").fetchone()[0]

    def add_income(self, card_number, amount):

        self.cursor.execute(f"""
            UPDATE card
            SET balance = balance + {amount}
            WHERE number = {card_number}""")
        self.conn.commit()

    def transfer_money(self, card_number_from, amount, card_number_to):

        if amount > self.get_card_balance(card_number_from):

            print("Not enough money!")

        else:

            self.cursor.execute(f"""
                        UPDATE card
                        SET balance = balance - {amount}
                        WHERE number = {card_number_from}""")
            self.cursor.execute(f"""
                                UPDATE card
                                SET balance = balance + {amount}
                                WHERE number = {card_number_to}""")
            self.conn.commit()

    def delete_account(self, card_number):

        self.cursor.execute(f"""
                    DELETE FROM card 
                    WHERE number = {card_number}""")
        self.conn.commit()


database = Database('card.s3db', Database.cards)


def generate_number():

    try:

        last_card_number = database.cursor.execute(f"""
                SELECT number
                FROM card
                ORDER BY id DESC
                LIMIT 1""").fetchone()[0]

        last_card_number = int(last_card_number) // 10 + 1

        number = list(map(int, str(last_card_number)))

    except TypeError:

        number = list(map(int, "400000000000000"))

    numbers_sum = 0

    for i in range(len(number)):

        val = number[i]

        if i % 2 == 0:
            val *= 2

        numbers_sum += val if val < 10 else val - 9

    checksum = ((numbers_sum // 10 + 1) * 10 - numbers_sum) % 10
    number.append(checksum)
    number = map(str, number)
    card_number = "".join(number)

    return card_number


def check_number(card_number):

    number = list(map(int, card_number[:-1]))

    numbers_sum = 0

    for i in range(len(number)):

        val = number[i]

        if i % 2 == 0:
            val *= 2

        numbers_sum += val if val < 10 else val - 9

    checksum = ((numbers_sum // 10 + 1) * 10 - numbers_sum) % 10

    return checksum == int(card_number[-1])


def generate_card():

    card_number = generate_number()
    card_pin = "".join([str(random.randint(0, 9)) for _ in range(4)])
    balance = 0

    database.cursor.execute(f"""
                    INSERT INTO card
                        (number,
                        pin,
                        balance)
                    VALUES
                        ({card_number}, 
                        {card_pin}, 
                        {balance})
                    ;""")
    database.conn.commit()

    return [card_number, card_pin]


running = True
logged = False
logged_card_number = None


def get_input():

    global running, logged, logged_card_number

    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")

    command = input()

    print()

    if command == "1":

        requisites = generate_card()

        print(f"""Your card has been created
Your card number:
{requisites[0]}
Your card PIN:
{requisites[1]}
""")

    elif command == "2":

        card_number = input("Enter your card number:\n")
        card_pin = input("Enter your PIN:\n")

        print()

        if card_number in database.get_all_card_numbers() and database.check_pin(card_number, card_pin):

            logged = True
            logged_card_number = card_number

            print("You have successfully logged in!")
            print()

        else:

            print("Wrong card number or PIN!")
            print()

    if command == "0":

        print("Bye!")

        running = False


def get_input_logged():

    global running, logged, logged_card_number

    print("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit""")

    command = input()

    print()

    if command == "1":

        print(f"Balance: {database.get_card_balance(logged_card_number)}")
        print()

    elif command == "2":

        income = input("Enter income:\n")

        database.add_income(logged_card_number, income)

        print("Income was added!\n")

    elif command == "3":

        print("Transfer\n")
        transfer_to = input("Enter card number:\n")

        if logged_card_number == transfer_to:

            print("You can't transfer money to the same account!\n")

        elif not check_number(transfer_to):

            print("Probably you made a mistake in the card number. Please try again!\n")

        elif transfer_to not in database.get_all_card_numbers():

            print("Such a card does not exist.\n")

        else:

            amount = int(input("Enter how much money you want to transfer:\n"))
            database.transfer_money(logged_card_number, amount, transfer_to)
            print("Success!\n")

    elif command == "4":

        database.delete_account(logged_card_number)
        logged = False
        logged_card_number = None

        print("The account has been closed!\n")

    elif command == "5":

        logged = False
        logged_card_number = None

        print("You have successfully logged out!\n")

    elif command == "0":

        print("Bye!")

        running = False


def run():

    while running:

        if not logged:

            get_input()

        else:

            get_input_logged()


run()