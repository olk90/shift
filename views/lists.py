from PySide6.QtCore import QObject


class MonthList(QObject):
    def __init__(self):
        super(MonthList, self).__init__()
        self.months: list = [
            self.tr("January"),
            self.tr("February"),
            self.tr("March"),
            self.tr("April"),
            self.tr("May"),
            self.tr("June"),
            self.tr("July"),
            self.tr("August"),
            self.tr("September"),
            self.tr("October"),
            self.tr("November"),
            self.tr("December")
        ]


class WeekdayList(QObject):
    def __init__(self):
        super(WeekdayList, self).__init__()
        self.weekdays: list = [
            self.tr("Monday"),
            self.tr("Tuesday"),
            self.tr("Wednesday"),
            self.tr("Thursday"),
            self.tr("Friday"),
            self.tr("Saturday"),
            self.tr("Sunday")
        ]
