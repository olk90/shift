from PySide6.QtCore import QModelIndex, QItemSelectionModel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout, QHeaderView, QTableView, QAbstractItemView

from logic.database import configure_employee_model
from views.editorDialogs import EmployeeEditorWidget
from views.helpers import load_ui_file


class EmployeeWidget(QWidget):

    def __init__(self):
        super(EmployeeWidget, self).__init__()

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
