from termcolor import colored, cprint
from prettytable import PrettyTable
import Phone_Book, notes, clean
import os
from abc import ABC, abstractmethod

class UserInterface(ABC):
    @abstractmethod
    def show_message(self, message, color='white'):
        pass

    @abstractmethod
    def read_input(self):
        pass

class ConsoleInterface(UserInterface):
    def show_message(self, message, color='white'):
        cprint(message, color)

    def read_input(self):
        text = colored('Зробіть свій вибір > ', 'yellow')
        return input(text).lower().split(' ')

def show_greeting(ui):      
    x = PrettyTable(align='l')
    x.field_names = [colored("Вас вітає бот помічник, наразі доступні наступні модулі:", 'light_blue')]
    x.add_row([colored("1. Сортування файлів","blue")])     
    x.add_row([colored("2. Робота з адресною книгою","blue")])
    x.add_row([colored("3. Робота з нотатками","blue")])
    x.add_row([colored("0. Закінчити роботу програми","blue")])

    ui.show_message(str(x), 'blue')

def run(ui):    
    os.system('cls||clear')
    
    sorting = False
    addresbook = False
    notes_local = False
    
    while True:
        
        if not (sorting or addresbook or notes_local):
            show_greeting(ui)        
            answer = ui.read_input()
        
            try:
                if int(answer[0]) == 0:
                    ui.show_message("Good bye!", 'blue')
                    break
                if int(answer[0]) == 1:
                    sorting = True
                if int(answer[0]) == 2:
                    addresbook = True
                if int(answer[0]) == 3:
                    notes_local = True
            except ValueError as e:
                ui.show_message('Введіть будь ласка число від 0 до 3', 'red')

        if sorting:
            clean.main()
            sorting = False
        
        if addresbook:
            Phone_Book.main()
            addresbook = False
            
        if notes_local:
            notes.main()          
            notes_local = False

if __name__ == '__main__':
    console_ui = ConsoleInterface()
    run(console_ui)
