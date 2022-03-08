from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout

from views.helpers import load_ui_file


class EmployeeEditorWidget(QWidget):

    def __init__(self):
        super().__init__()
        ui_file_name = "ui/employeeEditor.ui"
        ui_file = load_ui_file(ui_file_name)

        loader = QUiLoader()
        self.widget = loader.load(ui_file)
        ui_file.close()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

        self.firstNameEdit = self.widget.firstNameEdit  # noqa
        self.lastNameEdit = self.widget.lastNameEdit  # noqa
        self.emailEdit = self.widget.emailEdit  # noqa

    def fill_text_fields(self, first_name: str, last_name: str, email: str):
        self.firstNameEdit.setText(first_name)
        self.lastNameEdit.setText(last_name)
        self.emailEdit.setText(email)
