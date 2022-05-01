from PySide6.QtCore import QModelIndex, QItemSelectionModel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout, QHeaderView, QTableView, QAbstractItemView, QLineEdit, \
    QPushButton, QSpinBox, QMessageBox, QApplication, QFileDialog

from logic.config import properties
from logic.database import EmployeeModel, SearchTableModel, update_employee_type, OffPeriodModel, \
    find_off_period_by_id, update_off_period, ScheduleModel, find_schedule_by_id, delete_item, shift_plan_active, \
    update_schedule, schedule_exists
from logic.database import find_employee_by_id, update_employee, EmployeeTypeModel, find_employee_type_by_id
from logic.model import Employee, EmployeeType, OffPeriod, Schedule
from logic.planning import fill_schedule, toggle_schedule_state, create_schedule, clear_schedule
from views.confirmationDialogs import ConfirmScheduleUpdateDialog, ConfirmDeletionDialog
from views.editorDialogs import AddEmployeeDialog, AddOffPeriodDialog, AddRepeatingOffPeriodDialog
from views.editorDialogs import AddEmployeeTypeDialog
from views.editorWidgets import EmployeeEditorWidget, EditorWidget, EmployeeTypeEditorWidget, OffPeriodEditorWidget, \
    ScheduleEditorWidget
from views.helpers.helper_classes import CenteredItemDelegate, EmployeeItemDelegate, OffPeriodItemDelegate, \
    ScheduleItemDelegate
from views.helpers.helper_functions import load_ui_file, configure_month_box, configure_year_box


class TableDialog(QWidget):

    def __init__(self, table_ui_name: str, configure_widgets: bool = True):
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

        if configure_widgets:
            # widgets might be configured in a subclass afterwards
            self.configure_widgets()
            self.configure_search()

    def get_table(self) -> QTableView:
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
        self.editor.toggle_buttons(True)

    def configure_widgets(self):
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


class EmployeeTypeWidget(TableDialog):

    def __init__(self):
        super(EmployeeTypeWidget, self).__init__(table_ui_name="ui/employeeTypeView.ui")
        self.add_dialog = AddEmployeeTypeDialog(self)
        self.setup_table(EmployeeTypeModel(), range(1, 3))

        tableview: QTableView = self.get_table()
        delegate: CenteredItemDelegate = CenteredItemDelegate()
        tableview.setItemDelegate(delegate)

    def get_editor_widget(self) -> EditorWidget:
        return EmployeeTypeEditorWidget()

    def configure_search(self):
        self.searchLine.textChanged.connect(
            lambda x: self.reload_table_contents(EmployeeTypeModel(self.searchLine.text())))

    def get_selected_item(self):
        item_id = super(EmployeeTypeWidget, self).get_selected_item()
        item = find_employee_type_by_id(item_id)
        return item

    def add_item(self):
        self.add_dialog.clear_fields()
        self.add_dialog.exec_()

    def delete_item(self):
        dialog = ConfirmDeletionDialog(self)
        button = dialog.exec_()
        if button == QMessageBox.AcceptRole:
            item = self.get_selected_item()
            delete_item(item)
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
        super(OffPeriodWidget, self).__init__(table_ui_name="ui/offPeriodView.ui", configure_widgets=False)
        self.add_dialog = AddOffPeriodDialog(self)
        self.setup_table(OffPeriodModel(), range(1, 4))

        self.repeating_button: QPushButton = self.table_widget.repeatingButton  # noqa
        self.add_repeating_dialog = AddRepeatingOffPeriodDialog(self)

        tableview: QTableView = self.get_table()
        delegate: OffPeriodItemDelegate = OffPeriodItemDelegate()
        tableview.setItemDelegate(delegate)

        self.configure_widgets()

    def configure_widgets(self):
        super(OffPeriodWidget, self).configure_widgets()
        self.repeating_button.clicked.connect(self.repeating_day)

    def repeating_day(self):
        self.add_repeating_dialog.clear_fields()
        self.add_repeating_dialog.exec_()

    def get_editor_widget(self) -> EditorWidget:
        return OffPeriodEditorWidget()

    def configure_search(self):
        self.searchLine.textChanged.connect(
            lambda x: self.reload_table_contents(OffPeriodModel(self.searchLine.text())))

    def get_selected_item(self):
        item_id = super(OffPeriodWidget, self).get_selected_item()
        item = find_off_period_by_id(item_id)
        return item

    def add_item(self):
        self.add_dialog.clear_fields()
        self.add_dialog.exec_()

    def delete_item(self):
        dialog = ConfirmDeletionDialog(self)
        button = dialog.exec_()
        if button == QMessageBox.AcceptRole:
            item: OffPeriod = self.get_selected_item()
            delete_item(item)
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


