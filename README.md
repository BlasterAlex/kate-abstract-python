# kate-abstract-python

Создание **pdf** документа на основе файлов изображений. Программа может использоваться студентами для хранения фотографий лекций или других записей в удобном для чтения формате.

# Установка 

Для работы приложения необходимо следующее программное обеспечение:

- [Python](https://www.python.org/downloads/) версии 3.8.2 и выше;
- Установленные в системе шрифты [DejaVu fonts](https://github.com/dejavu-fonts/dejavu-fonts);
- Программа для конвертирования в pdf [Pandoc](https://pandoc.org/installing.html);
- Поддержка стилизации создаваемых pdf документов:
  - [Miktex](https://miktex.org/download) для Windows;
  - [TeX Live](https://wiki.archlinux.org/index.php/TeX_Live) для Linux.

После установки требуемого ПО необходимо в папке проекта создать виртуальное окружение:

```bash
  # Создание виртуального окружения
  $ python3 -m pip install --user virtualenv
  $ python3 -m venv env

  # Активация виртуального окружения
  $ source env/bin/activate
```

В созданном виртуальном окружении нужно установить необходимые пакеты, описанные в [requirements.txt](requirements.txt):

```bash  
  # Установка необходимых пакетов
  (env) $ pip install -r requirements.txt
```

При возникновении конфликта пакета PyQt5 из виртуального окружения с пакетом, имеющимся в системе, необходимо удалить пакет из виртуального окружения и заменить его ссылкой:

```bash  
  # Замена пакета PyQt5 на ссылку из системы
  $ PyQt5sys="/usr/lib/python3.8/site-packages/PyQt5"
  $ PyQt5env="env/lib/python3.8/site-packages/PyQt5"
  $ sudo rm -rf "$PyQt5env"
  $ ln -s "$PyQt5sys" "$PyQt5env"
```

# Использование

После установки всего необходимого программа запускается из виртуального окружения:

```bash  
  # Установка необходимых пакетов
  (env) $ python3 kate-abstract-python
```