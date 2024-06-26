import datetime
from typing import Union

from PySide6.QtCore import QDate, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QPainter
from PySide6.QtSql import QSqlTableModel
from PySide6.QtWidgets import QWidget, QComboBox, QHBoxLayout, QDialogButtonBox, QSpinBox, QPushButton, QTableView, \
    QMessageBox, QStyleOptionViewItem, QCalendarWidget

from logic.config import properties
from logic.database import configure_query_model, persist_item, delete_item, update_off_period, find_by_id
from logic.model import OffPeriod, Employee
from logic.queries import employee_fullname_query
from logic.table_models import OffPeriodModel
from views.base_classes import EditorDialog, EditorWidget, TableDialog, CenteredItemDelegate
from views.base_functions import configure_month_box, configure_weekday_box, configure_year_box, get_day_range
from views.confirmationDialogs import ConfirmDeletionDialog


class AddOffPeriodDialog(EditorDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent, ui_file_name="ui/offPeriodAddDialog.ui")

        self.employee_box: QComboBox = self.get_widget(QComboBox, "employeeBox")
        query: str = employee_fullname_query()
        configure_query_model(self.employee_box, query)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.button_box: QDialogButtonBox = self.get_widget(QDialogButtonBox, "buttonBox")
        self.start_edit: QCalendarWidget = self.get_widget(QCalendarWidget, "startEdit")
        self.end_edit: QCalendarWidget = self.get_widget(QCalendarWidget, "endEdit")

        self.parent = parent

        self.configure_widgets()

    def configure_widgets(self):
        super(AddOffPeriodDialog, self).configure_widgets()
        self.end_edit.selectionChanged.connect(self.update_start_date)
        self.start_edit.selectionChanged.connect(self.update_end_date)

    def update_start_date(self):
        start_date: QDate = self.start_edit.selectedDate()
        end_date: QDate = self.end_edit.selectedDate()
        if end_date < start_date:
            self.start_edit.setSelectedDate(end_date)

    def update_end_date(self):
        start_date: QDate = self.start_edit.selectedDate()
        end_date: QDate = self.end_edit.selectedDate()
        if start_date > end_date:
            self.end_edit.setSelectedDate(start_date)

    def commit(self):
        model: QSqlTableModel = self.employee_box.model()
        index: int = self.employee_box.currentIndex()
        e_id = model.index(index, 1).data()
        start: QDate = self.start_edit.selectedDate()
        year = start.year()
        month = start.month()
        start_date = datetime.date(year, month, start.day())
        end: QDate = self.end_edit.selectedDate()
        end_date = datetime.date(end.year(), end.month(), end.day())
        off_period = OffPeriod(e_id=e_id, start=start_date, end=end_date)
        persist_item(off_period)
        self.parent.reload_table_contents(model=OffPeriodModel(year, month))
        self.close()

    def clear_fields(self):
        query: str = employee_fullname_query()
        self.employee_box.model().setQuery(query)
        self.employee_box.setCurrentIndex(0)
        year = self.parent.year
        month = self.parent.month
        selected_date: QDate = QDate(year, month, 1)
        self.start_edit.setSelectedDate(selected_date)
        self.end_edit.setSelectedDate(selected_date)


class AddRepeatingOffPeriodDialog(EditorDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent, ui_file_name="ui/repeatingOffPeriodAddDialog.ui")
        self.parent = parent

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.buttonBox: QDialogButtonBox = self.widget.buttonBox

        self.employee_box: QComboBox = self.get_widget(QComboBox, "employeeBox")
        query: str = employee_fullname_query()
        configure_query_model(self.employee_box, query)

        self.month_box: QComboBox = self.get_widget(QComboBox, "monthBox")
        self.year_box: QSpinBox = self.get_widget(QSpinBox, "yearBox")
        self.weekday_box: QComboBox = self.get_widget(QComboBox, "weekdayBox")

        self.configure_widgets()

    def configure_widgets(self):
        super(AddRepeatingOffPeriodDialog, self).configure_widgets()
        self.reload_month_and_year()
        configure_weekday_box(self.weekday_box)

    def clear_fields(self):
        query: str = employee_fullname_query()
        self.employee_box.model().setQuery(query)
        self.employee_box.setCurrentIndex(0)
        self.reload_month_and_year()

    def reload_month_and_year(self):
        initial_date = datetime.date(year=self.parent.year, month=self.parent.month, day=1)
        configure_month_box(self.month_box, initial_date)
        configure_year_box(self.year_box, initial_date)

    def commit(self):
        model: QSqlTableModel = self.employee_box.model()
        index: int = self.employee_box.currentIndex()
        e_id = model.index(index, 1).data()
        month: int = self.month_box.currentIndex() + 1
        year: int = self.year_box.value()
        weekday: int = self.weekday_box.currentIndex()
        day_range = get_day_range(month, year)

        s = properties.open_session()
        for day in day_range:
            date = datetime.date(year, month, day)
            if date.weekday() == weekday:
                off_period = OffPeriod(start=date, end=date, e_id=e_id)
                s.add(off_period)
        s.commit()
        self.parent.reload_table_contents(model=OffPeriodModel(year, month))


