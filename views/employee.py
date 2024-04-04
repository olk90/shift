from typing import Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt, QAbstractItemModel
from PySide6.QtGui import QPainter
from PySide6.QtSql import QSqlQueryModel
from PySide6.QtWidgets import QWidget, QHBoxLayout, QDialogButtonBox, QTableView, QMessageBox, QStyleOptionViewItem, \
    QStyleOptionButton, QLabel, QComboBox, QSpinBox, QLineEdit, QCheckBox

from logic.config import properties
from logic.crypt import decrypt_string
from logic.database import configure_query_model, persist_item, delete_item, update_employee, find_by_id, find_all_off
from logic.model import Employee, EmployeeType
from logic.queries import employee_type_designation_query
from logic.table_models import EmployeeModel
from views.base_classes import EditorDialog, EditorWidget, TableDialog, CenteredItemDelegate
from views.confirmationDialogs import ConfirmDeletionDialog


class AddEmployeeDialog(EditorDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent, ui_file_name="ui/employeeEditor.ui")

        self.get_widget(QLabel, "editorTitle").setText(self.tr("Add Employee"))

        self.firstname_edit: QLineEdit = self.get_widget(QLineEdit, "firstNameEdit")
        self.lastname_edit: QLineEdit = self.get_widget(QLineEdit, "lastNameEdit")

        self.firstname_edit.textChanged.connect(self.widget.validate)
        self.lastname_edit.textChanged.connect(self.widget.validate)

        self.widget.append_validation_fields(self.firstname_edit, self.lastname_edit)

        self.reference_spinner: QSpinBox = self.get_widget(QSpinBox, "referenceSpinner")
        self.score_spinner: QSpinBox = self.get_widget(QSpinBox, "scoreSpinner")
        self.type_combobox: QComboBox = self.get_widget(QComboBox, "typeCombobox")
        self.nightshift_edit: QCheckBox = self.get_widget(QCheckBox, "nightShiftsEdit")

        query: str = employee_type_designation_query()
        configure_query_model(self.type_combobox, query)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.button_box: QDialogButtonBox = self.get_widget(QDialogButtonBox, "buttonBox")

        self.configure_widgets()

    def commit(self):
        first_name: str = self.firstname_edit.text()
        last_name: str = self.lastname_edit.text()
        reference: int = self.reference_spinner.value()
        score: int = self.score_spinner.value()
        night_shifts: bool = self.nightshift_edit.isChecked()

        model: QSqlQueryModel = self.type_combobox.model()
        index: int = self.type_combobox.currentIndex()
        et_id = model.index(index, 1).data()
        employee = Employee(firstname=first_name, lastname=last_name, reference_value=reference,
                            night_shifts=night_shifts, e_type_id=et_id, score=score)
        persist_item(employee)
        self.parent.reload_table_contents(model=EmployeeModel())
        self.close()


class EmployeeEditorWidget(EditorWidget):

    def __init__(self, item_id=None):
        super().__init__(ui_file_name="ui/employeeEditor.ui", item_id=item_id)

        self.firstname_edit = self.widget.firstNameEdit
        self.lastname_edit = self.widget.lastNameEdit

        self.firstname_edit.textChanged.connect(self.validate)
        self.lastname_edit.textChanged.connect(self.validate)

        self.append_validation_fields(self.firstname_edit, self.lastname_edit)

        self.type_combobox = self.widget.typeCombobox
        self.reference_spinner = self.widget.referenceSpinner
        self.nightshift_edit = self.widget.nightShiftsEdit
        self.score_spinner = self.widget.scoreSpinner

        query: str = employee_type_designation_query()
        configure_query_model(self.type_combobox, query)

    def fill_fields(self, employee: Employee):
        self.item_id = employee.id

        firstname = employee.firstname
        lastname = employee.lastname

        key = properties.encryption_key
        if key is not None:
            firstname = decrypt_string(key, firstname)
            lastname = decrypt_string(key, lastname)

        self.firstname_edit.setText(firstname)
        self.lastname_edit.setText(lastname)
        self.reference_spinner.setValue(employee.reference_value)
        self.nightshift_edit.setChecked(employee.night_shifts)
        self.score_spinner.setValue(employee.score)

        query: str = employee_type_designation_query()
        configure_query_model(self.type_combobox, query)
        et_id: int = employee.e_type_id
        et: EmployeeType = find_by_id(et_id, EmployeeType)
        self.type_combobox.setCurrentText(et.designation)

    def get_values(self) -> dict:
        return {
            "item_id": self.item_id,
            "firstname": self.firstname_edit.text(),
            "lastname": self.lastname_edit.text(),
            "reference_value": self.reference_spinner.value(),
            "score": self.score_spinner.value(),
            "night_shifts": self.nightshift_edit.isChecked(),
            "e_type": self.type_combobox.currentText()
        }

    def clear_fields(self):
        query: str = employee_type_designation_query()
        self.type_combobox.model().setQuery(query)
        self.type_combobox.setCurrentIndex(0)

        self.firstname_edit.setText("")
        self.lastname_edit.setText("")
        self.reference_spinner.setValue(0)
        self.score_spinner.setValue(0)
        self.toggle_buttons(False, False)


class EmployeeWidget(TableDialog):

    def __init__(self):
        super(EmployeeWidget, self).__init__(table_ui_name="ui/employeeView.ui")
        self.add_dialog = AddEmployeeDialog(self)
        self.setup_table(EmployeeModel())

        self.tableview: QTableView = self.get_table()
        delegate: EmployeeItemDelegate = EmployeeItemDelegate(self)
        self.tableview.setItemDelegate(delegate)

    def setup_table(self, model: EmployeeModel):
        super().setup_table(model)

    def get_editor_widget(self) -> EditorWidget:
        return EmployeeEditorWidget()

    def configure_search(self):
        self.searchLine.textChanged.connect(lambda x: self.reload_table_contents(EmployeeModel(self.searchLine.text())))

    def get_selected_item(self):
        item_id = super().get_selected_item()
        employee = find_by_id(item_id, Employee)
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
            self.editor.clear_fields()

    def commit_changes(self):
        value_dict: dict = self.editor.get_values()
        update_employee(value_dict)
        search = self.searchLine.text()
        self.reload_table_contents(model=EmployeeModel(search))

    def revert_changes(self):
        employee: Employee = find_by_id(self.editor.item_id, Employee)
        self.editor.fill_fields(employee)


class EmployeeItemDelegate(CenteredItemDelegate):

    def __init__(self, parent: QWidget):
        super(EmployeeItemDelegate, self).__init__()
        self.editor = parent

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        model = index.model()
        data = model.data(index, Qt.EditRole)
        key = properties.encryption_key
        if key is not None:
            dec = decrypt_string(key, data)
            editor.setText(dec)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex):
        value = editor.text()
        key = properties.encryption_key
        if key is not None:
            dec = decrypt_string(key, value)
            model.setData(index, dec, Qt.EditRole)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: Union[QModelIndex, QPersistentModelIndex]):
        model = index.model()
        model_index = model.index(index.row(), index.column())
        data = model_index.data()

        if index.column() == 4:
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
