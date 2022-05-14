import datetime
from typing import Union

from PySide6.QtCore import QDate, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QPainter
from PySide6.QtSql import QSqlTableModel
from PySide6.QtWidgets import QWidget, QComboBox, QHBoxLayout, QDialogButtonBox, QSpinBox, QPushButton, QTableView, \
    QMessageBox, QStyleOptionViewItem
from sqlalchemy import create_engine as ce
from sqlalchemy.orm import sessionmaker as sm

from logic.config import properties
from logic.database import configure_query_model, persist_item, find_employee_by_id, \
    find_off_period_by_id, delete_item, update_off_period
from logic.table_models import OffPeriodModel
from logic.model import OffPeriod, Employee
from logic.queries import employee_fullname_query
from views.confirmationDialogs import ConfirmDeletionDialog
from views.base_classes import EditorDialog, EditorWidget, TableDialog, CenteredItemDelegate
from views.base_functions import configure_month_box, configure_weekday_box, configure_year_box, get_day_range


class AddOffPeriodDialog(EditorDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent, ui_file_name="ui/offPeriodAddDialog.ui")

        self.employee_box: QComboBox = self.widget.employeeBox  # noqa
        query: str = employee_fullname_query()
        configure_query_model(self.employee_box, query)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa
        self.startEdit = self.widget.startEdit  # noqa
        self.endEdit = self.widget.endEdit  # noqa

        self.configure_widgets()

    def configure_widgets(self):
        super(AddOffPeriodDialog, self).configure_widgets()
        self.endEdit.selectionChanged.connect(self.update_start)
        self.startEdit.selectionChanged.connect(self.update_end)

    def update_start(self):
        end_date: QDate = self.endEdit.selectedDate()
        self.startEdit.setMaximumDate(end_date)

    def update_end(self):
        start_date: QDate = self.startEdit.selectedDate()
        self.endEdit.setMinimumDate(start_date)

    def commit(self):
        model: QSqlTableModel = self.employee_box.model()
        index: int = self.employee_box.currentIndex()
        e_id = model.index(index, 1).data()
        start: QDate = self.widget.startEdit.selectedDate()  # noqa
        start_date = datetime.date(start.year(), start.month(), start.day())
        end: QDate = self.widget.endEdit.selectedDate()  # noqa
        end_date = datetime.date(end.year(), end.month(), end.day())
        off_period = OffPeriod(e_id=e_id, start=start_date, end=end_date)
        persist_item(off_period)
        self.parent.reload_table_contents(model=OffPeriodModel())
        self.close()

    def clear_fields(self):
        query: str = employee_fullname_query()
        self.employee_box.model().setQuery(query)
        self.employee_box.setCurrentIndex(0)  # noqa
        self.widget.startEdit.setSelectedDate(QDate.currentDate())  # noqa
        self.widget.endEdit.setSelectedDate(QDate.currentDate())  # noqa


class AddRepeatingOffPeriodDialog(EditorDialog):

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent, ui_file_name="ui/repeatingOffPeriodAddDialog.ui")

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.buttonBox: QDialogButtonBox = self.widget.buttonBox  # noqa

        self.employee_box: QComboBox = self.widget.employeeBox  # noqa
        query: str = employee_fullname_query()
        configure_query_model(self.employee_box, query)

        self.month_box: QComboBox = self.widget.monthBox  # noqa
        self.year_box: QSpinBox = self.widget.yearBox  # noqa
        self.weekday_box: QComboBox = self.widget.weekdayBox  # noqa

        self.configure_widgets()

    def configure_widgets(self):
        super(AddRepeatingOffPeriodDialog, self).configure_widgets()
        configure_month_box(self.month_box)
        configure_year_box(self.year_box)
        configure_weekday_box(self.weekday_box)

    def clear_fields(self):
        query: str = employee_fullname_query()
        self.employee_box.model().setQuery(query)
        self.employee_box.setCurrentIndex(0)  # noqa

    def commit(self):
        model: QSqlTableModel = self.employee_box.model()
        index: int = self.employee_box.currentIndex()
        e_id = model.index(index, 1).data()
        month: int = self.month_box.currentIndex()
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
        self.parent.reload_table_contents(model=OffPeriodModel())


class OffPeriodEditorWidget(EditorWidget):

    def __init__(self, item_id=None):
        super().__init__(ui_file_name="ui/offPeriodEditor.ui", item_id=item_id)

        self.name_label = self.widget.name_label  # noqa
        self.startEdit = self.widget.startEdit  # noqa
        self.endEdit = self.widget.endEdit  # noqa
        self.configure_widgets()

    def configure_widgets(self):
        self.endEdit.selectionChanged.connect(self.update_start)
        self.startEdit.selectionChanged.connect(self.update_end)

    def update_start(self):
        end_date: QDate = self.endEdit.selectedDate()
        self.startEdit.setMaximumDate(end_date)

    def update_end(self):
        start_date: QDate = self.startEdit.selectedDate()
        self.endEdit.setMinimumDate(start_date)

    def fill_fields(self, period: OffPeriod):
        self.item_id = period.id
        employee: Employee = find_employee_by_id(period.e_id)
        self.name_label.setText(employee.get_full_name())

        start = period.start
        q_start = QDate(start.year, start.month, start.day)
        self.startEdit.setSelectedDate(q_start)

        end = period.end
        q_end = QDate(end.year, end.month, end.day)
        self.endEdit.setSelectedDate(q_end)

    def get_values(self) -> dict:
        return {
            "item_id": self.item_id,
            "start": self.startEdit.selectedDate(),
            "end": self.endEdit.selectedDate()
        }


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
        self.configure_search()

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
