import os
import socket
import re
import argparse
import json
import base64

class VFS:
    def __init__(self, vfs_path):
        self.vfs_path = vfs_path
        self.filesystem = {}
        self.loaded = False
        
    def load(self):
        try:
            with open(self.vfs_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.filesystem = data
            self.loaded = True
            return True
           
        except FileNotFoundError as e:
            print(f"VFS файл не найден: {self.vfs_path}")
            return False
        
        except json.JSONDecodeError as e:
            print(f"Эррорка: {e}")
            return False
        
        except ValueError as e:
            print(f"Эррорка: {e}")
            return False
    
    def get_file_content(self, path):
        try:
            current = self.filesystem
            parts = path.strip('/').split('/')
            
            for part in parts:
                if part not in current:
                    return None
                current = current[part]
            
            if isinstance(current, dict):
                return None
            
            if isinstance(current, str) and current.startswith('base64:'):
                return base64.b64decode(current[7:]).decode('utf-8')
            
            elif isinstance(current, str):
                return current
            
            else:
                return str(current)
                
        except Exception as e:
            print(f"Ошибка чтения файла {path}: {e}")
            return None
    
    def list_directory(self, path="/"):
        try:
            if path == "/":
                current = self.filesystem
            else:
                current = self.filesystem
                parts = path.strip('/').split('/')
                
                for part in parts:
                    if part not in current:
                        return None
                    current = current[part]
            
            if not isinstance(current, dict):
                return None
            
            return list(current.keys())
            
        except Exception as e:
            print(f"Ошибка чтения директории {path}: {e}")
            return None
    
    def path_exists(self, path):
        try:
            if path == "/":
                return True
                
            current = self.filesystem
            parts = path.strip('/').split('/')
            
            for part in parts:
                if part not in current:
                    return False
                current = current[part]
            
            return True
            
        except Exception:
            return False
    
    def is_directory(self, path):
        try:
            if path == "/":
                return True
                
            current = self.filesystem
            parts = path.strip('/').split('/')
            
            for part in parts:
                if part not in current:
                    return False
                current = current[part]
            
            return isinstance(current, dict)
            
        except Exception:
            return False


class ComLineEm:
    def __init__(self, vfs_path=None, script_path=None):
        self.currentpath="/"
        self.user = os.getlogin()
        self.hostname = socket.gethostname()
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.in_script_mode = False
        self.script_commands = []
        self.script_index = 0
        self.vfs = None

        if vfs_path:
            self.vfs = VFS(vfs_path)
            if not self.vfs.load():
                print("Продолжение работы без vfs!")
                self.vfs = None

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
                    path=self.currentpath.strip('/').split('/')
                    command_line = input(f"{self.user}@{self.hostname}:{"~/"+path[-1] if self.currentpath!="/" else "~"}$ ")
                except (KeyboardInterrupt):
                    print("\nВыход из эмулятора")
                    break

            if not command_line: continue

            command_line=self.parse_command_line(command_line)
            command= command_line[0]
            args=command_line[1:]

            if command =='help' and not args:
                print("Доступные команды: ls, cd, echo, cat, cal, chmod, mv, exit")
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

        path = self.currentpath+"/"+args[0] if args else self.currentpath
        
        if self.vfs:
            if not self.vfs.path_exists(path):
                print(f"Ошибка: путь не существует: {path}")
                return
                
            if not self.vfs.is_directory(path):
                print(f"Ошибка: не является директорией: {path}")
                return
                
            items = self.vfs.list_directory(path)

            if items is not None:
                for item in sorted(items):
                    print(item)
            else:
                print(f"Ошибка чтения директории: {path}")

        else:
            print("Hello there!")

    def cd(self, args):

        if not args:
            print("Ошибка: укажите путь")
            return
        
        path = self.currentpath+"/"+args[0] if self.currentpath!="/" and args[0]!="/" else args[0]
        
        if self.vfs:
            if not self.vfs.path_exists(path):
                print(f"Ошибка: путь не существует: {path}")
                return
                
            if not self.vfs.is_directory(path):
                print(f"Ошибка: не является директорией: {path}")
                return
                
            self.currentpath = path
            print(f"Перешел в директорию: {"root" if path=="/" else path}")

        else:
            self.currentpath = path
            print(f"Перешел в директорию: {path}")

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vfs', '-v')
    parser.add_argument('--script', '-s')
    return parser.parse_args()

if __name__ == "__main__":
    args=parse_arguments()
    print("Принимаемые аргументы:")
    print(f"VFS: {args.vfs if args.vfs!=None else "нет"}")
    print(f"Скрипт: {args.script if args.script!=None else "нет"}")
    shell = ComLineEm(vfs_path=args.vfs, script_path=args.script)
    shell.run()