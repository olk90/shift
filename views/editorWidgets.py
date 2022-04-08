from sqlalchemy import create_engine as ce
from sqlalchemy.orm import sessionmaker as sm

from PySide6.QtCore import QDate
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout, QDialogButtonBox, QTextEdit, QComboBox

from logic.database import find_employee_by_id, configure_query_model, find_employee_type_by_id
from logic.model import RotationPeriod, EmployeeType, Employee, OffPeriod, Schedule
from logic.queries import employee_type_designation_query, day_shift_replacement_query, night_shift_replacement_query, \
    employee_id_by_fullname_query
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
        self.scoreSpinner = self.widget.scoreSpinner  # noqa

        query: str = employee_type_designation_query()
        configure_query_model(self.typeCombobox, query)

    def fill_fields(self, employee: Employee):
        self.item_id = employee.id
        self.firstNameEdit.setText(employee.firstname)
        self.lastNameEdit.setText(employee.lastname)
        self.referenceSpinner.setValue(employee.referenceValue)
        self.nightShiftsEdit.setChecked(employee.night_shifts)
        self.scoreSpinner.setValue(employee.global_score)

        query: str = employee_type_designation_query()
        configure_query_model(self.typeCombobox, query)
        et_id: int = employee.e_type_id
        et: EmployeeType = find_employee_type_by_id(et_id)
        self.typeCombobox.setCurrentText(et.designation)

    def get_values(self) -> dict:
        return {
            "item_id": self.item_id,
            "firstname": self.firstNameEdit.text(),
            "lastname": self.lastNameEdit.text(),
            "reference_value": self.referenceSpinner.value(),
            "global_score": self.scoreSpinner.value(),
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

        self.d_id: int = 0
        self.n_id: int = 0

        self.date_display: QLabel = self.widget.dateDisplay  # noqa

        self.day_box: QComboBox = self.widget.dayBox  # noqa
        self.day_box.currentTextChanged.connect(lambda x: self.update_selection_id(self.day_box))
        day_query: str = day_shift_replacement_query()
        configure_query_model(self.day_box, day_query)

        self.night_box: QComboBox = self.widget.nightBox  # noqa
        self.night_box.currentTextChanged.connect(lambda x: self.update_selection_id(self.night_box))
        night_query: str = night_shift_replacement_query()
        configure_query_model(self.night_box, night_query)

        self.comment_edit: QTextEdit = self.widget.commentEdit  # noqa

    def update_selection_id(self, box: QComboBox):
        db = ce("sqlite:///shift.db")
        session = sm(bind=db)
        s = session()
        fullname: str = box.currentText()
        query = employee_id_by_fullname_query(fullname)
        result = s.execute(query)
        for e_id in result:
            if box == self.day_box:
                self.d_id = e_id[0]
            elif box == self.night_box:
                self.n_id = e_id[0]

    def fill_fields(self, schedule: Schedule):
        self.item_id = schedule.id
        self.date_display.setText(str(schedule.date))

        self.d_id: int = schedule.day_id
        day_shift: Employee = find_employee_by_id(self.d_id)
        self.day_box.setCurrentText(day_shift.get_full_name())

        self.n_id: int = schedule.night_id
        night_shift: Employee = find_employee_by_id(self.n_id)
        self.night_box.setCurrentText(night_shift.get_full_name())

        self.comment_edit.setText(schedule.comment)

    def get_values(self) -> dict:
        text: str = self.comment_edit.toPlainText()
        return {
            "item_id": self.item_id,
            "date": self.date_display.text(),
            "d_id": self.d_id,
            "n_id": self.n_id,
            "comment": text
        }
