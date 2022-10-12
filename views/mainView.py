from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFileDialog

from logic.config import properties
from logic.database import init_database
from logic.table_models import EmployeeTypeModel, EmployeeModel, OffPeriodModel, ScheduleModel
from views.base_classes import OptionsEditorDialog, TableDialog, LogDialog
from views.base_functions import load_ui_file
from views.employee import EmployeeWidget
from views.employeeType import EmployeeTypeWidget
from views.offPeriod import OffPeriodWidget
from views.schedule import PlanningWidget


class MainWindow(QMainWindow):

    def __init__(self, form):
        super().__init__(parent=form)
        self.adjustSize()

        form.setWindowTitle("Shift")
        form.setWindowIcon(QIcon("icon.svg"))

        self.layout = QVBoxLayout(form)
        self.options_dialog = OptionsEditorDialog(self)
        self.log_dialog = LogDialog(self)

        ui_file_name = "ui/main.ui"
        ui_file = load_ui_file(ui_file_name)

        loader = QUiLoader()
        self.widget = loader.load(ui_file, form)
        ui_file.close()

        self.tabview = self.widget.tabview
        self.load_db_button = self.widget.loadDbButton
        self.options_button = self.widget.optionsButton
        self.log_button = self.widget.logButton

        self.configure_buttons()
        self.configure_tabview()

        self.layout.addWidget(self.widget)

        form.resize(1600, 900)

    def configure_tabview(self):
        employee_type_widget = EmployeeTypeWidget()
        self.tabview.addTab(employee_type_widget, self.tr("Employee Types"))

        employee_widget = EmployeeWidget()
        self.tabview.addTab(employee_widget, self.tr("Employees"))

        off_period_widget = OffPeriodWidget()
        self.tabview.addTab(off_period_widget, self.tr("Days Off"))

        planning_widget = PlanningWidget()
        self.tabview.addTab(planning_widget, self.tr("Planning"))

        self.tabview.currentChanged.connect(self.reload_current_widget)

    def reload_current_widget(self):
        current: QWidget = self.tabview.currentWidget()
        if isinstance(current, TableDialog):
            search = current.searchLine.text()
            if isinstance(current, EmployeeTypeWidget):
                current.reload_table_contents(EmployeeTypeModel(search))
            elif isinstance(current, EmployeeWidget):
                current.reload_table_contents(EmployeeModel(search))
            elif isinstance(current, OffPeriodWidget):
                year = current.year_box.value()
                month = current.month_box.currentIndex() + 1
                current.reload_table_contents(OffPeriodModel(year, month, search))
            elif isinstance(current, PlanningWidget):
                year = current.year_box.value()
                month = current.month_box.currentIndex() + 1
                current.reload_table_contents(ScheduleModel(year, month, search))

    def configure_buttons(self):
        self.load_db_button.clicked.connect(self.load_database)
        self.options_button.clicked.connect(self.open_options)
        self.log_button.clicked.connect(self.open_logs)

    def load_database(self):
        load_dialog: QFileDialog = QFileDialog(parent=self)
        load_dialog.setWindowTitle(self.tr("Load Database"))
        load_dialog.setDirectory(str(properties.user_home))
        load_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        load_dialog.setNameFilter(self.tr("SQLite3 (*.db)"))
        if load_dialog.exec_() == QFileDialog.Accepted:
            file_path: str = load_dialog.selectedFiles()[0]
            properties.database_path = file_path
            init_database(True)
            self.reload_current_widget()
            properties.write_config_file()

    def open_options(self):
        self.options_dialog.exec_()

    def open_logs(self):
        self.log_dialog.load_log_files()
        self.log_dialog.exec_()
