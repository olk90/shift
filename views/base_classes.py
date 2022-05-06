from typing import Union

import qdarktheme
from PySide6.QtCore import QLibraryInfo, QTranslator, QLocale, QItemSelectionModel, QModelIndex, \
    QPersistentModelIndex, Qt
from PySide6.QtGui import QPainter
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDialog, QWidget, QDialogButtonBox, QHBoxLayout, QMainWindow, QComboBox, QApplication, \
    QLineEdit, QTableView, QAbstractItemView, QHeaderView, QItemDelegate, QStyleOptionViewItem

from logic.config import properties
from logic.database import SearchTableModel
from views.base_functions import load_ui_file


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


class EditorWidget(QWidget):

    def __init__(self, ui_file_name: str, item_id: int = None):
        super(EditorWidget, self).__init__()
        self.item_id = item_id
        ui_file = load_ui_file(ui_file_name)

        loader = QUiLoader()
        self.widget = loader.load(ui_file)
        ui_file.close()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa
        self.configure_buttons()

    def configure_buttons(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setText(self.tr("OK"))
        self.buttonBox.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))
        self.toggle_buttons(False)

    def toggle_buttons(self, activate: bool):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(activate)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(activate)

    def get_values(self) -> dict:
        """Must be implemented by subclass"""

    def fill_fields(self, item):
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


class CenteredItemDelegate(QItemDelegate):

    def __init__(self):
        super(CenteredItemDelegate, self).__init__()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: Union[QModelIndex, QPersistentModelIndex]):
        option.displayAlignment = Qt.AlignCenter
        super(CenteredItemDelegate, self).paint(painter, option, index)
