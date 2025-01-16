from datetime import datetime, date, timedelta
from collections import UserDict
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
     def __init__(self, name):
        super().__init__(name)

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:                                     # check for validation of input
            raise ValueError
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        
        try:                                                                            # validation of the input date format
            datetime.strptime(value, "%d.%m.%Y")  
        except ValueError:
            raise ValueError ("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)  

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)


    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        p = self.find_phone(old_phone)
        if p:                                                                           #  if the old phone was found, remove it and add new phone
            self.add_phone(new_phone)
            self.remove_phone(old_phone)
        else:
            raise ValueError("Old phone number is not found")                                                           #  if the old phone wasn't found
            
    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]  

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p                                                                # return the matching Phone object
        return None                                                                     # return None if phone is not found

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"



class AddressBook(UserDict):
    def save_data(book, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(book, f)

    def load_data(filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook()


    def add_record(self, record):                                                       # add a Record item to the address book
        self.data[record.name.value] = record

    def find(self, name):                                                               # find and return a Record item by name
        return self.data.get(name) 

    def delete(self, name):                                                             # delete a Record item by name
        if name in self.data:
            del self.data[name]
       
    def get_upcoming_birthdays(self, days=7):
        def find_next_weekday(start_date, weekday=0):                   
            days_ahead = weekday - start_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return start_date + timedelta(days=days_ahead)

        upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():                                               # iterate through the Record objects
            if record.birthday:                                                         # check if the record has a birthday
                parsed_birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                birthday_this_year = parsed_birthday.replace(year=today.year)           # birthday in the current year
                if birthday_this_year < today:                                          # if the birthday already passed this year, use the next year
                    birthday_this_year = parsed_birthday.replace(year=today.year + 1)

                if 0 <= (birthday_this_year - today).days <= days:                      # check if the birthday is within the range
                    if birthday_this_year.weekday() >= 5:                               # if birthday falls on a weekend
                        birthday_this_year = find_next_weekday(birthday_this_year, 0)   # moving it to Monday
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": birthday_this_year.strftime('%d.%m.%Y')

                    })

        return upcoming_birthdays

    def __str__(self):
        return "\n".join([str(record) for record in self.data.values()])                    #output of records
   

def input_error(func):                                                                      #decorator, function for errors handling
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Enter the argument for the command"
        except ValueError:
            return "Incorrect input: please, enter name, phone number in 10 digits format or date in  DD.MM.YYYY format." 
        except KeyError:                            
            return "Enter the right name please."
        except Exception as ex:
            return f"error {ex}"

    return inner
    
@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):                                                   # adding name and phone number to dictionare contacts
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

def change_contact(args, book: AddressBook):
    if len(args) < 3:                                                                       # validation for the input arguments
        return "Please enter the name, the old phone number, and the new phone number."
    
    name, old_phone, new_phone = args  # Unpack the arguments
    record = book.find(name)                                                                 # find the contact by name

    if record:                                                                               # if the contact exists
        record.edit_phone(old_phone, new_phone)                                          # use the edit_phone method
        return f"Updated {name}'s phone: {old_phone} -> {new_phone}"
    else:
        return f"Contact with name {name} not found. Enter the correct name, please."


@input_error
def show_phone(args, book: AddressBook):                                                        # getting phone number for specified contact
    name = args[0]  
    record = book.find(name)  
    if record:
        return f"{record.name.value}: {', '.join(phone.value for phone in record.phones)}"
    else:
        return f"Contact with name {name} not found."
    
@input_error
def show_all(_, book):                                                                          # shows all items in dictionary contacts
    return "\n".join(
        f"{record.name.value}: {', '.join(phone.value for phone in record.phones)}, birthday: {record.birthday.value if record.birthday else 'N/A'}"
        for record in book.data.values()
    )

@input_error
def add_birthday(args, book):
    if len(args) < 2:
        return "Please enter the name and the birthday (in DD.MM.YYYY format)."
    
    name, birthday = args  
    record = book.find(name)                                                                    # find the record by name

    if record:                                                                                  # if the record exists
        record.add_birthday(birthday)                                                       # add the birthday using Record's method
        return f"Birthday {birthday} has been added to {name}."
    else:
        return f"Contact with name {name} not found. Enter the correct name, please."

@input_error
def show_birthday(args, book):
    name, *_ = args  
    record = book.find(name)  

    if record is None:
        return f"Contact with name {name} not found."

    if record.birthday is None:
        return f"{name} does not have a birthday set."
    
    return f"{name}'s birthday is {record.birthday.value}."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No upcoming birthdays in the next week."

    result = "Upcoming birthdays:\n"
    for item in upcoming:
        result += f"{item['name']}'s birthday is on {item['birthday']}\n"
    
    return result


def main():
    book = AddressBook.load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            book.save_data()
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(None, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")
if __name__ == "__main__":
    main()