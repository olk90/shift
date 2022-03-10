from PySide6.QtCore import QModelIndex, QItemSelectionModel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout, QHeaderView, QTableView, QAbstractItemView, QDialog

from logic.database import configure_employee_model, persist_employee
from logic.model import Employee
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

        editor_ui_name = "ui/employeeEditor.ui"
        editor_file = load_ui_file(editor_ui_name)
        self.editor = EmployeeEditorWidget()
        editor_file.close()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.table_widget, stretch=2)
        self.layout.addWidget(self.editor, stretch=1)

        self.setup_table()
        self.configure_buttons()

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

        header = tableview.horizontalHeader()
        for i in range(0, 3):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

    def reload_table_contents(self):
        model = configure_employee_model()
        tableview: QTableView = self.get_table()
        tableview.setModel(model)

    def reload_editor(self):
        tableview: QTableView = self.get_table()
        selection_model: QItemSelectionModel = tableview.selectionModel()
        indexes: QModelIndex = selection_model.selectedRows()
        model = tableview.model()
        for index in indexes:
            first_name = model.data(model.index(index.row(), 0))
            last_name = model.data(model.index(index.row(), 1))
            email = model.data(model.index(index.row(), 2))
            self.editor.fill_text_fields(first_name, last_name, email)

    def configure_buttons(self):
        self.table_widget.addButton.clicked.connect(self.add_employee)  # noqa -> button loaded from ui file

    def add_employee(self):
        self.add_employee_dialog.exec_()


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

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

        self.configure_buttons()

    def configure_buttons(self):
        self.widget.confirmUserEditButton.clicked.connect(self.commit)  # noqa
        self.widget.cancelUserEditButton.clicked.connect(self.close)  # noqa

    def commit(self):
        first_name: str = self.widget.firstNameEdit.text()  # noqa
        last_name: str = self.widget.lastNameEdit.text()  # noqa
        email: str = self.widget.emailEdit.text()  # noqa
        employee = Employee(firstname=first_name, lastname=last_name, email=email)
        persist_employee(employee)
        self.parent.reload_table_contents()
        self.close()