class OffPeriodEditorWidget(EditorWidget):

    def __init__(self, item_id=None):
        super().__init__(ui_file_name="ui/offPeriodEditor.ui", item_id=item_id)

        self.name_label = self.widget.name_label
        self.start_edit = self.widget.startEdit
        self.end_edit = self.widget.endEdit
        self.configure_widgets()

    def configure_widgets(self):
        self.end_edit.selectionChanged.connect(self.update_start)
        self.start_edit.selectionChanged.connect(self.update_end)

    def update_start(self):
        end_date: QDate = self.end_edit.selectedDate()
        self.start_edit.setMaximumDate(end_date)

    def update_end(self):
        start_date: QDate = self.start_edit.selectedDate()
        self.end_edit.setMinimumDate(start_date)

    def fill_fields(self, period: OffPeriod):
        self.item_id = period.id
        employee: Employee = find_by_id(period.e_id, Employee)
        self.name_label.setText(employee.get_full_name())

        start = period.start
        q_start = QDate(start.year, start.month, start.day)
        self.start_edit.setSelectedDate(q_start)

        end = period.end
        q_end = QDate(end.year, end.month, end.day)
        self.end_edit.setSelectedDate(q_end)

    def get_values(self) -> dict:
        return {
            "item_id": self.item_id,
            "start": self.start_edit.selectedDate(),
            "end": self.end_edit.selectedDate()
        }


class OffPeriodWidget(TableDialog):

    def __init__(self):
        super(OffPeriodWidget, self).__init__(table_ui_name="ui/offPeriodView.ui", configure_widgets=False)

        self.month_box: QComboBox = self.table_widget.monthBox
        self.year_box: QSpinBox = self.table_widget.yearBox
        self.configure_widgets()

        self.year = self.year_box.value()
        self.month = self.month_box.currentIndex() + 1
        self.setup_table(OffPeriodModel(self.year, self.month))

        self.add_dialog = AddOffPeriodDialog(self)

        self.repeating_button: QPushButton = self.table_widget.repeatingButton
        self.add_repeating_dialog = AddRepeatingOffPeriodDialog(self)
        self.repeating_button.clicked.connect(self.repeating_day)

        tableview: QTableView = self.get_table()
        delegate: OffPeriodItemDelegate = OffPeriodItemDelegate()
        tableview.setItemDelegate(delegate)

        self.configure_search()

    def configure_widgets(self):
        super(OffPeriodWidget, self).configure_widgets()
        self.configure_month_box()
        self.configure_year_box()

    def configure_month_box(self):
        configure_month_box(self.month_box)
        self.month_box.currentIndexChanged.connect(self.trigger_reload)

    def configure_year_box(self):
        configure_year_box(self.year_box)
        self.year_box.valueChanged.connect(self.trigger_reload)

    def trigger_reload(self):
        self.month = self.month_box.currentIndex() + 1
        self.year = self.year_box.value()
        self.reload_table_contents(OffPeriodModel(self.year, self.month))

    def repeating_day(self):
        self.add_repeating_dialog.clear_fields()
        self.add_repeating_dialog.exec_()

    def get_editor_widget(self) -> EditorWidget:
        return OffPeriodEditorWidget()

    def configure_search(self):
        self.searchLine.textChanged.connect(
            lambda x: self.reload_table_contents(self.update_search_model()))

    def update_search_model(self) -> OffPeriodModel:
        year: int = self.year_box.value()
        month: int = self.month_box.currentIndex() + 1
        search: str = self.searchLine.text()
        return OffPeriodModel(year, month, search)

    def get_selected_item(self):
        item_id = super(OffPeriodWidget, self).get_selected_item()
        item = find_by_id(item_id, OffPeriod)
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
            self.reload_table_contents(model=OffPeriodModel(self.year, self.month, search))
            self.editor.toggle_buttons(False)

    def commit_changes(self):
        value_dict: dict = self.editor.get_values()
        update_off_period(value_dict)
        search = self.searchLine.text()
        self.reload_table_contents(model=OffPeriodModel(self.year, self.month, search))

    def revert_changes(self):
        period: OffPeriod = find_by_id(self.editor.item_id, OffPeriod)
        self.editor.fill_fields(period)


class OffPeriodItemDelegate(CenteredItemDelegate):

    def __init__(self):
        super(OffPeriodItemDelegate, self).__init__()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: Union[QModelIndex, QPersistentModelIndex]):
        model = index.model()
        if index.column() in [1, 2]:
            date_str: str = model.index(index.row(), index.column()).data()
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            text = date.strftime("%a, %d %b %Y")
            option.displayAlignment = Qt.AlignCenter
            self.drawDisplay(painter, option, option.rect, text)
        else:
            super(OffPeriodItemDelegate, self).paint(painter, option, index)
