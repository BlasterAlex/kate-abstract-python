import re
import os
import codecs
import pypandoc
import configparser
from section import Section

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QSpacerItem,
    QPushButton,
    QRadioButton,
    QDialogButtonBox,
    QMessageBox,
    QCheckBox,
    QLabel,
)

from pylovepdf.ilovepdf import ILovePdf
from requests.exceptions import ConnectionError


# Чтение конфиг файла
config = configparser.ConfigParser()
config.read([os.path.join("config", "local.ini"), os.path.join("config", "config.ini")])
ProjectKey = config["DEFAULT"]["ProjectKey"]
mainSection = config["DEFAULT"]["mainSection"]
styleFile = config["DEFAULT"]["styleFile"]


# Диалог выбора разделов конспекта
class NoteDialog(QDialog):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.output = ""
        self.initUI()

        if len(self.subs) == 1:
            self.toc.setChecked(False)

    # Описание UI
    def initUI(self):

        self.dir = os.path.basename(self.path)
        self.setWindowTitle(self.dir)

        # Главный слой
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Заголовок
        label = QLabel("<b>Выберите необходимые разделы</b>:", self)
        label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        label.setMaximumHeight(30)
        label.setMargin(5)
        layout.addWidget(label)

        # Блок разделов
        self.sections = QVBoxLayout()
        layout.addLayout(self.sections)
        self.scanSub()

        # Нижний блок
        bottom = QVBoxLayout()
        bottom.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
        layout.addLayout(bottom)

        # Чекбокс содержания
        self.toc = QCheckBox("Создать содержание")
        self.toc.setChecked(True)
        bottom.addWidget(self.toc)

        # Чекбокс сжатия файла
        self.compress = QCheckBox("Сжать выходной файл")
        self.compress.setChecked(False)
        bottom.addWidget(self.compress)

        # Кнопки
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        bottom.addWidget(self.buttonBox)
        bottom.setAlignment(self.buttonBox, Qt.AlignCenter)

        self.hide()

    # Сканирование папки конспекта на наличие подпапок
    def scanSub(self):
        self.subs = []

        # Проход по папкам конспектов
        lst = os.listdir(self.path)

        if os.path.isdir(os.path.join(self.path, mainSection)):
            lst.remove(mainSection)

            lst.sort()

        if os.path.isdir(os.path.join(self.path, mainSection)):
            lst.insert(0, mainSection)

        for item in lst:
            if os.path.isdir(os.path.join(self.path, item)):
                r = Section(item, self)
                r.activate.connect(self.updateSubs)
                r.moveUp.connect(self.moveUp)
                r.moveDown.connect(self.moveDown)
                self.subs.append(r)

        # Вывод списка разделов
        self.updateSubs()

    # Перерисовка блока разделов после обновления
    @pyqtSlot()
    def updateSubs(self):

        # Очистка слоя разделов
        for i in reversed(range(self.sections.count())):
            self.sections.itemAt(i).widget().setParent(None)

        # Заполнение слоя разделов
        for sub in self.subs:
            if sub.isSelected():
                sub.allEnable()
            self.sections.addWidget(sub)

        # Деактивация стрелок для первого и последнего элементов
        self.subs[0].up.setDisabled(True)
        self.subs[len(self.subs) - 1].down.setDisabled(True)

    # Переместить раздел вверх в списке
    @pyqtSlot()
    def moveUp(self):
        sender = self.sender()
        index = self.subs.index(sender)

        get = self.subs[index], self.subs[index - 1]
        self.subs[index - 1], self.subs[index] = get

        self.updateSubs()

    # Переместить раздел вниз в списке
    @pyqtSlot()
    def moveDown(self):
        sender = self.sender()
        index = self.subs.index(sender)

        get = self.subs[index], self.subs[index + 1]
        self.subs[index + 1], self.subs[index] = get

        self.updateSubs()

    # Вызов создания файла
    def accept(self):

        # Создание нового файла
        fPath = os.path.join(self.path, self.dir + ".md")
        f = codecs.open(fPath, "w", "utf-8")

        # Рекурсивный спуск по папкам подразделов
        def passSub(dir):

            # Заголовок раздела
            name = os.path.basename(dir)

            # Уровень заголовка
            level = os.path.relpath(self.path, dir).count(os.path.sep) + 1

            # Вывод заголовка в md файл
            if not name == mainSection or level > 1:
                f.write(("#" * level) + " " + name + "\n\n")

            # Получение списка изображений
            lst = os.listdir(dir)
            lst.sort(key=lambda x: os.path.getmtime(os.path.join(dir, x)))

            # Список подпапок (сортируется отдельно)
            dirs = []

            # Запись списка в файл
            for item in lst:
                filePath = os.path.join(dir, item)
                if os.path.isfile(filePath):
                    f.write("![](" + filePath + ")\n\n")
                if os.path.isdir(filePath):
                    dirs.append(filePath)

            # Рекурсивный спуск по подпапкам
            dirs.sort()
            for d in dirs:
                passSub(d)

        # Проход по папкам разделов
        for sub in self.subs:
            if sub.isSelected():
                passSub(os.path.join(self.path, sub.name))

        # Завершения потока
        f.close()

        # Установка нумерации страниц генерируемого файла
        self.setPageNumbering(not self.toc.isChecked())

        # Определение передаваемых параметров
        extra_args = ["--pdf-engine=xelatex", "-H", "data/tex/style.tex"]
        if self.toc.isChecked():
            extra_args.append("--toc")
            extra_args.append("-V")
            extra_args.append("toc-title=Содержание")

        # Вызов конвертирования
        outputFile = os.path.join(self.path, self.dir + ".pdf")
        try:
            self.output = pypandoc.convert_file(
                fPath, "pdf", outputfile=outputFile, extra_args=extra_args
            )

        except RuntimeError as err:
            self.output = repr(err)

        # Успешная конвертация без ошибок
        if self.output == "":

            # Компрессия выходного файла
            if self.compress.isChecked():
                try:

                    print(os.path.basename(outputFile))
                    ilovepdf = ILovePdf(ProjectKey, verify_ssl=True)
                    task = ilovepdf.new_task("compress")
                    task.add_file(outputFile)
                    task.debug = False
                    task.compression_level = "low"
                    task.set_output_folder(self.path)

                    task.execute()
                    task.download()
                    task.delete_current_task()

                except AttributeError as attrErr:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("<b>Ошибка сжатия файла:</b><br>" + repr(attrErr))
                    msg.setWindowTitle("Ошибка сжатия файла")
                    msg.exec()

                except ConnectionError as connectErr:
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText(
                        "<b>Ошибка сжатия файла:</b><br>"
                        + "Проверьте интернет соединение"
                    )
                    msg.setWindowTitle("Ошибка сжатия файла")
                    msg.exec()

            # Возврат результата
            return super().accept()

        return super().reject()

    # Включение / отключение нумерации страниц генерируемого файла
    def setPageNumbering(self, enable):

        f = open(styleFile, "r", encoding="UTF8", errors="ignore")
        content = f.read()
        f.close()

        if enable:
            content_new = re.sub(
                "%[ ]?(\\\pagenumbering{gobble})", r"\1", content, flags=re.M
            )
        else:
            content_new = re.sub(
                "^[ ]?(\\\pagenumbering{gobble})", r"% \1", content, flags=re.M
            )
        if content != content_new:
            f = open(styleFile, "w")
            f.write(content_new)
            f.close()