from PyQt6 import QtCore, QtWidgets, QtGui


class MyWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(250, 150)
        self.setMaximumSize(250, 150)

# +++ vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        scrollArea = QtWidgets.QScrollArea()
        content_widget = QtWidgets.QWidget()
        scrollArea.setWidget(content_widget)
        scrollArea.setWidgetResizable(True)
        self.box1 = QtWidgets.QGridLayout(content_widget)
# +++ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        self.button = QtWidgets.QPushButton('Button')

        for n in range(1, 17):
            btn = QtWidgets.QPushButton(
                f'Button{n}',
                clicked=lambda ch, n=n: print(f'Button{n}')
            )
            self.box1.addWidget(btn, n-1, 0)

        self.box = QtWidgets.QHBoxLayout()
#        self.box.addLayout(self.box1)                           # ---
        self.box.addWidget(scrollArea)                           # +++

        self.box.addWidget(self.button)
        self.setLayout(self.box)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle(' ')
    window.show()
    sys.exit(app.exec())
