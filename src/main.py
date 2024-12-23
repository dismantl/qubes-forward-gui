import sys
import PyQt6.QtWidgets as widgets
import ui_wrapper
from config import config


def main():
    app = widgets.QApplication(sys.argv)
    window = widgets.QMainWindow()
    qbox = widgets.QWidget()
    window.setCentralWidget(qbox)

    ui_wrapper.Index(qbox)

    window.setMinimumSize(600, 400)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()