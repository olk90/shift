from typing import Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QPainter
from PySide6.QtSql import QSqlQueryModel
from PySide6.QtWidgets import QWidget, QHBoxLayout, QDialogButtonBox, QTableView, QMessageBox, QStyleOptionViewItem, \
    QStyleOptionButton

from logic.database import configure_query_model, persist_item, find_employee_type_by_id, \
    find_employee_by_id, delete_item, update_employee
from logic.table_models import EmployeeModel
from logic.model import Employee, EmployeeType
from logic.queries import employee_type_designation_query
from views.confirmationDialogs import ConfirmDeletionDialog
from views.base_classes import EditorDialog, EditorWidget, TableDialog, CenteredItemDelegate


class AddEmployeeDialog(EditorDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent, ui_file_name="ui/employeeEditor.ui")

        self.widget.editorTitle.setText(self.tr("Add Employee"))  # noqa
        self.type_box = self.widget.typeCombobox  # noqa
        query: str = employee_type_designation_query()
        configure_query_model(self.type_box, query)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa

        self.configure_widgets()

    def commit(self):
        first_name: str = self.widget.firstNameEdit.text()  # noqa
        last_name: str = self.widget.lastNameEdit.text()  # noqa
        reference: int = self.widget.referenceSpinner.value()  # noqa
        score: int = self.widget.scoreSpinner.value()  # noqa
        night_shifts: bool = self.widget.nightShiftsEdit.isChecked()  # noqa

        model: QSqlQueryModel = self.type_box.model()
        index: int = self.type_box.currentIndex()
        et_id = model.index(index, 1).data()
        employee = Employee(firstname=first_name, lastname=last_name, reference_value=reference,
                            night_shifts=night_shifts, e_type_id=et_id, score=score)
        persist_item(employee)
        self.parent.reload_table_contents(model=EmployeeModel())
        self.close()

    def clear_fields(self):
        query: str = employee_type_designation_query()
        self.type_box.model().setQuery(query)
        self.widget.firstNameEdit.setText("")  # noqa
        self.widget.lastNameEdit.setText("")  # noqa
        self.widget.referenceSpinner.setValue(0)  # noqa
        self.widget.scoreSpinner.setValue(0)  # noqa
        self.widget.typeCombobox.setCurrentIndex(0)  # noqa


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
        self.referenceSpinner.setValue(employee.reference_value)
        self.nightShiftsEdit.setChecked(employee.night_shifts)
        self.scoreSpinner.setValue(employee.score)

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
            "score": self.scoreSpinner.value(),
            "night_shifts": self.nightShiftsEdit.isChecked(),
            "e_type": self.typeCombobox.currentText()
        }


class EmployeeWidget(TableDialog):

    def __init__(self):
        super(EmployeeWidget, self).__init__(table_ui_name="ui/employeeView.ui")
        self.add_dialog = AddEmployeeDialog(self)
        self.setup_table(EmployeeModel(), range(1, 7))

        tableview: QTableView = self.get_table()
        delegate: EmployeeItemDelegate = EmployeeItemDelegate()
        tableview.setItemDelegate(delegate)

    def get_editor_widget(self) -> EditorWidget:
        return EmployeeEditorWidget()

    def configure_search(self):
        self.searchLine.textChanged.connect(lambda x: self.reload_table_contents(EmployeeModel(self.searchLine.text())))

    def get_selected_item(self):
        item_id = super().get_selected_item()
        employee = find_employee_by_id(item_id)
        return employee

    def add_item(self):
        self.add_dialog.clear_fields()
        self.add_dialog.exec_()

    def delete_item(self):
        dialog = ConfirmDeletionDialog(self)
        button = dialog.exec_()
        if button == QMessageBox.AcceptRole:
            employee: Employee = self.get_selected_item()
            delete_item(employee)
            search = self.searchLine.text()
            self.reload_table_contents(model=EmployeeModel(search))

    def commit_changes(self):
        value_dict: dict = self.editor.get_values()
        update_employee(value_dict)
        search = self.searchLine.text()
        self.reload_table_contents(model=EmployeeModel(search))

    def revert_changes(self):
        employee: Employee = find_employee_by_id(self.editor.item_id)
        self.editor.fill_fields(employee)


class EmployeeItemDelegate(CenteredItemDelegate):

    def __init__(self):
        super(EmployeeItemDelegate, self).__init__()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: Union[QModelIndex, QPersistentModelIndex]):
        if index.column() == 4:
            model = index.model()
            data = model.index(index.row(), index.column()).data()
            opt: QStyleOptionButton = QStyleOptionButton()
            opt.rect = option.rect
            if data:
                value = Qt.Checked
            else:
                value = Qt.Unchecked
            self.drawCheck(painter, option, option.rect, value)
            self.drawFocus(painter, option, option.rect)
        else:
            super(EmployeeItemDelegate, self).paint(painter, option, index)
