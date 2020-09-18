import re
import os
import configparser
from notedialog import NoteDialog

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSpacerItem,
    QPushButton,
    QRadioButton,
    QMessageBox,
    QLabel,
)

# Чтение конфиг файла
config = configparser.ConfigParser()
config.read(os.path.join("config", "config.ini"))
mainSection = config["DEFAULT"]["mainSection"]
notesFolder = config["DEFAULT"]["notesFolder"]

# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.scanNotes()

    # Описание UI
    def initUI(self):

        # Главный виджет
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        # Главный слой
        vbl = QVBoxLayout(self.main_widget)

        # Заголовок
        label = QLabel("<b>Выберите папку конспекта:</b>", self.main_widget)
        label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        label.setMaximumHeight(30)
        label.setMargin(5)
        vbl.addWidget(label)

        # Внутренние слои
        self.radioL = QVBoxLayout()
        self.radioL.setAlignment(Qt.AlignCenter)
        self.buttonL = QHBoxLayout()
        vbl.addLayout(self.radioL)
        vbl.addItem(
            QSpacerItem(
                50, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
            )
        )
        vbl.addLayout(self.buttonL)

        # Кнопки
        createBtn = QPushButton("Создать", self.main_widget)
        createBtn.clicked.connect(self.create)
        self.buttonL.addWidget(createBtn)

        refreshBtn = QPushButton("Обновить", self.main_widget)
        refreshBtn.clicked.connect(self.scanNotes)
        self.buttonL.addWidget(refreshBtn)

        # Свойства окна
        self.setGeometry(300, 300, 350, 200)
        self.setWindowTitle("Abstract")

    # Сканирование папки notes и формирование списка папок конспектов
    def scanNotes(self):
        self.root = notesFolder
        self.notes = []

        # Очистка слоя
        for i in reversed(range(self.radioL.count())):
            self.radioL.itemAt(i).widget().deleteLater()

        # Проход по папкам конспектов
        lst = os.listdir(self.root)
        lst.sort()
        for item in lst:
            if os.path.isdir(os.path.join(self.root, item)):
                r = QRadioButton(item, self.main_widget)
                self.radioL.addWidget(r)
                self.notes.append(r)

        # Папка notes не содержит подпапок
        if len(self.notes) == 0:
            label = QLabel("Ни одной папки с конспектом", self.main_widget)
            label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            label.setMaximumHeight(20)
            self.radioL.addWidget(label)
        else:
            self.notes[0].setChecked(True)

    # Вызов диалогового окна конспекта
    def create(self):
        indexes = [x.isChecked() for x in self.notes]

        if len(indexes) == 0:
            self.message("Выберите папку конспекта")
            return

        checked = self.notes[indexes.index(True)]
        dir = checked.text()

        dlg = NoteDialog(os.path.join(self.root, dir), self)
        self.setEnabled(False)
        dlg.setEnabled(True)

        if not dlg.exec_():
            if dlg.output:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Critical)
                msg.setText(
                    "Ошибка при конвертации файла <b>" + dir + "/" + dir + ".md</b>"
                )
                msg.setInformativeText(
                    "Нажмите <i>Show Details</i> для получения дополнительной информации"
                )
                msg.setWindowTitle("Ошибка конвертирования")
                msg.setDetailedText(dlg.output)
                msg.exec()
        else:

            # Проверка на наличие сконвертированного файла
            outputDir = os.path.join(self.root, dir)
            compress = [
                f for f in os.listdir(outputDir) if re.match(r"compress_.*.pdf", f)
            ]

            if len(compress) > 0:

                # Вычисление степени сжатия
                oldFile = os.path.join(outputDir, dir + ".pdf")
                newFile = os.path.join(outputDir, compress[0])
                perc = round(
                    (1 - os.path.getsize(newFile) / os.path.getsize(oldFile)) * 100
                )

                # Замена старого файла на новый сжатый файл
                if os.path.exists(oldFile):
                    os.remove(oldFile)
                os.rename(newFile, oldFile)

                self.message(
                    "Конспект " + dir + " успешно создан и сжат на " + str(perc) + "%"
                )

            else:
                self.message("Успешное создание конспекта: " + dir)

        self.setEnabled(True)

    # Проверка папки конспекта
    def checkDir(self, dir):
        return os.path.isdir(os.path.join(self.root, dir, mainSection))

    # Вывод сообщения с автоматической очисткой
    def message(self, text):
        self.statusBar().showMessage(text)
        self.statusBar().show()
        QTimer.singleShot(5000, self.clearStatusBar)

    # Очистка статусбара
    def clearStatusBar(self):
        self.statusBar().clearMessage()
        self.statusBar().hide()