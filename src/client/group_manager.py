from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class GroupManager(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Group List"))
        self.create_group_button = QPushButton("Create Group")
        layout.addWidget(self.create_group_button)

        self.setLayout(layout)

        self.create_group_button.clicked.connect(self.create_group)

    def create_group(self):
        # Здесь добавьте логику для создания группы
        print("Creating a new group")
