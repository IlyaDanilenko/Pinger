# Pinger
Утилита для пинга устройств. Приложение написано с помощью фреймворка PyQt5

## Установка
1. Клонируем репозиторий
```
git clone https://github.com/IlyaDanilenko/Pinger.git
```
2. Устанавливаем необходимые библиотеки Python
```
cd Pinger
pip3 install -r requirements.txt
```

## Настройка
Задать список пингуемых устройств можно в `config/config.json`. Некоторые настройки заданы константами в файле `pinger.py`.

## Запуск программы
```
python3 pinger.py
```

## Управление
* `ESCAPE` - выход из приложения
* `F` - полноэкранный/оконный режим
* `Z` - обнуление среднего значения пинга
* `1` - окно просмотра запросов

## Комментарии
* Для корректного отображение имени оно не должна привышать 15 символов
* Устройство считается недоступным если пинг составляет `TIMEOUT` мс
* По оси X отмечено время в секундах. Однако отсчет начинается с `SCALE` секунд
