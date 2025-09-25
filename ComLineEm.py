import os
import re
import socket
<<<<<<< HEAD
import re
=======
import argparse

>>>>>>> 144c9e7563a33ff61e4f0295ee7ad6bd7af4470c
class ComLineEm:
    def __init__(self, vfs_path=None, script_path=None):
        self.currentpath="~/"
        self.user = os.getlogin()
        self.hostname = socket.gethostname()
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.in_script_mode = False
        self.script_commands = []
        self.script_index = 0

    def run(self):

        if self.script_path:
            if not self.load_script():
                return
            self.in_script_mode = True

        print("Введите help для получения списка команд")
        print("-" * 50)
        
        while True:

            if self.in_script_mode:

                command_line = self.script_commands[self.script_index]
                self.script_index += 1
                
                if self.script_index == len(self.script_commands): self.in_script_mode=False

                print(f"{self.user}@{self.hostname}:{self.currentpath}$ {command_line}")

            else:
                try:
                    command_line = input(f"{self.user}@{self.hostname}:{self.currentpath}$ ")
                except (EOFError, KeyboardInterrupt):
                    print("\nВыход из эмулятора")
                    break

            if not command_line: continue

            command_line=self.parse_command_line(command_line)
            command= command_line[0]
<<<<<<< HEAD
            args=self.parse_command_line(command_line[1:])
=======
            args=command_line[1:]

>>>>>>> 144c9e7563a33ff61e4f0295ee7ad6bd7af4470c
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

            elif command =='echo':
                line=""
                for arg in args:
                    line+=arg+" "
                print(line)

            else:
                print(f"Ошибка: неизвестная команда '{command}'")
                if self.in_script_mode:
                    print("Аварийное завершение работы")
                    break

    def parse_command_line(self, command_line):
        if not command_line:
            return []
            
        pattern = r'\"([^\"]*)\"|\'([^\']*)\'|(\S+)'
        matches = re.findall(pattern, command_line)
        result = []

        for match in matches:
            for group in match:
                if group and group!=" ":
                    result.append(group.strip())
                    break

        return result
    
    def load_script(self):
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                self.script_commands = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            return True
        except FileNotFoundError:
            print(f"Эррорка: неправильный файл {self.script_path}")
            return False
        except Exception as e:
            print(f"Эррорка: неправильный скрипт {e}")
            return False
    
    def ls(self, args):
        print(f"Команда: ls - показать список файлов и папок в директории")
        print(f"Аргументы: {args}")
    
    
    def cd(self, args):
        print(f"Команда: cd - сменить директорию")
        print(f"Аргументы: {args}")

<<<<<<< HEAD
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
=======
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vfs', '-v')
    parser.add_argument('--script', '-s')
    return parser.parse_args()
>>>>>>> 144c9e7563a33ff61e4f0295ee7ad6bd7af4470c



if __name__ == "__main__":
    args=parse_arguments()
    print("Аргументы командной строки:")
    print(f"  VFS путь: {args.vfs}")
    print(f"  Скрипт: {args.script}")
    shell = ComLineEm(vfs_path=args.vfs, script_path=args.script)
    shell.run()