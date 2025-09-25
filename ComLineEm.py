import os
import sys
import socket
import re
class ComLineEm:
    def __init__(self):
        self.currentpath="~/"
        self.user = os.getlogin()
        self.hostname = socket.gethostname()    

    def run(self):
        print("Введите help для получения списка команд")
        print("-" * 50)
        
        while True:
            command_line = input(f"{self.user}@{self.hostname}:{self.currentpath}$ ").split()
            if not command_line:
                continue
            command= command_line[0]
            args=self.parse_command_line(command_line[1:])
            if command =='help' and not args:
                print("Доступные команды: ls, cd, exit")
                print("Для выхода введите 'exit'")
            elif command == 'exit' and not args:
                print("Выход из эмулятора")
                break            
            elif command == 'ls':
                self.ls(args)
            elif command == 'cd':
                self.cd(args)            
            else:
                print(f"Ошибка: неизвестная команда '{command}'")


    def ls(self, args):
        print(f"Команда: ls - показать список файлов и папок в директории")
        print(f"Аргументы: {args}")
    
    
    def cd(self, args):
        print(f"Команда: cd - сменить директорию")
        print(f"Аргументы: {args}")

    def parse_command_line(self, command_line):
        """Парсит командную строку с учетом кавычек"""
        pattern = r'\"([^\"]*)\"|\'([^\']*)\'|(\S+)'
        matches = re.findall(pattern, command_line)
        result = []

        for match in matches:
            # Выбираем непустую группу из трех возможных
            for group in match:
                if group:
                    result.append(group)
                    break

        return result
    
print ('args: ', sys.argv)



if __name__ == "__main__":
    shell = ComLineEm()
    shell.run()