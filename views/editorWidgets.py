from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout, QDialogButtonBox

from logic.database import find_employee_types
from logic.model import RotationPeriod, EmployeeType, Employee
from views.helpers import load_ui_file


class EmployeeTypeEditorWidget(QWidget):

    def __init__(self, employee_type_id=None):
        super().__init__()

        self.employee_type_id = employee_type_id

        ui_file_name = "ui/employeeTypeEditor.ui"
        ui_file = load_ui_file(ui_file_name)

        loader = QUiLoader()
        self.widget = loader.load(ui_file)
        ui_file.close()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

        self.designationEdit = self.widget.designationEdit  # noqa
        self.rotationBox = self.widget.rotationBox  # noqa

        self.rotationBox.addItems(RotationPeriod.periods)

        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa
        self.buttonBox.button(QDialogButtonBox.Ok).setText(self.tr("OK"))
        self.buttonBox.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))

    def fill_text_fields(self, employee_type: EmployeeType):
        self.employee_type_id = employee_type.id
        self.designationEdit.setText(employee_type.designation)
        self.rotationBox.setCurrentIndex(RotationPeriod.periods.index(employee_type.rotation_period))  # noqa

    def get_values(self) -> dict:
        return {
            "e_type_id": self.employee_type_id,
            "rotation_period": self.rotationBox.currentText()
        }


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

        self.typeCombobox.addItems(find_employee_types())

        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa
        self.buttonBox.button(QDialogButtonBox.Ok).setText(self.tr("OK"))
        self.buttonBox.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))

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
