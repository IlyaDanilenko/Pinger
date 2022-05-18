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
sudo pip3 install -r requirements.txt
```

## Настройка
Задать список пингуемых устройств можно в `config/config.json`. Некоторые настройки заданы константами в файле `pinger.py`.

## Запуск программы
```
sudo python3 pinger.py
```