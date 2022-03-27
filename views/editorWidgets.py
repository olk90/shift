from PySide6 import QtCore
from PySide6.QtCore import QDate
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout, QDialogButtonBox

from logic.database import find_e_type_by_e_id, find_employee_types, find_employee_by_id, configure_combobox_model
from logic.model import RotationPeriod, EmployeeType, Employee, OffPeriod, employeeTypeTableName
from views.helpers import load_ui_file


class EditorWidget(QWidget):

    def __init__(self, ui_file_name: str, item_id: int = None):
        super(EditorWidget, self).__init__()
        self.item_id = item_id
        ui_file = load_ui_file(ui_file_name)

        loader = QUiLoader()
        self.widget = loader.load(ui_file)
        ui_file.close()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa
        self.configure_buttons()

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

        self.firstNameEdit = self.widget.firstNameEdit  # noqa
        self.lastNameEdit = self.widget.lastNameEdit  # noqa
        self.typeCombobox = self.widget.typeCombobox  # noqa
        self.referenceSpinner = self.widget.referenceSpinner  # noqa
        self.nightShiftsEdit = self.widget.nightShiftsEdit  # noqa

        configure_combobox_model(self.typeCombobox, employeeTypeTableName, "designation")

    def fill_fields(self, employee: Employee):
        self.item_id = employee.id
        self.firstNameEdit.setText(employee.firstname)
        self.lastNameEdit.setText(employee.lastname)
        self.referenceSpinner.setValue(employee.referenceValue)
        self.nightShiftsEdit.setChecked(employee.night_shifts)

        self.typeCombobox.model().select()

    def get_values(self) -> dict:
        return {
            "item_id": self.item_id,
            "firstname": self.firstNameEdit.text(),
            "lastname": self.lastNameEdit.text(),
            "reference_value": self.referenceSpinner.value(),
            "night_shifts": self.nightShiftsEdit.isChecked(),
            "e_type": self.typeCombobox.currentText()
        }


class OffPeriodEditorWidget(EditorWidget):

    def __init__(self, item_id=None):
        super().__init__(ui_file_name="ui/offPeriodEditor.ui", item_id=item_id)

        self.name_label = self.widget.name_label  # noqa
        self.startEdit = self.widget.startEdit  # noqa
        self.endEdit = self.widget.endEdit  # noqa

    def fill_fields(self, period: OffPeriod):
        self.item_id = period.id
        employee: Employee = find_employee_by_id(period.e_id)
        self.name_label.setText(employee.get_full_name())

        start = period.start
        q_start = QDate(start.year, start.month, start.day)
        self.startEdit.setSelectedDate(q_start)

        end = period.end
        q_end = QDate(end.year, end.month, end.day)
        self.endEdit.setSelectedDate(q_end)

    def get_values(self) -> dict:
        return {
            "item_id": self.item_id,
            "start": self.startEdit.selectedDate(),
            "end": self.endEdit.selectedDate()
        }


class ScheduleEditorWidget(EditorWidget):

    def __init__(self, item_id=None):
        super().__init__(ui_file_name="ui/scheduleEditor.ui", item_id=item_id)
