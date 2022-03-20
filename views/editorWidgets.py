from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout, QDialogButtonBox

from logic.database import find_e_type_by_e_id, find_employee_types
from logic.model import RotationPeriod, EmployeeType, Employee
from views.helpers import load_ui_file


class EditorWidget(QWidget):

    def __init__(self, ui_file_name: str, item_id: int = None):
        super(EditorWidget, self).__init__()
        self.item_id = item_id
        ui_file = load_ui_file(ui_file_name)

        loader = QUiLoader()
        self.widget = loader.load(ui_file)
        ui_file.close()

        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa

    def configure_buttons(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setText(self.tr("OK"))
        self.buttonBox.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))

    def get_values(self) -> dict:
        """Must be implemented by subclass"""

    def fill_fields(self, item):
        """Must be implemented by subclass"""


class EmployeeTypeEditorWidget(EditorWidget):

    def __init__(self, item_id=None):
        super().__init__(ui_file_name="ui/employeeTypeEditor.ui", item_id=item_id)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

        self.designationEdit = self.widget.designationEdit  # noqa
        self.rotationBox = self.widget.rotationBox  # noqa

        self.rotationBox.addItems(RotationPeriod.periods)

    def fill_fields(self, employee_type: EmployeeType):
        self.item_id = employee_type.id
        self.designationEdit.setText(employee_type.designation)
        self.rotationBox.setCurrentIndex(RotationPeriod.periods.index(employee_type.rotation_period))  # noqa

    def get_values(self) -> dict:
        return {
            "item_id": self.item_id,
            "designation": self.designationEdit.text(),
            "rotation_period": self.rotationBox.currentText()
        }


class EmployeeEditorWidget(EditorWidget):

    def __init__(self, item_id=None):
        super().__init__(ui_file_name="ui/employeeEditor.ui", item_id=item_id)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

        self.firstNameEdit = self.widget.firstNameEdit  # noqa
        self.lastNameEdit = self.widget.lastNameEdit  # noqa
        self.typeCombobox = self.widget.typeCombobox  # noqa
        self.referenceSpinner = self.widget.referenceSpinner  # noqa

        e_types = find_employee_types()
        for e_type in e_types:
            self.typeCombobox.addItem(e_type.designation, userData=None)  # noqa

        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa
        self.buttonBox.button(QDialogButtonBox.Ok).setText(self.tr("OK"))
        self.buttonBox.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))

    def fill_fields(self, employee: Employee):
        self.item_id = employee.id
        self.firstNameEdit.setText(employee.firstname)
        self.lastNameEdit.setText(employee.lastname)
        self.referenceSpinner.setValue(employee.referenceValue)  # noqa

        e_type = find_e_type_by_e_id(self.item_id)
        # index = self.typeCombobox.findText(e_type.designation, QtCore.Qt.MatchFixedString)
        AllItems = [self.typeCombobox.itemText(i) for i in range(self.typeCombobox.count())]
        index = self.typeCombobox.findText(e_type.designation, QtCore.Qt.MatchExactly)
        if index >= 0:
            self.typeCombobox.setCurrentIndex(index)  # noqa

    def get_values(self) -> dict:
        return {
            "item_id": self.item_id,
            "firstname": self.firstNameEdit.text(),
            "lastname": self.lastNameEdit.text(),
            "reference_value": self.referenceSpinner.value(),
            "e_type": self.typeCombobox.currentText()
        }
