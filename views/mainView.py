from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QVBoxLayout

from views.editorDialogs import OptionsEditorDialog
from views.employeeDialog import EmployeeWidget
from views.helpers import load_ui_file


class MainWindow(QMainWindow):

    def __init__(self, form):
        super().__init__(parent=form)
        self.adjustSize()

        form.setWindowTitle("Shift")

        self.layout = QVBoxLayout(form)
        self.options_dialog = OptionsEditorDialog(self)

        ui_file_name = "ui/main.ui"
        ui_file = load_ui_file(ui_file_name)

        loader = QUiLoader()
        self.widget = loader.load(ui_file, form)
        ui_file.close()

        self.optionsButton = self.widget.optionsButton  # noqa

        self.configure_buttons()
        self.configure_tabview()

        self.layout.addWidget(self.widget)

        form.resize(1600, 900)

    def configure_tabview(self):
        tabview = self.widget.tabview  # noqa -> tabview is loaded from ui file

        employee_widget = EmployeeWidget()
        tabview.addTab(employee_widget, self.tr("Employees"))

    def configure_buttons(self):
        self.optionsButton.clicked.connect(self.open_options)

    def open_options(self):
        self.options_dialog.exec_()