class PlanningWidget(TableDialog):

    def __init__(self):
        super(PlanningWidget, self).__init__(table_ui_name="ui/planningView.ui", configure_widgets=False)

        self.month_box: QComboBox = self.table_widget.monthBox  # noqa
        self.year_box: QSpinBox = self.table_widget.yearBox  # noqa
        self.create_button: QPushButton = self.table_widget.createButton  # noqa
        self.planning_button: QPushButton = self.table_widget.planningButton  # noqa
        self.activate_button: QPushButton = self.table_widget.activateButton  # noqa
        self.clear_button: QPushButton = self.table_widget.clearButton  # noqa
        self.export_button: QPushButton = self.table_widget.exportButton  # noqa

        self.configure_widgets()
        self.configure_search()

        year = self.year_box.value()
        month = self.month_box.currentIndex() + 1
        self.setup_table(ScheduleModel(year, month), range(1, 5))

        tableview: QTableView = self.get_table()
        delegate: ScheduleItemDelegate = ScheduleItemDelegate()
        tableview.setItemDelegate(delegate)
        tableview.verticalHeader().setVisible(False)

        self.trigger_reload()

    def get_editor_widget(self) -> EditorWidget:
        return ScheduleEditorWidget()

    def configure_widgets(self):
        self.configure_month_box()
        self.configure_year_box()
        self.create_button.clicked.connect(self.create_schedule)
        self.planning_button.clicked.connect(self.fill_schedule)
        self.activate_button.clicked.connect(self.activate_schedule)
        self.clear_button.clicked.connect(self.clear_schedule)
        self.export_button.clicked.connect(self.export_schedule)
        self.editor.buttonBox.accepted.connect(self.commit_changes)
        self.editor.buttonBox.rejected.connect(self.revert_changes)

    def configure_search(self):
        self.searchLine.textChanged.connect(
            lambda x: self.reload_table_contents(self.update_search_model()))

    def get_selected_item(self):
        item_id = super(PlanningWidget, self).get_selected_item()
        item = find_schedule_by_id(item_id)
        return item

    def update_search_model(self) -> ScheduleModel:
        year: int = self.year_box.value()
        month: int = self.month_box.currentIndex() + 1
        search: str = self.searchLine.text()
        return ScheduleModel(year, month, search)

    def configure_month_box(self):
        app = QApplication.instance()
        configure_month_box(app, self.month_box)
        self.month_box.currentIndexChanged.connect(self.trigger_reload)

    def configure_year_box(self):
        configure_year_box(self.year_box)
        self.year_box.valueChanged.connect(self.trigger_reload)

    def trigger_reload(self):
        month: int = self.month_box.currentIndex() + 1
        year: int = self.year_box.value()
        planning_needed: bool = not schedule_exists(year, month)
        self.create_button.setEnabled(planning_needed)
        plan_active: bool = shift_plan_active(year, month)
        self.activate_button.setChecked(plan_active)
        self.planning_button.setEnabled(not plan_active)
        self.clear_button.setEnabled(not plan_active)
        self.export_button.setEnabled(not planning_needed)
        self.reload_table_contents(ScheduleModel(year, month))

    def create_schedule(self):
        month: int = self.month_box.currentIndex() + 1
        year: int = self.year_box.value()
        create_schedule(month, year)
        self.create_button.setEnabled(False)
        self.reload_table_contents(ScheduleModel(year, month))

    def fill_schedule(self):
        month: int = self.month_box.currentIndex() + 1
        year: int = self.year_box.value()
        fill_schedule(month, year)
        self.reload_table_contents(ScheduleModel(year, month))

    def activate_schedule(self):
        month: int = self.month_box.currentIndex() + 1
        year: int = self.year_box.value()
        activated: bool = self.activate_button.isChecked()
        toggle_schedule_state(year, month, activated)
        self.trigger_reload()

    def clear_schedule(self):
        month: int = self.month_box.currentIndex() + 1
        year: int = self.year_box.value()
        clear_schedule(year, month)
        self.trigger_reload()

    def commit_changes(self):
        month: int = self.month_box.currentIndex() + 1
        year: int = self.year_box.value()
        search: str = self.searchLine.text()

        activated: bool = self.activate_button.isChecked()
        value_dict: dict = self.editor.get_values()
        if activated:
            dialog = ConfirmScheduleUpdateDialog(self)
            button = dialog.exec_()
            if button == QMessageBox.AcceptRole:
                update_schedule(value_dict)
        else:
            update_schedule(value_dict)
        self.reload_table_contents(ScheduleModel(year, month, search))

    def revert_changes(self):
        schedule: Schedule = find_schedule_by_id(self.editor.item_id)
        self.editor.fill_fields(schedule)

    def export_schedule(self):
        export_dialog: QFileDialog = QFileDialog(parent=self)
        export_dialog.setWindowTitle(self.tr("Export Schedule"))
        export_dialog.setDirectory(str(properties.user_home))
        export_dialog.setAcceptMode(QFileDialog.AcceptSave)
        export_dialog.setNameFilter(self.tr("Spreadsheets (*.xlsx)"))
        export_dialog.setDefaultSuffix("xlsx")
        if export_dialog.exec_() == QFileDialog.Accepted:
            file_path: str = export_dialog.selectedFiles()[0]
            table: QTableView = self.get_table()
            model: ScheduleModel = table.model()
            model.export_schedule(file_path, table.rootIndex())
