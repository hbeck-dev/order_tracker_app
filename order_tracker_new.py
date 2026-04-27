"""
Order Tracker
This program stores and formats any orders you wish to remember.
The program will:
- Collect order details from the user
- Store orders as dictionaries inside a list
- Save order data to order_history.txt
- Save prices to prices.txt
- Allow orders to be confirmed, edited, or cancelled
- Display orders in a readable manner
- Sort stored orders by cheapest or most expensive
"""

import datetime

# GLOBAL CONSTANTS
ORDERS = "order_history.txt" # stores all orders logged, doesn't update previous logs
PRICES = "prices.txt" # stores all item prices logged, updates previous logs when inputted price changes
DRINKS = ("Water", "Soda", "Lemonade", "Tea", "Coffee")

class Order:
    def __init__(self, name, location, main, side="", drink="", price=0.0):
        self.__name = name
        self.__location = location
        self.__main = main
        self.__side = side
        self.__drink = drink
        self.__price = price
    
    # Getters
    def get_name(self):
        return self.__name
    def get_location(self):
        return self.__location
    def get_main(self):
        return self.__main
    def get_side(self):
        return self.__side
    def get_drink(self):
        return self.__drink
    def get_price(self):
        return self.__price
    
    # Setters
    def set_name(self, name):
        self.__name = name.title()
    def set_location(self, location):
        self.__location = location
    def set_main(self, main):
        self.__main = main.upper()
    def set_side(self, side):
        self.__side = side.upper()
    def set_drink(self, drink):
        self.__drink = drink.upper()
    def set_price(self, price):
        if price < 0:
            raise ValueError("Price cannot be negative.")
        self.__price = price
    def update_price(self, amount):
        if self.__price + amount < 0:
            raise ValueError("Resulting price cannot be negative.")
        self.__price += amount
    def get_full_order(self):
        parts = [self.__main]
        if self.__side:
            parts.append(self.__side)
        if self.__drink:
            parts.append(self.__drink)
        return ", ".join(parts)

    def display(self):
        print("\nUSER ORDER:")
        print(f"NAME: {self.__name}")
        print(f"LOCATION: {self.__location}")
        print(f"ORDER: {self.get_full_order()}")
        print(f"TOTAL: ${self.__price:.2f}")



def menu():
    while True:
        print("Welcome to the Order Tracker!")
        print("-" * 25)
        choice = input("Type 1 to input a new order.\nType 2 to view a previous order. ")
        if choice != "1" and choice != "2":
            print("\nERROR: Please choose either 1 or 2.\n")
        else:
            break
    return choice

def user_info():
    name = input("Name: ").title()
    location = input("Where did you order from? ")
    return name, location

def order_and_price():
    total_price = 0.0
    full_order = 0.0
    try:
        main_item = input("Main item ordered: ").upper()
        combo = input("Was it a combo? (Y/N): ").upper()
        if combo == "Y":
            total_price = float(input("How much did the whole combo cost? "))
            
            full_order = (f"{main_item} COMBO")
        else:
            main_price = float(input("How much did the main item cost? "))
            side = input("Side? (leave blank if N/A): ").upper()
            if side != "":
                side_price = float(input("How much did the side cost? "))
            print(f"Typical drinks: {DRINKS}")
            drink = input("Drink? (Leave blank if N/A): ").upper()
            if drink != "":
                drink_price = float(input("How much did the drink cost? "))
            total_price = main_price + side_price + drink_price
            full_order = (f"{main_item}, {side}, {drink}")
    except ValueError:
        print("Error: Please do not enter anything other than numbers or decimals.")
    return total_price, full_order

def save_data_and_print(name, location, full_order, total_price):
    order = full_order.split(',')
    print(f"USER ORDER:")
    print(f"NAME: {name}\nLOCATION: {location}")
    print(f"ORDER: {order}")
    print(f"TOTAL: ${total_price:.2f}")

def save_to_file(timestamp_str, name, location, full_order, total_price):
    order_history = {
        timestamp_str: full_order
    }
    with open("order_history.txt", "a") as file:
        file.write(f"{timestamp_str}: {name} | {location} | {order_history[timestamp_str]} | ${total_price:.2f}\n")
    with open("prices.txt", "a") as file:
        file.write(f"{location} | {full_order} | ${total_price:.2f}\n")

def read_price_log():
    try:
        with open("prices.txt", 'r') as file:
            for line in file:
                parts_of_line = line.strip().split('|')
                location = parts_of_line[0].strip()
                full_order = parts_of_line[1].strip()
                total_price = parts_of_line[2].strip()
        return
    except FileNotFoundError: # prevents crash
        print("Error, file not found.")

def overwrite():
    try:
        with open("prices.txt", "r") as file:
            lines = file.readlines()
        if not lines:
            print("No previous data found.")
            return
        print("\nPrice Log:")
        for i, line in enumerate(lines, start=1):
            print(f"{i}. {line.strip()}")
        choice = int(input("\nPlease input the line # that you wish to update: "))
        selected_line = lines[choice - 1].strip().split("|")
        location = selected_line[0].strip()
        full_order = selected_line[1].strip()
        old_price = selected_line[2].strip()
        print(f"\nCurrent: {location} | {full_order} | {old_price}")
        try:
            new_price = float(input("Input a new price: "))
        except ValueError:
            print("Invalid price.")
            return
        lines[choice - 1] = f"{location} | {full_order} | ${new_price:.2f}\n"
        with open("prices.txt", "w") as file:
            file.writelines(lines)
        print("Price updated successfully!")
    except FileNotFoundError:
        print("Error: prices.txt not found.")

def main():
    while True:
        choice = menu()
        if choice == "1":
            name, location = user_info()
            print(f"Customer: {name} | Location: {location}")
            # 2. Data Collection Phase & 3. Calculation Phase
            total_price, full_order = order_and_price()
            # 4. Handoff Phase
            save_data_and_print(name=name, location=location, full_order=full_order, total_price=total_price)
            # Saving to file
            current_time = datetime.datetime.now()
            timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            save_to_file(timestamp_str=timestamp_str, name=name, location=location, full_order=full_order, total_price=total_price)
        else:
            overwrite()
main()