import calendar
import datetime

from sqlalchemy import create_engine as ce
from sqlalchemy.orm import sessionmaker as sm

from logic.database import get_day_shift_candidates, get_night_shift_candidates, get_schedule_by_date, reset_scores
from logic.model import Schedule, Employee

db = ce("sqlite:///shift.db")


def create_schedule(month: int, year: int):
    print("Set up new schedule for {}/{}".format(month, year))
    reset_scores()
    start_day = datetime.date(year, month, 1).day
    end_day = calendar.monthrange(year, month)[1]
    day_range = range(start_day, end_day + 1)

    for day in day_range:
        d_candidates: list = get_day_shift_candidates()
        n_candidates: list = get_night_shift_candidates()
        date = datetime.date(year, month, day)
        day_before = date - datetime.timedelta(days=1)
        d_candidate: Employee = d_candidates[0]
        n_candidate: Employee = n_candidates[0]
        if d_candidate.id == n_candidate.id:
            n_candidate = n_candidates[1]

        schedule_before: Schedule = get_schedule_by_date(day_before)
        if schedule_before:
            night_id = schedule_before.night_id
            if d_candidate.id == night_id:
                d_candidate: Employee = d_candidates[1]

        session = sm(bind=db)
        s = session()
        d_candidate = s.query(Employee).filter_by(id=d_candidate.id).first()
        n_candidate = s.query(Employee).filter_by(id=n_candidate.id).first()
        if date.weekday() > 4:
            d_candidate.score += 2
            n_candidate.score += 2
        else:
            d_candidate.score += 1
            n_candidate.score += 1

        schedule: Schedule = Schedule(date=date, day_id=d_candidate.id, night_id=n_candidate.id)
        s.add(schedule)
        s.commit()


def get_next_candidate_index(index: int, candidate_list: list) -> int:
    length = len(candidate_list)
    index = index + 1
    if length == index:
        index = 0
    return index
