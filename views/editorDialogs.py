import qdarktheme
from PySide6.QtCore import QLibraryInfo, QTranslator, QLocale
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QHBoxLayout, QDialog, QMainWindow, QApplication, QDialogButtonBox

from logic.config import properties
from logic.database import persist_employee, persist_employee_type, find_employee_types
from logic.model import EmployeeType, Employee, RotationPeriod
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

        self.buttonBox: QDialogButtonBox

    def configure_widgets(self):
        self.buttonBox.accepted.connect(self.commit)
        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.button(QDialogButtonBox.Ok).setText(self.tr("OK"))
        self.buttonBox.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))

    def commit(self):
        """Needs specific implementation"""
        pass


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
        e_types = find_employee_types()
        for e_type in e_types:
            self.widget.typeCombobox.addItem(e_type.designation, userData=None)  # noqa

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa

        self.configure_widgets()

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
        self.parent.reload_table_contents()
        self.close()

    def clear_fields(self):
        self.widget.designationEdit.setText("")  # noqa
        self.widget.rotationBox.setCurrentIndex(0)  # noqa
