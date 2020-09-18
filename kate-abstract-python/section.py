from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QToolButton,
    QCheckBox,
)


# Виджет раздела конспекта - элемент списка чекбоксов с
# возможностью сортировки пользователем
class Section(QGroupBox):

    activate = pyqtSignal()
    moveUp = pyqtSignal()
    moveDown = pyqtSignal()

    def __init__(self, name, parent=None):
        super().__init__(parent)

        self.setStyleSheet(
            ""
            "QGroupBox { max-height: 40px; border: 1px solid #c9c9c9; border-radius: 5px;} "
            ""
            "QToolButton { border: none; }"
            ""
        )
        layout = QHBoxLayout(self)

        self.name = name
        self.b = QCheckBox(self.name)
        self.b.setChecked(True)
        self.b.stateChanged.connect(self.stateChanged)
        layout.addWidget(self.b)

        buttons = QVBoxLayout()
        buttons.setSpacing(0)
        layout.addLayout(buttons)

        self.up = QToolButton()
        self.up.setIcon(QIcon(QPixmap("data/icons/up-arrow.svg")))
        self.up.setIconSize(QSize(10, 10))
        self.up.clicked.connect(self.moveUp.emit)
        buttons.addWidget(self.up)

        self.down = QToolButton()
        self.down.setIcon(QIcon(QPixmap("data/icons/down-arrow.svg")))
        self.down.setIconSize(QSize(10, 10))
        self.down.clicked.connect(self.moveDown.emit)
        buttons.addWidget(self.down)

    def isSelected(self):
        return self.b.isChecked()

    def allEnable(self):
        self.up.setDisabled(False)
        self.down.setDisabled(False)

    @pyqtSlot(int)
    def stateChanged(self, state):
        if state == Qt.Checked:
            self.allEnable()
            self.activate.emit()
        else:
            self.up.setDisabled(True)
            self.down.setDisabled(True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name