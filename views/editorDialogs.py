from datetime import datetime

import qdarktheme
from PySide6.QtCore import QDate
from PySide6.QtCore import QLibraryInfo, QTranslator, QLocale
from PySide6.QtSql import QSqlTableModel, QSqlQueryModel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout, QDialog, QMainWindow, QApplication, QDialogButtonBox

from logic.config import properties
from logic.database import persist_employee, persist_employee_type, EmployeeModel, \
    EmployeeTypeModel, persist_off_period, OffPeriodModel, configure_query_model
from logic.model import EmployeeType, Employee, RotationPeriod, OffPeriod
from logic.queries import build_employee_fullname_query, build_employee_type_designation_query
from views.helpers import load_ui_file


class EditorDialog(QDialog):

    def __init__(self, parent: QWidget, ui_file_name: str):
        super(EditorDialog, self).__init__()
        self.parent = parent
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setWindowTitle(" ")

        ui_file = load_ui_file(ui_file_name)

        loader = QUiLoader()
        self.widget = loader.load(ui_file)
        ui_file.close()

        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa

    def configure_widgets(self):
        self.buttonBox.accepted.connect(self.commit)
        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.button(QDialogButtonBox.Ok).setText(self.tr("OK"))
        self.buttonBox.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))

    def commit(self):
        """Must be implemented by subclass"""


class OptionsEditorDialog(EditorDialog):

    def __init__(self, parent: QMainWindow):
        super().__init__(parent=parent, ui_file_name="ui/optionsEditor.ui")

        self.localeBox: QComboBox = self.widget.localeBox  # noqa
        self.themeBox: QComboBox = self.widget.themeBox  # noqa
        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa

        self.configure_widgets()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

    def configure_widgets(self):
        super(OptionsEditorDialog, self).configure_widgets()

        self.localeBox.addItems(properties.locales)
        self.localeBox.setCurrentIndex(properties.locale_index)

        self.themeBox.addItems(properties.get_themes())
        self.themeBox.setCurrentIndex(properties.theme_index)

    def commit(self):
        self.update_locale()
        self.update_theme()

        properties.write_config_file()
        self.close()

    def update_locale(self):
        selected_index = self.localeBox.currentIndex()
        properties.locale_index = selected_index
        app = QApplication.instance()

        path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
        translator = QTranslator(app)
        if translator.load(QLocale.system(), 'qtbase', '_', path):
            app.installTranslator(translator)
        translator = QTranslator(app)
        path = './translations'
        if selected_index == 1:
            translator.load(QLocale(QLocale.German, QLocale.Germany), 'base', '_', path)
            app.installTranslator(translator)

    def update_theme(self):
        selected_index = self.themeBox.currentIndex()
        properties.theme_index = selected_index
        app = QApplication.instance()
        if selected_index == 0:
            app.setStyleSheet(qdarktheme.load_stylesheet())
        elif selected_index == 1:
            app.setStyleSheet(qdarktheme.load_stylesheet("light"))
        else:
            app.setStyleSheet(None)


class AddEmployeeDialog(EditorDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent, ui_file_name="ui/employeeEditor.ui")

        self.widget.editorTitle.setText(self.tr("Add Employee"))  # noqa
        self.type_box = self.widget.typeCombobox  # noqa
        query: str = build_employee_type_designation_query()
        configure_query_model(self.type_box, query)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa

        self.configure_widgets()

    def commit(self):
        first_name: str = self.widget.firstNameEdit.text()  # noqa
        last_name: str = self.widget.lastNameEdit.text()  # noqa
        reference: int = self.widget.referenceSpinner.value()  # noqa
        penalty: int = self.widget.penaltySpinner.value()  # noqa
        night_shifts: bool = self.widget.nightShiftsEdit.isChecked()  # noqa

        model: QSqlQueryModel = self.type_box.model()
        index: int = self.type_box.currentIndex()
        et_id = model.index(index, 1).data()
        employee = Employee(firstname=first_name, lastname=last_name, referenceValue=reference,
                            night_shifts=night_shifts, e_type_id=et_id, penalty=penalty)
        persist_employee(employee)
        self.parent.reload_table_contents(model=EmployeeModel())
        self.close()

    def clear_fields(self):
        query: str = build_employee_type_designation_query()
        self.type_box.model().setQuery(query)
        self.widget.firstNameEdit.setText("")  # noqa
        self.widget.lastNameEdit.setText("")  # noqa
        self.widget.referenceSpinner.setValue(0)  # noqa
        self.widget.penaltySpinner.setValue(0)  # noqa
        self.widget.typeCombobox.setCurrentIndex(0)  # noqa


class AddEmployeeTypeDialog(EditorDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent, ui_file_name="ui/employeeTypeEditor.ui")

        self.widget.editorTitle.setText(self.tr("Add Employee Type"))  # noqa
        self.widget.rotationBox.addItems(RotationPeriod.periods)  # noqa

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa

        self.configure_widgets()

    def commit(self):
        designation: str = self.widget.designationEdit.text()  # noqa
        rotation_period: str = self.widget.rotationBox.currentText()  # noqa
        employee_type = EmployeeType(designation=designation, rotation_period=rotation_period)
        persist_employee_type(employee_type)
        self.parent.reload_table_contents(model=EmployeeTypeModel())
        self.close()

    def clear_fields(self):
        self.widget.designationEdit.setText("")  # noqa
        self.widget.rotationBox.setCurrentIndex(0)  # noqa


class AddOffPeriodDialog(EditorDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent, ui_file_name="ui/offPeriodAddDialog.ui")

        self.employee_box: QComboBox = self.widget.employeeBox  # noqa
        query: str = build_employee_fullname_query()
        configure_query_model(self.employee_box, query)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa

        self.configure_widgets()

    def commit(self):
        model: QSqlTableModel = self.employee_box.model()
        index: int = self.employee_box.currentIndex()
        e_id = model.index(index, 1).data()
        start: QDate = self.widget.startEdit.selectedDate()  # noqa
        start_date = datetime(start.year(), start.month(), start.day())
        end: QDate = self.widget.endEdit.selectedDate()  # noqa
        end_date = datetime(end.year(), end.month(), end.day())
        off_period = OffPeriod(e_id=e_id, start=start_date, end=end_date)
        persist_off_period(off_period)
        self.parent.reload_table_contents(model=OffPeriodModel())
        self.close()

    def clear_fields(self):
        query: str = build_employee_fullname_query()
        self.employee_box.model().setQuery(query)
        self.employee_box.setCurrentIndex(0)  # noqa
        self.widget.startEdit.setSelectedDate(QDate.currentDate())  # noqa
        self.widget.endEdit.setSelectedDate(QDate.currentDate())  # noqa
