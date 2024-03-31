from PySide6.QtWidgets import QWidget, QHBoxLayout, QDialogButtonBox, QTableView, QMessageBox, QLabel, QComboBox, \
    QLineEdit

from logic.database import persist_item, delete_item, update_employee_type, find_by_id
from logic.table_models import EmployeeTypeModel
from logic.model import RotationPeriod, EmployeeType
from views.confirmationDialogs import ConfirmDeletionDialog
from views.base_classes import EditorDialog, EditorWidget, TableDialog, CenteredItemDelegate


class AddEmployeeTypeDialog(EditorDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent, ui_file_name="ui/employeeTypeEditor.ui")

        self.get_widget(QLabel, "editorTitle").setText(self.tr("Add Employee Type"))

        self.designation_edit: QLineEdit = self.get_widget(QLineEdit, "designationEdit")
        self.designation_edit.textChanged.connect(self.widget.validate)

        self.widget.append_validation_fields(self.designation_edit)

        self.rotation_box = self.get_widget(QComboBox, "rotationBox")
        self.rotation_box.addItems(RotationPeriod.periods)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.button_box: QDialogButtonBox = self.get_widget(QDialogButtonBox, "buttonBox")

        self.configure_widgets()

    def commit(self):
        designation: str = self.designation_edit.text()
        rotation_period: str = self.rotation_box.currentText()
        employee_type = EmployeeType(designation=designation, rotation_period=rotation_period)
        persist_item(employee_type)
        self.parent.reload_table_contents(model=EmployeeTypeModel())
        self.close()


class EmployeeTypeEditorWidget(EditorWidget):

    def __init__(self, item_id=None):
        super().__init__(ui_file_name="ui/employeeTypeEditor.ui", item_id=item_id)

        self.designation_edit = self.widget.designationEdit

        self.designation_edit.textChanged.connect(self.validate)
        self.append_validation_fields(self.designation_edit)

        self.rotation_box = self.widget.rotationBox

        self.rotation_box.addItems(RotationPeriod.periods)

    def fill_fields(self, employee_type: EmployeeType):
        self.item_id = employee_type.id
        self.designation_edit.setText(employee_type.designation)
        self.rotation_box.setCurrentIndex(RotationPeriod.periods.index(employee_type.rotation_period))

    def get_values(self) -> dict:
        return {
            "item_id": self.item_id,
            "designation": self.designation_edit.text(),
            "rotation_period": self.rotation_box.currentText()
        }

    def clear_fields(self):
        self.designation_edit.setText("")
        self.rotation_box.setCurrentIndex(0)
        self.toggle_buttons(False, False)


class EmployeeTypeWidget(TableDialog):

    def __init__(self):
        super(EmployeeTypeWidget, self).__init__(table_ui_name="ui/employeeTypeView.ui")
        self.add_dialog = AddEmployeeTypeDialog(self)
        self.setup_table(EmployeeTypeModel())

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
        item = find_by_id(item_id, EmployeeType)
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
            self.editor.clear_fields()

    def commit_changes(self):
        value_dict: dict = self.editor.get_values()
        update_employee_type(value_dict)
        search = self.searchLine.text()
        self.reload_table_contents(model=EmployeeTypeModel(search))

    def revert_changes(self):
        e_type: EmployeeType = find_by_id(self.editor.item_id, EmployeeType)
        self.editor.fill_fields(e_type)
