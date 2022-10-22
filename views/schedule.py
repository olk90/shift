import datetime
from typing import Union

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
from PySide6.QtWidgets import QComboBox, QToolButton, QTextEdit, QSpinBox, QPushButton, QTableView, QMessageBox, \
    QFileDialog, QStyleOptionViewItem, QLabel

from logic.config import properties
from logic.database import configure_query_model, schedule_exists, shift_plan_active, update_schedule, find_by_id
from logic.model import Schedule, Employee
from logic.queries import day_shift_replacement_query, night_shift_replacement_query
from logic.schedule.planning import create_schedule, fill_schedule, toggle_schedule_state, clear_schedule
from logic.table_models import ScheduleModel
from views.base_classes import EditorWidget, TableDialog, CenteredItemDelegate
from views.base_functions import configure_month_box, configure_year_box
from views.confirmationDialogs import ConfirmDeletionDialog, ConfirmScheduleUpdateDialog


class ScheduleEditorWidget(EditorWidget):

    def __init__(self, item_id=None):
        super().__init__(ui_file_name="ui/scheduleEditor.ui", item_id=item_id)

        self.d_id: int = 0
        self.n_id: int = 0

        self.date_display: QLabel = self.widget.dateDisplay

        self.day_box: QComboBox = self.widget.dayBox
        day_query: str = day_shift_replacement_query()
        configure_query_model(self.day_box, day_query)
        self.day_box.setCurrentIndex(-1)
        self.day_box.currentIndexChanged.connect(lambda x: self.update_selection_id(self.day_box))

        self.night_box: QComboBox = self.widget.nightBox
        night_query: str = night_shift_replacement_query()
        configure_query_model(self.night_box, night_query)
        self.night_box.setCurrentIndex(-1)
        self.night_box.currentIndexChanged.connect(lambda x: self.update_selection_id(self.night_box))

        self.remove_day_button: QToolButton = self.widget.removeDayButton
        self.remove_night_button: QToolButton = self.widget.removeNightButton
        self.remove_day_button.clicked.connect(lambda x: self.remove_shift(self.day_box))
        self.remove_night_button.clicked.connect(lambda x: self.remove_shift(self.night_box))

        self.comment_edit: QTextEdit = self.widget.commentEdit

    def update_selection_id(self, box: QComboBox):
        index = box.currentIndex()
        selected_id: int = box.model().index(index, 1).data()

        if box == self.day_box:
            self.d_id = selected_id
        elif box == self.night_box:
            self.n_id = selected_id

    def remove_shift(self, box: QComboBox):
        box.setCurrentIndex(-1)
        if box == self.day_box:
            self.d_id = None
        elif box == self.night_box:
            self.n_id = None

    def fill_fields(self, schedule: Schedule):

        day_query: str = day_shift_replacement_query()
        configure_query_model(self.day_box, day_query)
        night_query: str = night_shift_replacement_query()
        configure_query_model(self.night_box, night_query)

        self.item_id = schedule.id
        self.date_display.setText(str(schedule.date.strftime("%a, %d %b %Y")))

        self.d_id: int = schedule.day_id
        day_shift: Employee = find_by_id(self.d_id, Employee)
        if day_shift:
            self.day_box.setCurrentText(day_shift.get_full_name_and_score())
        else:
            self.day_box.setCurrentIndex(-1)

        self.n_id: int = schedule.night_id
        night_shift: Employee = find_by_id(self.n_id, Employee)
        if night_shift:
            self.night_box.setCurrentText(night_shift.get_full_name_and_score())
        else:
            self.night_box.setCurrentIndex(-1)

        self.comment_edit.setText(schedule.comment)

    def get_values(self) -> dict:
        text: str = self.comment_edit.toPlainText()
        return {
            "item_id": self.item_id,
            "date": self.date_display.text(),
            "d_id": self.d_id,
            "n_id": self.n_id,
            "comment": text
        }


class PlanningWidget(TableDialog):

    def __init__(self):
        super(PlanningWidget, self).__init__(table_ui_name="ui/planningView.ui", configure_widgets=False)

        self.month_box: QComboBox = self.table_widget.monthBox
        self.year_box: QSpinBox = self.table_widget.yearBox
        self.create_button: QPushButton = self.table_widget.createButton
        self.planning_button: QPushButton = self.table_widget.planningButton
        self.activate_button: QPushButton = self.table_widget.activateButton
        self.clear_button: QPushButton = self.table_widget.clearButton
        self.export_button: QPushButton = self.table_widget.exportButton

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
        item = find_by_id(item_id, Schedule)
        return item

    def update_search_model(self) -> ScheduleModel:
        year: int = self.year_box.value()
        month: int = self.month_box.currentIndex() + 1
        search: str = self.searchLine.text()
        return ScheduleModel(year, month, search)

    def configure_month_box(self):
        configure_month_box(self.month_box)
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
        dialog = ConfirmDeletionDialog(self)
        button = dialog.exec_()
        if button == QMessageBox.AcceptRole:
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
        schedule: Schedule = find_by_id(self.editor.item_id, Schedule)
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


class ScheduleItemDelegate(CenteredItemDelegate):

    def __init__(self):
        super(ScheduleItemDelegate, self).__init__()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: Union[QModelIndex, QPersistentModelIndex]):
        model = index.model()
        date_str: str = model.index(index.row(), 1).data()
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        if date.weekday() > 3:
            theme: int = properties.theme_index
            color: QColor = QColor("#3f4042") if theme == 0 else QColor("#dadce0")
            brush: QBrush = QBrush(color)
            painter.setBrush(brush)
            pen = QPen()
            pen.setStyle(Qt.NoPen)
            painter.setPen(pen)
            painter.drawRect(option.rect)
        if index.column() == 1:
            text = date.strftime("%a, %d %b %Y")
            option.displayAlignment = Qt.AlignCenter
            self.drawDisplay(painter, option, option.rect, text)
        else:
            super(ScheduleItemDelegate, self).paint(painter, option, index)
