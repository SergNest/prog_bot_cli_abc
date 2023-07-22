import contextlib
from collections import UserDict
from datetime import date
import pickle
from prettytable import PrettyTable
from termcolor import colored, cprint
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from record import Record 
from field import *
import os
from abc import ABC, abstractmethod

commands = ['add', 'phones', 'show_all', 'next', 'del_phone', 'del_contact', 'edit_contact', 'search', 'birthday_in_days', 'help', 'exit']
path_to_db = 'db.bin'


class IntentCompleter(Completer):
    def __init__(self, commands):
        super().__init__()
        self.intents = commands

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        word_before_cursor = text_before_cursor.split()[-1] if text_before_cursor else ''

        for intent in self.intents:
            if intent.startswith(word_before_cursor):
                yield Completion(intent, start_position=-len(word_before_cursor))

class AddressBook(ABC, UserDict):
    def __init__(self, data={}):
        self.data = data
        self.index = 0
        self.__iterator = None

    @abstractmethod
    def write_data(self):   
        pass

    @abstractmethod
    def read_data(self):        
        pass

    @abstractmethod
    def add_record(self, record):
        pass

    @abstractmethod
    def show_phones(self, args):
        pass
    
    @abstractmethod
    def iterator(self):
        pass

    @abstractmethod
    def search_in(self, args):
        pass

    @abstractmethod
    def add_contact(self, args):
        pass

    @abstractmethod
    def delete_contact(self, contact_name):
        pass

    @abstractmethod
    def edit_contact(self, contact_name):
        pass

    @abstractmethod
    def birthday_in_days(self, args):
        pass

    @abstractmethod
    def show_all_cont(self):
        pass


