from PySide6.QtCore import QModelIndex, QItemSelectionModel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout, QHeaderView, QTableView, QAbstractItemView, QLineEdit

from logic.database import delete_employee, \
    EmployeeModel, SearchTableModel, update_employee_type, OffPeriodModel, find_off_period_by_id, delete_off_period, \
    update_off_period
from logic.database import find_employee_by_id, update_employee, EmployeeTypeModel, find_employee_type_by_id, \
    delete_employee_type
from logic.model import Employee, EmployeeType, OffPeriod
from views.editorDialogs import AddEmployeeDialog, AddOffPeriodDialog
from views.editorDialogs import AddEmployeeTypeDialog
from views.editorWidgets import EmployeeEditorWidget, EditorWidget, EmployeeTypeEditorWidget, OffPeriodEditorWidget
from views.helpers import load_ui_file


class TableDialog(QWidget):

    def __init__(self, table_ui_name: str):
        super(TableDialog, self).__init__()
        loader = QUiLoader()

        table_file = load_ui_file(table_ui_name)
        self.table_widget = loader.load(table_file)
        table_file.close()
        self.searchLine: QLineEdit = self.table_widget.searchLine  # noqa

        self.editor: EditorWidget = self.get_editor_widget()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.table_widget, stretch=2)
        self.layout.addWidget(self.editor, stretch=1)

        self.configure_buttons()
        self.configure_search()

    def get_table(self):
        return self.table_widget.table  # noqa -> loaded from ui file

    def setup_table(self, model: SearchTableModel, header_range: range):
        tableview: QTableView = self.get_table()
        tableview.setModel(model)
        tableview.setSelectionBehavior(QTableView.SelectRows)
        tableview.setSelectionMode(QAbstractItemView.SingleSelection)
        tableview.selectionModel().selectionChanged.connect(self.reload_editor)

        # ID column is just used for loading the object from the DB tu the editor
        tableview.setColumnHidden(0, True)

        header = tableview.horizontalHeader()
        for i in header_range:
            header.setSectionResizeMode(i, QHeaderView.Stretch)

    def reload_table_contents(self, model: SearchTableModel):
        tableview: QTableView = self.get_table()
        tableview.setModel(model)
        tableview.selectionModel().selectionChanged.connect(self.reload_editor)

    def reload_editor(self):
        item = self.get_selected_item()
        self.editor.fill_fields(item)

    def configure_buttons(self):
        self.table_widget.addButton.clicked.connect(self.add_item)  # noqa -> button loaded from ui file
        self.table_widget.deleteButton.clicked.connect(self.delete_item)  # noqa -> button loaded from ui file
        self.editor.buttonBox.accepted.connect(self.commit_changes)
        self.editor.buttonBox.rejected.connect(self.revert_changes)

    def get_selected_item(self):
        tableview: QTableView = self.get_table()
        selection_model: QItemSelectionModel = tableview.selectionModel()
        indexes: QModelIndex = selection_model.selectedRows()
        model = tableview.model()
        index = indexes[0]
        return model.data(model.index(index.row(), 0))

    def configure_search(self):
        """Must be implemented by subclass"""

    def get_editor_widget(self) -> EditorWidget:
        """Must be implemented by subclass"""

    def add_item(self):
        """Must be implemented by subclass"""

    def delete_item(self):
        """Must be implemented by subclass"""

    def commit_changes(self):
        """Must be implemented by subclass"""

    def revert_changes(self):
        """Must be implemented by subclass"""


class EmployeeWidget(TableDialog):

    def __init__(self):
        super(EmployeeWidget, self).__init__(table_ui_name="ui/employeeView.ui")
        self.add_dialog = AddEmployeeDialog(self)
        self.setup_table(EmployeeModel(), range(1, 5))

    def get_table(self):
        return self.table_widget.table  # noqa -> loaded from ui file

    def get_editor_widget(self) -> EditorWidget:
        return EmployeeEditorWidget()

    def configure_search(self):
        self.searchLine.textChanged.connect(lambda x: self.reload_table_contents(EmployeeModel(self.searchLine.text())))

    def reload_editor(self):
        employee = self.get_selected_item()
        self.editor.fill_fields(employee)

    def get_selected_item(self):
        item_id = super().get_selected_item()
        employee = find_employee_by_id(item_id)
        return employee

    def add_item(self):
        self.add_dialog.clear_fields()
        self.add_dialog.exec_()

    def delete_item(self):
        employee = self.get_selected_item()
        delete_employee(employee)
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


