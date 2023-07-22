from field import *
from datetime import date

class Record:
    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None, email: Email = None, address: Address = None):
        self.name = name
        self.phones = []
        self.birthday = None
        self.email = None
        self.address = None

    def __str__(self):
        return f'{self.name} {self.phones} {self.birthday} {self.email} {self.address}'

    def __repr__(self):
        return f'{self.name} {self.phones} {self.birthday} {self.email} {self.address}'


    def add_phone(self, phone: Phone):
        self.phones.append(phone)
    
    def add_birthday(self, birthday: Birthday):
        self.birthday = birthday
    
    def add_mail(self, email: Email):
        self.email = email

    def add_address(self, address: Address):
        self.address = address
    
    def show_phones(self):
        return self.phones
    
    def show_birthday(self):
        return self.birthday
    
    def show_email(self):
        return self.email

    def change_phone(self, old_phone : Phone, new_phone : Phone):
        for phone in self.phones:
            if phone == old_phone:
                self.add_phone(new_phone)
                self.phones.remove(phone)
                return f'Номер {phone} видалено.'

    def change_birthday_in(self, birthday: Birthday):
        self.birthday = birthday
        return f'Дата народження змінена'
    
    def change_email_iner(self, email: Email):
        self.email = email
        return f'{self.email}'
    
    def change_address_iner(self, address: Address):
        self.address = address
        return f'{self.address}'

    def delete_phone(self, new_phone):
        for phone in self.phones:
            if phone == new_phone:
                self.phones.remove(phone)
                
    def days_to_birthday(self):
        if not self.birthday:
            return ' '
        today = date.today()
        birthday_this_year = date(today.year, self.birthday.value.month, self.birthday.value.day)
        if birthday_this_year >= today:
            delta = birthday_this_year - today
        else:
            delta = date(today.year + 1, self.birthday.value.month, self.birthday.value.day) - today
        return delta.days