class ConcreteAddressBook(AddressBook):
        
    def write_data(self):   
        with open(path_to_db, 'wb') as file: 
            pickle.dump(self.data, file)
    
    def read_data(self):        
        with open(path_to_db, 'rb') as file:
            self.data = pickle.load(file)

    def add_record(self, record):
        self.data[record.name.value] = record

    def show_phones(self, args):
        if args:
            if args[0] not in self.data.keys():
                return f'Контакт {args[0]} відсутній'
            for i, j in self.data.items():
                if args[0] == i:
                    return f'Контакт: {args[0]} номери: {str(j.phones)[1:-1]}'
        return "Введіть ім'я контакту"

    def iterator(self):
        if not self.__iterator:
            self.__iterator = iter(self)
        return self.__iterator

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.data):
            self.index = 0
            raise StopIteration
        else:
            result = list(self.data)[self.index]
            self.index += 1
            return result

    def search_in(self, args):
        search_result = []
        for i, j in self.data.items():
            if args[0] in str(self.data[i]):
                search_result.append(self.data[i])
            else:
                for j in list(self.data[i].phones):
                    if args[0] in str(j):
                        search_result.append(self.data[i])
                        break
        x = PrettyTable(align='l')    # ініціалізуєм табличку, вирівнюєм по лівому краю 
        x.field_names = [colored("Ім'я", 'light_blue'),colored("Телефон", 'light_blue'),colored("Пошта", 'light_blue'),colored("День народження", 'light_blue'),colored("Адреса", 'light_blue')]
        for values in search_result:
            a = ''.join(f'{i}\n' for i in values.phones)
            x.add_row([colored(f"{values.name}","blue"),colored(f"{a}","blue"), colored(f"{values.email}","blue"), colored(f"{values.birthday}","blue"), colored(f"{values.address}","blue")])
        return x
        
        
    def add_contact(self, args):
        contact_name = args[0]
        if contact_name in phone_book.data:
            return "Такий контакт вже існує"

        record = Record(Name(contact_name))
        field_mapping = {
            "bd=": record.add_birthday,
            "em=": record.add_mail,
            "addr=": record.add_address,
        }

        for item in args[1:]:
            for prefix, field_method in field_mapping.items():
                if item.startswith(prefix):
                    value = item.split("=")[1]
                    field_method(value)
                    break
            else:
                record.add_phone(Phone(item))

        phone_book.add_record(record)
        return f'Контакт : {contact_name}, створений'

    def delete_contact(self, contact_name):
       
        contact_to_delete = self.data.get(contact_name)
        if contact_to_delete:
            del self.data[contact_name]
            return "Контакт успішно видалений"
        else:
            return "Контакт не знайдено"

    def edit_contact(self, contact_name):
        
        contact_to_change = self.data.get(contact_name)
        if contact_to_change:
            list_commands = ['done']
            cprint ("+---------------------+", 'blue')
            cprint ("Доступні поля для зміни", 'blue')
            for key, value  in contact_to_change.__dict__.items():
                print(f'{key} - {value}')
                list_commands.append(key)
            cprint ("+---------------------+", 'blue')
            session = PromptSession(auto_suggest=AutoSuggestFromHistory(), completer=IntentCompleter(list_commands))
            while True:
                input = session.prompt('Введіть перші літери поля яке хочете змінити, або "done" щоб завершити редагування > ')
                input = input.split(' ')[0].strip()
                if input == 'done':
                    break
                else:
                    session2 = PromptSession(auto_suggest=AutoSuggestFromHistory(), completer=IntentCompleter([]))
                    if input == 'phones':
                        if len(contact_to_change.phones):
                            text = f'Введіть старий і новий номер у форматі "380XXXXXXXXX" > '
                            new_value = session2.prompt(text)
                            input_phone = new_value.split(' ')
                            contact_to_change.change_phone(input_phone[0], input_phone[1])
                        else:
                            text = f'Введіть номер телефону який хочете додати у форматі "380XXXXXXXXX" > '
                            new_value = session2.prompt(text)
                            input_phone = new_value.split(' ')
                            contact_to_change.add_phone(Phone(input_phone[0]))
                    elif input == 'email':
                        text = f'Введіть новий email y форматі "first@domen.com" > '
                        new_value = session2.prompt(text)
                        input_phone = new_value.split(' ')
                        contact_to_change.change_email_iner(Email(input_phone[0]))
                    elif input == 'birthday':
                        text = f'Введіть дату народження у форматі "День/Місяць/Рік" > '
                        new_value = session2.prompt(text)
                        input_phone = new_value.split(' ')
                        contact_to_change.change_birthday_in(Birthday(input_phone[0]))
                    elif input == 'address':
                        text = f'Введіть нову адресу > '
                        new_value = session2.prompt(text)
                        contact_to_change.change_address_iner(Address(new_value))
                    elif input == 'name':
                        cprint('Вибачте зміна імені не доступна', 'red')

            cprint ("Контакт успішно оновлено", 'green')
        else:
            cprint ("Контакт не знайдено", 'red')
    
    def birthday_in_days(self, args): #add 82-113
        not_cont_with_birthday=True
        for key, value in self.data.items():
            if value.birthday:
                number = int(args[0])
                today = date.today()
                birthday_this_year = date(today.year, value.birthday.value.month, value.birthday.value.day)
                birthday_next_year = date(today.year + 1, value.birthday.value.month, value.birthday.value.day)
                if birthday_this_year >= today:
                    delta = birthday_this_year - today
                    delta_plus = abs(delta.days)
                    if number >= delta_plus:
                        print(f"У {key} день народження через {delta_plus} днів ")
                        not_cont_with_birthday = False
                        continue
                if birthday_next_year >= today:
                    delta = birthday_next_year - today
                    delta_plus = abs(delta.days)
                    if number >= delta_plus:
                        print(f"У {key} день народження через {delta_plus} днів ")
                        not_cont_with_birthday = False
                        continue
        if not_cont_with_birthday:
            cprint(f"В цей проміжок немає днів народження", 'red')

    def show_all_cont(self):
        x = PrettyTable(align='l')    # ініціалізуєм табличку, вирівнюєм по лівому краю 
        x.field_names = [colored("Ім'я", 'light_blue'),colored("Телефон", 'light_blue'),colored("Пошта", 'light_blue'),colored("День народження", 'light_blue'),colored("Адреса", 'light_blue')]
        for i, values in self.data.items():
            a = ''.join(f'{i}\n' for i in values.phones)
            x.add_row([colored(f"{i}","blue"),colored(f"{a}","blue"), colored(f"{values.email}","blue"), colored(f"{values.birthday}","blue"), colored(f"{values.address}","blue")])
        return x    

