import datetime
import calendar

from logic.database import persist_schedule
from logic.model import Schedule


def create_schedule(month: int, year: int):
    print("Set up new schedule for {}/{}".format(month, year))
    start_day = datetime.date(year, month, 1).day
    end_day = calendar.monthrange(year, month)[1]
    day_range = range(start_day, end_day + 1)
    for day in day_range:
        date = datetime.date(year, month, day)
        schedule: Schedule = Schedule(date=date)
        persist_schedule(schedule)
