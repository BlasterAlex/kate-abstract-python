import sys
from mainwindow import MainWindow
from PyQt5.QtWidgets import QApplication

# Запуск основного цикла программы
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())