def show_help():      
    x = PrettyTable(align='l')    # ініціалізуєм табличку, вирівнюєм по лівому краю 

    x.field_names = [colored("Робота з адресною книгою, наразі доступні наступні команди:", 'light_blue')]
    for a, i in enumerate(commands, start=1):
        x.add_row([colored(f"{a}. {i}","blue")])
   
    return x # показуємо табличку

def input_error(func):
    def inner(*args):
        try: 
            return func(*args)  
        except KeyError:
            print('Enter user name.')
        except ValueError:
            cprint('Некоректні данні', 'red')
        except IndexError:
            cprint('Введіть правильну кількість аргументів', 'red')
        except TypeError:
            print('Use commands')
        except StopIteration:
            cprint('Останній контакт!', 'blue')
    return inner

@input_error
def add_contact(args):   
    cprint(phone_book.add_contact(args), 'blue')
   

@input_error     
def change_contact(args):  
    record = phone_book.data.get(args[0]) 
    if args[0] not in phone_book.keys():  
        record.add_phone(args)  
        return f'{args[0]} added to contacts!'
    elif len(args) == 3:          
        for key, values in phone_book.items():            
            if key == args[0] and args[1] in str(values.phones):
                record.change_phone(Phone(args[1]), Phone(args[2]))
    else:
        return f"Для зміни номеру контакта введіть введіть у наступній послідовності:\n Ім'я старий номер новий номер"

@input_error
def change_email(args):
    if args[0] not in phone_book.keys():
        return f'{args[0]} Такого контакту неіснуе!'
    record = phone_book.data.get(args[0])
    for key in phone_book.keys():            
        if key == args[0]:
            record.change_email_iner(Email(args[1]))

@input_error
def change_birthday(args): 
    if args[0] not in phone_book.keys():
        return f'{args[0]} Такого контакту неіснуе!'
    record = phone_book.data.get(args[0])
    for key in phone_book.keys():            
        if key == args[0]:
            record.change_birthday_in(Birthday(args[1]))
        return f'День народження змінено > {record}'

@input_error
def del_phone(args):
    record = phone_book.data.get(args[0])
    for key in phone_book.keys():            
            if key == args[0]:
                record.delete_phone(args[1])
                return f'Phone {args[1]} was deleted from {key} contact!'

def search(args):
    return phone_book.search_in(args)

@input_error
def del_record(args):
    return phone_book.delete_contact(args[0])

@input_error
def edit_contact(args):
    return phone_book.edit_contact(args[0])

@input_error
def show():
   cprint(next(phone_book.iterator()), 'green')

@input_error
def birthday_in_days(args):
    return phone_book.birthday_in_days(args)

phone_book = ConcreteAddressBook({})

@input_error
def main():
    
    if os.path.exists(path_to_db):        
            phone_book.read_data() 
        
    print(show_help())
    session = PromptSession(auto_suggest=AutoSuggestFromHistory(), completer=IntentCompleter(commands))
    while True:
        b = session.prompt('Введіть потрібну вам команду > ').strip() 
        c = ['exit']
        d, *args = b.split(' ')
        with contextlib.suppress(ValueError):
            if int(d):
                for a, i in enumerate(commands, start=1):
                    if a == int(d):
                        d = i

        if b in c or d in c or d == '0':
            phone_book.write_data()
            cprint('See you soon!','green')
            break
        elif b == 'show_all' or d == 'show_all':
            print(phone_book.show_all_cont())
        elif b == 'help' or d == 'help':
            print(show_help())
        elif b == 'next' or d == 'next':
            show()
        elif d == 'birthday_in_days':
            birthday_in_days(args)
        elif b in commands:
            cprint('Enter arguments to command', 'red')
        elif d == 'add':
            add_contact(args)
        elif d == 'phones':
            print(phone_book.show_phones(args))
        elif d == 'del_phone':
            print(del_phone(args))
        elif d == 'search':
            print(search(args))
        elif d == 'del_contact':
            cprint(del_record(args), 'green')
        elif d == 'edit_contact':
            edit_contact(args)
        else:
            cprint('Please enter correct command. Use command "help" to see more.', 'red')


if __name__ == "__main__":
    main()