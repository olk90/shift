from PySide6.QtWidgets import QWidget, QHBoxLayout, QDialogButtonBox, QTableView, QMessageBox

from logic.database import persist_item, find_employee_type_by_id, delete_item, update_employee_type
from logic.table_models import EmployeeTypeModel
from logic.model import RotationPeriod, EmployeeType
from views.confirmationDialogs import ConfirmDeletionDialog
from views.base_classes import EditorDialog, EditorWidget, TableDialog, CenteredItemDelegate


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
        persist_item(employee_type)
        self.parent.reload_table_contents(model=EmployeeTypeModel())
        self.close()

    def clear_fields(self):
        self.widget.designationEdit.setText("")  # noqa
        self.widget.rotationBox.setCurrentIndex(0)  # noqa


class EmployeeTypeEditorWidget(EditorWidget):

    def __init__(self, item_id=None):
        super().__init__(ui_file_name="ui/employeeTypeEditor.ui", item_id=item_id)

        self.designationEdit = self.widget.designationEdit  # noqa
        self.rotationBox = self.widget.rotationBox  # noqa

        self.rotationBox.addItems(RotationPeriod.periods)

    def fill_fields(self, employee_type: EmployeeType):
        self.item_id = employee_type.id
        self.designationEdit.setText(employee_type.designation)
        self.rotationBox.setCurrentIndex(RotationPeriod.periods.index(employee_type.rotation_period))  # noqa

    def get_values(self) -> dict:
        return {
            "item_id": self.item_id,
            "designation": self.designationEdit.text(),
            "rotation_period": self.rotationBox.currentText()
        }


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
