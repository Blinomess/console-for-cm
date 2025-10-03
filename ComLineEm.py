import os
import socket
import re
import argparse
import json
import base64
import calendar
from datetime import datetime

class VFS:
    def __init__(self, vfs_path):
        self.vfs_path = vfs_path
        self.filesystem = {}
        self.file_permissions={}
        self.loaded = False
        
        
    def load(self):
        try:
            with open(self.vfs_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.filesystem = data
            self.loaded = True
        
            self.init_permissions()
            return True
           
        except FileNotFoundError as e:
            print(f"VFS файл не найден: {self.vfs_path}")
            return False
    
    def get_files(self, path):
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
    
    def list_dir(self, path="/"):
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
    
    def path_exists(self, path):
        if path == "/":
            return True
                
        current = self.filesystem
        parts = path.strip('/').split('/')
            
        for part in parts:
            if part not in current:
                return False
            current = current[part]
            
        return True

    
    def is_dir(self, path):
        if path == "/":
            return True
                
        current = self.filesystem
        parts = path.strip('/').split('/')
            
        for part in parts:
            if part not in current:
                return False
            current = current[part]
            
        return isinstance(current, dict)
        
    def move_file(self, src_path, dst_path):

        if not self.path_exists(src_path):
            print(src_path)
            return False, "Исходный путь не существует"
            
        if self.path_exists(dst_path):
            return False, "Целевой путь уже существует"

        src_parts = src_path.strip('/').split('/')
        src_name = src_parts[-1]
        src_parent = self.get_parent(src_path)
            
        if src_parent is None:
            return False, "Не удалось найти родительскую директорию"
            
        dst_parent_path = '/'.join(dst_path.strip('/').split('/')[:-1])

        if dst_parent_path == '':
            dst_parent_path = '/'
            
        if not self.path_exists(dst_parent_path) or not self.is_dir(dst_parent_path):
            return False, "Целевая директория не существует"
            
        dst_parent = self.get_parent(dst_path)

        if dst_parent is None:
            return False, "Не удалось найти целевую директорию"
            
        dst_name = dst_path.strip('/').split('/')[-1]
        if src_name.count('.')>0 and dst_name.count('.')>0:
            if dst_name[dst_name.rfind('.'):]==src_name[src_name.rfind('.'):]:
                dst_parent[dst_name] = src_parent[src_name]
                del src_parent[src_name]
            else: return False, "Неверный формат"

        elif src_name.count('.')==0 and dst_name.count('.')==0:
            dst_parent[dst_name] = src_parent[src_name]
            del src_parent[src_name]

        else: return False, "Неверный формат"
        
        if src_path in self.file_permissions:
            self.file_permissions[dst_path] = self.file_permissions[src_path]
            del self.file_permissions[src_path]
            
        return True, "Успешно"
    
    def get_parent(self, path):
        if path == "/":
            return None
                
        parts = path.strip('/').split('/')
        if len(parts) == 1:
            return self.filesystem
                
        current = self.filesystem
        for part in parts[:-1]:
            if part not in current:
                return None
            current = current[part]
            
        return current
        
    def init_permissions(self):
        def set_perms(path, obj):
            if isinstance(obj, dict):
                self.file_permissions[path] = '755'
                for name, content in obj.items():
                    new_path = f"{path}/{name}" if path != "/" else f"/{name}"
                    set_perms(new_path, content)
            else:
                self.file_permissions[path] = '644'
        
        set_perms("/", self.filesystem)
    
    def get_permissions(self, path):
        if path in self.file_permissions:
            return self.file_permissions[path]
        
        if self.is_dir(path):
            return '755'
        else:
            return '644'
    
    def set_permissions(self, path, mode):
        self.file_permissions[path] = mode
        return True
        
    def save(self):
        with open(self.vfs_path, 'w', encoding='utf-8') as f:
            json.dump(self.filesystem, f, indent=2, ensure_ascii=False)
        print(f"Изменения сохранены в: {self.vfs_path}")
        return


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
                print("Продолжение работы без vfs")
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

                if self.script_index == len(self.script_commands): 
                    self.in_script_mode=False

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
                if self.ls(args) and self.in_script_mode:
                    break

            elif command == 'cd':
                if self.cd(args) and self.in_script_mode:
                    break

            elif command =='echo':
                line=""
                for arg in args:
                    line+=arg+" "
                print(line)
            
            elif command == 'cat':
                if self.cat(args) and self.in_script_mode:
                    break
            
            elif command == 'cal':
                if self.cal(args) and self.in_script_mode:
                    break
            
            elif command == 'mv':
                if self.mv(args) and self.in_script_mode:
                    break

            elif command == 'chmod':
                if (self.chmod(args) and self.in_script_mode):
                    break
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
                self.script_commands = [line.strip() for line in f]
            return True
        except FileNotFoundError:
            print(f"Эррорка: неправильный файл {self.script_path}")
            return False
    
    def ls(self, args):

        if len(args)>1:
            if args[0]!="-l":
                print("Действие выплняется с одним аргументом или без аргументов")
                return 1

        if args:
            if args[0]!="-l":
                if self.currentpath!="/" and not args[0].startswith('~'):
                    path=self.currentpath+"/"+args[0]
                elif self.currentpath=="/" and args[0].find('/')==0:
                    path=args[0]
                elif args[0].startswith('~'):
                    path=(args[0])[1:]
                else: path="/"+args[0]
            else:
                if len(args)>1:
                    if self.currentpath!="/" and not args[1].startswith('~'):
                        path=self.currentpath+"/"+args[1]
                    elif self.currentpath=="/" and args[1].find('/')==0:
                        path=args[1]
                    elif args[1].startswith('~'):
                        path=(args[1])[1:]
                    else: path="/"+args[1]
                else: path=self.currentpath
        else: path=self.currentpath
        
        if self.vfs:
            if not self.vfs.path_exists(path):
                print(f"Эррорка: путь не существует: {path}")
                return 1
                
            if not self.vfs.is_dir(path):
                print(f"Эррорка: не является директорией: {path}")
                return 1
                
            items = self.vfs.list_dir(path)

            if items is not None:
                if args and args[0]=="-l":
                    for item in sorted(items):
                        item_path = f"{path}/{item}" if path != "/" else f"/{item}"
                        perms = self.vfs.get_permissions(item_path)
                        print(f"{perms} {item}")
                else:
                    for item in sorted(items):
                        print(item)
            else:
                print(f"Ошибка чтения директории: {path}")
                return 1

        else:
            print("Hello there!")
        return 0
    
    def mv(self, args):

        if len(args) != 2:
            print("Эррорка: использование: mv <источник> <назначение>")
            return 1
            
        src_path, dst_path = args
        
        if src_path.startswith('~'):
            src_path=src_path[1:]
        elif src_path.startswith('/'):
            src_path=self.currentpath+src_path[1:]
        else: 
            src_path=self.currentpath+"/"+src_path
        if dst_path.startswith('~'):
            dst_path=dst_path[1:]
        elif dst_path.startswith('/'):
            dst_path=self.currentpath+dst_path[1:]
        else: 
            dst_path=self.currentpath+dst_path

        if self.vfs:
            success, message = self.vfs.move_file(src_path, dst_path)
            if success:
                print(f"Успешно: {src_path} -> {dst_path}")
                if self.in_script_mode==0:
                    self.vfs.save()
            else:
                print(f"Эррорка: {message}")
                return 1
        else:
            print(f"Перемещение: {src_path} -> {dst_path}")
        return 0


    def cd(self, args):

        if not args:
            print("Эррорка: укажите путь")
            return 1
        elif len(args)!=1:
            print("Действие выплняется с одним аргументом")
            return 1
        if (args[0].find('~')==0):
            path = (args[0])[1:]
        else:
            path = self.currentpath+"/"+args[0] if self.currentpath!="/" and args[0]!="/" and args[0]!=".." else args[0]
        
        if self.vfs:
            if path==".":
                print(f"Перешел в директорию: {self.currentpath}")
                return 0
            if (not self.vfs.path_exists(path) and path!="..") or (path.count("//")>0) or (path==".." and self.currentpath=="/"):
                print(f"Эррорка: путь не существует: {path}")
                return 1
                
            if not self.vfs.is_dir(path) and path!="..":
                print(f"Эррорка: не является директорией: {path}")
                return 1
            
            self.currentpath = path if path!=".." else '/'+'/'.join(self.currentpath.strip('/').split('/')[:-1])
            if path=="/":
                print("Перешел в директорию: root")
            else: print (f"Перешел в директорию: {self.currentpath}")
            
        else:
            self.currentpath = path if path!=".." else '/'+'/'.join(self.currentpath.strip('/').split('/')[:-1])
            print(f"Перешел в директорию: {path}")
        return 0
    
    def chmod(self, args):
        if len(args) != 2:
            print("Эррорка: использование: chmod <режим> <файл>")
            return 1
            
        mode, file_path = args
        
        if not re.match(r'^[0-7]{3}$', mode):
            print("Эррорка: режим должен состоять из 3 цифр")
            return 1
        
        if not file_path.startswith('/'):
            file_path = f"{self.currentpath}/{file_path}" if self.currentpath != "/" else f"/{file_path}"
        
        if self.vfs:
            if not self.vfs.path_exists(file_path):
                print(f"Эррорка: путь не существует: {file_path}")
                return 1
            if self.vfs.set_permissions(file_path, mode):
                print(f"Права доступа {file_path} изменены на {mode}")
            else:
                print(f"Эррорка: не удалось изменить права доступа для {file_path}")
                return 1
        else:
            print(f"Права доступа {file_path} изменены на {mode} (эмуляция)")
        
        return 0

    
    def cat(self, args):
        if not args:
            print("Эррорка: укажите файл")
            return 1
            
        file_path = self.currentpath+'/'+args[0] if self.currentpath!="/" and args[0]!="/" else args[0]
        
        if self.vfs:

            if not self.vfs.path_exists(file_path):
                print(f"Эррорка: файл не существует: {file_path}")
                return 1
                
            if self.vfs.is_dir(file_path):
                print(f"Эррорка: является директорией: {file_path}")
                return 1
                
            content = self.vfs.get_files(file_path)
            if content is not None:
                print(f"Содержимое файла {file_path}:")
                print("-" * 50)
                print(content)
                print("-" * 50)
            else:
                print(f"Ошибка чтения файла: {file_path}")
                return 1

        else:
            print(f"Содержимое файла {file_path}:")
            print("-" * 40)
            print("Это содержимое файла из VFS")
            print("Здесь мог бы быть ваш текст...")
            print("-" * 40)
        return 0
    
    def cal(self, args):
        now = datetime.now()     
        try:
            if len(args) == 0:
                print(calendar.month(now.year, now.month))
                
            elif len(args) == 1:
                year = int(args[0])
                if 1 <= year <= 9999:
                    print(calendar.calendar(year))
                else:
                    print("Ошибка: год должен быть от 1 до 9999")
                    return 1
                    
            elif len(args) == 2:
                month = int(args[0])
                year = int(args[1])
                
                if 1 <= month <= 12 and 1 <= year <= 9999:
                    print(calendar.month(year, month))
                else:
                    print("Эррорка: месяц должен быть от 1 до 12, год от 1 до 9999")
                    return 1         
            else:
                print("Эррорка: слишком много аргументов")
                print("Использование: cal [год] или cal [месяц] [год]")
                return 1         
        except ValueError:
            print("Эррорка: аргументы должны быть числами")
            return 1
        return 0

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