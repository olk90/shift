from PySide6.QtCore import QModelIndex, QItemSelectionModel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout, QHeaderView, QTableView, QAbstractItemView, QLineEdit

from logic.database import find_employee_by_id, update_employee, EmployeeTypeModel, find_employee_type_by_id, \
    delete_employee_type
from logic.model import Employee
from views.editorDialogs import AddEmployeeTypeDialog
from views.editorWidgets import EmployeeTypeEditorWidget
from views.helpers import load_ui_file


class EmployeeTypeWidget(QWidget):

    def __init__(self):
        super(EmployeeTypeWidget, self).__init__()

        self.add_employee_dialog = AddEmployeeTypeDialog(self)

        loader = QUiLoader()

        table_ui_name = "ui/employeeTypeView.ui"
        table_file = load_ui_file(table_ui_name)
        self.table_widget = loader.load(table_file)
        table_file.close()
        self.searchLine: QLineEdit = self.table_widget.searchLine  # noqa

        editor_ui_name = "ui/employeeTypeEditor.ui"
        editor_file = load_ui_file(editor_ui_name)
        self.editor = EmployeeTypeEditorWidget()
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
        model = EmployeeTypeModel()

        tableview: QTableView = self.get_table()
        tableview.setModel(model)
        tableview.setSelectionBehavior(QTableView.SelectRows)
        tableview.setSelectionMode(QAbstractItemView.SingleSelection)
        tableview.selectionModel().selectionChanged.connect(lambda x: self.reload_editor())

        # ID column is just used for loading the object from the DB tu the editor
        tableview.setColumnHidden(0, True)

        header = tableview.horizontalHeader()
        for i in range(1, 3):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

    def reload_table_contents(self, search: str = ""):
        model = EmployeeTypeModel(search)
        tableview: QTableView = self.get_table()
        tableview.setModel(model)
        tableview.selectionModel().selectionChanged.connect(lambda x: self.reload_editor())

    def reload_editor(self):
        item = self.get_selected_item()
        self.editor.fill_text_fields(item)

    def get_selected_item(self):
        tableview: QTableView = self.get_table()
        selection_model: QItemSelectionModel = tableview.selectionModel()
        indexes: QModelIndex = selection_model.selectedRows()
        model = tableview.model()
        index = indexes[0]
        item_id = model.data(model.index(index.row(), 0))
        item = find_employee_type_by_id(item_id)
        return item

    def configure_buttons(self):
        self.table_widget.addButton.clicked.connect(self.add_employee)  # noqa -> button loaded from ui file
        self.table_widget.deleteButton.clicked.connect(self.delete_employee_type)  # noqa -> button loaded from ui file
        self.editor.buttonBox.accepted.connect(self.commit_changes)
        self.editor.buttonBox.rejected.connect(self.revert_changes)

    def add_employee(self):
        self.add_employee_dialog.clear_fields()
        self.add_employee_dialog.exec_()

    def delete_employee_type(self):
        item = self.get_selected_item()
        delete_employee_type(item)
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
