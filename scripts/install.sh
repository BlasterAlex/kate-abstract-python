#!/bin/bash

# Создание виртуального окружения
python3 -m pip install --user virtualenv
python3 -m venv env

# Активация виртуального окружения
source env/bin/activate

# Установка необходимых пакетов
pip install -r requirements.txt

# Замена пакета PyQt5 на ссылку из системы
PyQt5sys="/usr/lib/python3.8/site-packages/PyQt5"
PyQt5env="env/lib/python3.8/site-packages/PyQt5"
sudo rm -rf "$PyQt5env"
ln -s "$PyQt5sys" "$PyQt5env"