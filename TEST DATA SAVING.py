import json
import time

i = 0
k = 10000000000000
event = 0
suma = 0
sum_1s = 0
event_flag = False
while True:
    print(i)
    k = k*1.005
    i += 1
    suma = suma+i #Сумма всего
    time.sleep(0.27) #Для наглядности
    current_time = time.time()
    formatted_time = time.ctime(current_time)
    #Переключатель ивента
    if i >= 30 and event_flag == False:
        event +=1
        event_flag = True
        #Тут ресет переменных за ивент
    #Создаю пустую ячейку в файле
    with open("test.json", 'r') as game_file:
        data = json.load(game_file)
    if str(event) not in data:
        data[event] = {}
        with open('test.json', 'w') as time_file:
            json.dump(data, time_file, indent=4)
    #Выход из ивента
    if i >= 50:
        event_flag = False
        i = 0
    #Работа в ивенте
    if event_flag == True:
        sum_1s = sum_1s + i
        #Снова подгружаем обновленный файл (1)
        with open("test.json", 'r') as game_file:
            data = json.load(game_file)
        #Вносим изменения по структуе  (2)
        if str(formatted_time) not in data[str(event)]:
            data[str(event)][str(formatted_time)] = {
                "sum": suma,
                "k": k,
                "i": i,
                "1s": sum_1s
            }
            #Ресет переменных за 1 секунду
            sum_1s = 0
            #Последнее сохранение
            with open('test.json', 'w') as time_file:
                json.dump(data, time_file, indent=4)

#Между (1) и (2) во время ассинхрона проблема, что одна функция внесла
#изменения но не пропушила в файл, а вторая взяла старый файл и пропушила
#изменения относительно старого файла