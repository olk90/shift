from PySide6.QtCore import QModelIndex, QItemSelectionModel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout, QHeaderView, QTableView, QAbstractItemView, QDialog, QLineEdit

from logic.database import configure_employee_model, persist_employee, find_employee_by_id, delete_employee, \
    update_employee
from logic.model import Employee, EmployeeType
from views.editorDialogs import EmployeeEditorWidget
from views.helpers import load_ui_file


class EmployeeWidget(QWidget):

    def __init__(self):
        super(EmployeeWidget, self).__init__()

        self.add_employee_dialog = AddEmployeeDialog(self)

        loader = QUiLoader()

        table_ui_name = "ui/employeeView.ui"
        table_file = load_ui_file(table_ui_name)
        self.table_widget = loader.load(table_file)
        table_file.close()
        self.searchLine: QLineEdit = self.table_widget.searchLine  # noqa

        editor_ui_name = "ui/employeeEditor.ui"
        editor_file = load_ui_file(editor_ui_name)
        self.editor = EmployeeEditorWidget()
        editor_file.close()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.table_widget, stretch=2)
        self.layout.addWidget(self.editor, stretch=1)

        self.setup_table()
        self.configure_buttons()
        self.configure_search()

    def get_table(self):
        return self.table_widget.table  # noqa -> loaded from ui file

    def setup_table(self):
        model = configure_employee_model()

        tableview: QTableView = self.get_table()
        tableview.setModel(model)
        tableview.setSelectionBehavior(QTableView.SelectRows)
        tableview.setSelectionMode(QAbstractItemView.SingleSelection)
        tableview.setSortingEnabled(True)
        tableview.selectionModel().selectionChanged.connect(lambda x: self.reload_editor())

        # ID column is just used for loading the object from the DB tu the editor
        tableview.setColumnHidden(0, True)

        header = tableview.horizontalHeader()
        for i in range(1, 5):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

    def reload_table_contents(self, search: str = ""):
        model = configure_employee_model(search)
        tableview: QTableView = self.get_table()
        tableview.setModel(model)
        tableview.selectionModel().selectionChanged.connect(lambda x: self.reload_editor())

    def reload_editor(self):
        employee = self.get_selected_employee()
        self.editor.fill_text_fields(employee)

    def get_selected_employee(self):
        tableview: QTableView = self.get_table()
        selection_model: QItemSelectionModel = tableview.selectionModel()
        indexes: QModelIndex = selection_model.selectedRows()
        model = tableview.model()
        index = indexes[0]
        employee_id = model.data(model.index(index.row(), 0))
        employee = find_employee_by_id(employee_id)
        return employee

    def configure_buttons(self):
        self.table_widget.addButton.clicked.connect(self.add_employee)  # noqa -> button loaded from ui file
        self.table_widget.deleteButton.clicked.connect(self.delete_employee)  # noqa -> button loaded from ui file
        self.editor.commitButton.clicked.connect(self.commit_changes)
        self.editor.revertButton.clicked.connect(self.revert_changes)

    def add_employee(self):
        self.add_employee_dialog.clear_fields()
        self.add_employee_dialog.exec_()

    def delete_employee(self):
        employee = self.get_selected_employee()
        delete_employee(employee)
        self.reload_table_contents()

    def configure_search(self):
        self.searchLine.textChanged.connect(lambda x: self.text_changed(self.searchLine.text()))

    def text_changed(self, text):
        self.reload_table_contents(text)

    def commit_changes(self):
        value_dict: dict = self.editor.get_values()
        update_employee(value_dict)
        self.reload_table_contents(self.searchLine.text())

    def revert_changes(self):
        employee: Employee = find_employee_by_id(self.editor.employee_id)
        self.editor.fill_text_fields(employee)


class AddEmployeeDialog(QDialog):

    def __init__(self, parent: EmployeeWidget):
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
        self.widget.commitButton.clicked.connect(self.commit)  # noqa
        self.widget.revertButton.clicked.connect(self.close)  # noqa

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
