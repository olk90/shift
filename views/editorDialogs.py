import qdarktheme
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout, QDialog, QMainWindow, QApplication

from logic.config import properties
from logic.database import persist_employee
from logic.model import EmployeeType, Employee
from views.helpers import load_ui_file


class OptionsEditorDialog(QDialog):

    def __init__(self, parent: QMainWindow):
        super().__init__()
        self.parent = parent
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setWindowTitle(" ")
        ui_file_name = "ui/optionsEditor.ui"
        ui_file = load_ui_file(ui_file_name)

        loader = QUiLoader()
        self.widget = loader.load(ui_file)
        ui_file.close()

        self.themeBox: QComboBox = self.widget.themeBox  # noqa
        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa

        self.configure_widgets()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

    def configure_widgets(self):
        self.themeBox.addItems(properties.themes)
        self.themeBox.setCurrentIndex(properties.theme_index)

        self.buttonBox.accepted.connect(self.apply_changes)
        self.buttonBox.rejected.connect(self.cancel)

    def apply_changes(self):
        selected_index = self.themeBox.currentIndex()
        properties.theme_index = selected_index

        app = QApplication.instance()
        if selected_index == 0:
            app.setStyleSheet(qdarktheme.load_stylesheet())
        elif selected_index == 1:
            app.setStyleSheet(qdarktheme.load_stylesheet("light"))
        else:
            app.setStyleSheet(None)

        properties.write_config_file()
        self.close()

    def cancel(self):
        self.close()


class AddEmployeeDialog(QDialog):

    def __init__(self, parent: QWidget):
        super().__init__()
        self.parent = parent
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setWindowTitle(" ")
        ui_file_name = "ui/employeeEditor.ui"
        ui_file = load_ui_file(ui_file_name)

        loader = QUiLoader()
        self.widget = loader.load(ui_file)
        ui_file.close()

        self.widget.editorTitle.setText("Add Employee")  # noqa
        self.widget.typeCombobox.addItems(EmployeeType.types)  # noqa

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.configure_buttons()

    def configure_buttons(self):
        self.widget.buttonBox.accepted.connect(self.commit)  # noqa
        self.widget.buttonBox.rejected.connect(self.close)  # noqa

    def commit(self):
        first_name: str = self.widget.firstNameEdit.text()  # noqa
        last_name: str = self.widget.lastNameEdit.text()  # noqa
        reference: str = self.widget.referenceSpinner.text()  # noqa
        e_type: str = self.widget.typeCombobox.currentText()  # noqa
        employee = Employee(firstname=first_name, lastname=last_name, referenceValue=reference, e_type=e_type)
        persist_employee(employee)
        self.parent.reload_table_contents()
        self.close()

    def clear_fields(self):
        self.widget.firstNameEdit.setText("")  # noqa
        self.widget.lastNameEdit.setText("")  # noqa
        self.widget.referenceSpinner.setValue(0)  # noqa
        self.widget.typeCombobox.setCurrentIndex(0)  # noqa


class EmployeeEditorWidget(QWidget):

    def __init__(self, employee_id=None):
        super().__init__()

        self.employee_id = employee_id

        ui_file_name = "ui/employeeEditor.ui"
        ui_file = load_ui_file(ui_file_name)

        loader = QUiLoader()
        self.widget = loader.load(ui_file)
        ui_file.close()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

        self.firstNameEdit = self.widget.firstNameEdit  # noqa
        self.lastNameEdit = self.widget.lastNameEdit  # noqa
        self.typeCombobox = self.widget.typeCombobox  # noqa
        self.referenceSpinner = self.widget.referenceSpinner  # noqa

        self.typeCombobox.addItems(EmployeeType.types)

        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa

    def fill_text_fields(self, employee: Employee):
        self.employee_id = employee.id
        self.firstNameEdit.setText(employee.firstname)
        self.lastNameEdit.setText(employee.lastname)
        self.referenceSpinner.setValue(employee.referenceValue)  # noqa
        self.typeCombobox.setCurrentIndex(EmployeeType.types.index(employee.e_type))  # noqa

    def get_values(self) -> dict:
        return {
            "e_id": self.employee_id,
            "firstname": self.firstNameEdit.text(),
            "lastname": self.lastNameEdit.text(),
            "reference_value": self.referenceSpinner.value(),
            "e_type": self.typeCombobox.currentText()
        }