class EmployeeTypeWidget(TableDialog):

    def __init__(self):
        super(EmployeeTypeWidget, self).__init__(table_ui_name="ui/employeeTypeView.ui")
        self.add_dialog = AddEmployeeTypeDialog(self)
        self.setup_table(EmployeeTypeModel(), range(1, 3))

    def get_table(self):
        return self.table_widget.table  # noqa -> loaded from ui file

    def get_editor_widget(self) -> EditorWidget:
        return EmployeeTypeEditorWidget()

    def configure_search(self):
        self.searchLine.textChanged.connect(
            lambda x: self.reload_table_contents(EmployeeTypeModel(self.searchLine.text())))

    def get_selected_item(self):
        item_id = super(EmployeeTypeWidget, self).get_selected_item()
        item = find_employee_type_by_id(item_id)
        return item

    def configure_buttons(self):
        self.table_widget.addButton.clicked.connect(self.add_item)  # noqa -> button loaded from ui file
        self.table_widget.deleteButton.clicked.connect(self.delete_item)  # noqa -> button loaded from ui file
        self.editor.buttonBox.accepted.connect(self.commit_changes)
        self.editor.buttonBox.rejected.connect(self.revert_changes)

    def add_item(self):
        self.add_dialog.clear_fields()
        self.add_dialog.exec_()

    def delete_item(self):
        item = self.get_selected_item()
        delete_employee_type(item)
        search = self.searchLine.text()
        self.reload_table_contents(model=EmployeeTypeModel(search))

    def commit_changes(self):
        value_dict: dict = self.editor.get_values()
        update_employee_type(value_dict)
        search = self.searchLine.text()
        self.reload_table_contents(model=EmployeeTypeModel(search))

    def revert_changes(self):
        e_type: EmployeeType = find_employee_type_by_id(self.editor.item_id)
        self.editor.fill_fields(e_type)


class OffPeriodWidget(TableDialog):

    def __init__(self):
        super(OffPeriodWidget, self).__init__(table_ui_name="ui/offPeriodView.ui")
        self.add_dialog = AddOffPeriodDialog(self)
        self.setup_table(OffPeriodModel(), range(1, 5))

    def get_table(self):
        return self.table_widget.table  # noqa -> loaded from ui file

    def get_editor_widget(self) -> EditorWidget:
        return OffPeriodEditorWidget()

    def configure_search(self):
        self.searchLine.textChanged.connect(
            lambda x: self.reload_table_contents(OffPeriodModel(self.searchLine.text())))

    def get_selected_item(self):
        item_id = super(OffPeriodWidget, self).get_selected_item()
        item = find_off_period_by_id(item_id)
        return item

    def configure_buttons(self):
        self.table_widget.addButton.clicked.connect(self.add_item)  # noqa -> button loaded from ui file
        self.table_widget.deleteButton.clicked.connect(self.delete_item)  # noqa -> button loaded from ui file
        self.editor.buttonBox.accepted.connect(self.commit_changes)
        self.editor.buttonBox.rejected.connect(self.revert_changes)

    def add_item(self):
        self.add_dialog.clear_fields()
        self.add_dialog.exec_()

    def delete_item(self):
        item = self.get_selected_item()
        delete_off_period(item)
        search = self.searchLine.text()
        self.reload_table_contents(model=OffPeriodModel(search))

    def commit_changes(self):
        value_dict: dict = self.editor.get_values()
        update_off_period(value_dict)
        search = self.searchLine.text()
        self.reload_table_contents(model=OffPeriodModel(search))

    def revert_changes(self):
        period: OffPeriod = find_off_period_by_id(self.editor.item_id)
        self.editor.fill_fields(period)
