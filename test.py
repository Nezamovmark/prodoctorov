import urllib.request
import os
import datetime

API_USERS = 'https://json.medrating.org/users?id='
API_TODOS = 'https://json.medrating.org/todos?userId='

class MyData:
    id_user = None
    name = None
    username = None
    email = None
    company = None
    completed_tasks = []
    unfinished_tasks = []
    
    
def tasks(report): # функция собирает все задачи пользователя 
   zapros_todos = urllib.request.urlopen(API_TODOS + report.id_user)
   todos = zapros_todos.readlines() 
   for line in todos:
       task = line.decode('utf-8')[0:-1]
       if task.find('title')>0:
           if len(task) > 66: #проверка длины строки
               titel = task[14:64]+'...'                           
           else:
               titel = task[14:-2]
       elif task.find('completed') > 0:
           statys = task[17:]
           if statys == 'true':
               report.completed_tasks.append(titel)
           else:
               report.unfinished_tasks.append(titel)


def write_to_disk(road, otchet):  
    file_name = os.path.join(road, otchet.username + '.txt')
    if os.path.exists(file_name):                                    
        temporary_name = os.path.join(road, otchet.username +"_old" + ".txt") 
        os.renames(file_name, temporary_name)
        if write_to_disk(road, otchet) == 0:                           
            old_name = os.path.join(road, otchet.username + "_old" + ".txt")
            t2 = os.stat(old_name).st_mtime
            new_name = os.path.join(road, otchet.username + "_" +
                                    datetime.datetime.fromtimestamp(t2).
                                    strftime('%Y-%m-%dT%H-%M-%S')
                                    + ".txt")
            os.renames(temporary_name, new_name)
            
    else:                                                           
        now = datetime.datetime.now()
        my_file = open(file_name, "w")
        print(road + '\\' + otchet.username + ".txt")
        size = my_file.write(otchet.name + " <" + otchet.email + "> " +
                             now.strftime("%d.%m.%Y %H:%M") + "\n" +
                             otchet.company + "\n\n" + 
                             "Завершённые задачи:\n")
        if size == 0: 
            my_file.close()
            write_error(road, otchet.username)
            return 1
        
        if otchet.completed_tasks:
            for item in otchet.completed_tasks:
                size = my_file.write("%s\n" % item)
                if size == 0: 
                    my_file.close()
                    write_error(road, otchet.username)
                    return 1
        else: my_file.write("Задач нет.\n")
        
        my_file.write("\nОставшиеся задачи:\n")
        if otchet.unfinished_tasks:
            for item in otchet.unfinished_tasks:
                size = my_file.write("%s\n" % item)
                if size == 0: 
                    my_file.close()
                    write_error(road, otchet.username)
                    return 1
        else: my_file.write("Задач нет.\n")
        my_file.close()
    return 0 
        

def write_error(dir, name):  #функция удаления неполного файла
    print('Сбой во время записи в файл.')
    old_name = os.path.join(dir, name+"_old"+".txt")
    new_name = os.path.join(dir, name+".txt")
    os.remove(new_name)
    os.renames(old_name, new_name)


dir = os.path.abspath(os.curdir)
fulldir = os.path.join(dir,'tasks')
if os.path.exists(fulldir):
    print('Папка существует')
else:
    print('Папка создана')
    os.mkdir(fulldir)
    
try:
    urllib.request.urlopen(API_USERS)
    urllib.request.urlopen(API_TODOS)
    report = MyData()                                               
    page = urllib.request.urlopen(API_USERS+'1')
    stroka = page.readlines() 
    while len(stroka) > 5:
        report.id_user = stroka[2].decode('utf-8')[10:-2]
        report.name = stroka[3].decode('utf-8')[13:-3]
        report.username = stroka[4].decode('utf-8')[17:-3]
        report.email = stroka[5].decode('utf-8')[14:-3]
        if not report.email:
            report.email = 'не указан'
        report.company = stroka[19].decode('utf-8')[15:-3]
        if not report.company:
            report.company = 'Место работы не известно.'
            
        tasks(report)                                              
        write_to_disk(fulldir, report) 
                             
        report.completed_tasks.clear()
        report.unfinished_tasks.clear()
        page = urllib.request.urlopen(API_USERS + str(int(report.id_user) + 1))
        stroka = page.readlines()
except IOError:
    print('Сбой в доступе к API')
