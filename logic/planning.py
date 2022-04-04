import calendar
import datetime

from sqlalchemy import create_engine as ce
from sqlalchemy.orm import sessionmaker as sm

from logic.database import get_day_shift_candidates, get_night_shift_candidates, get_schedule_by_date, reset_scores
from logic.model import Schedule, Employee
from logic.queries import schedule_id_query

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
        d_replacement_index = 1
        n_replacement_index = 1
        d_candidate_id: int = d_candidates[0]
        n_candidate_id: int = n_candidates[0]
        if d_candidate_id == n_candidate_id:
            n_candidate_id = n_candidates[n_replacement_index]
            n_replacement_index += 1

        last_Schedule: Schedule = get_schedule_by_date(day_before)
        if last_Schedule:
            day_id: int = last_Schedule.day_id
            night_id: int = last_Schedule.night_id
            if d_candidate_id in [day_id, night_id]:
                d_candidate_id = d_candidates[d_replacement_index]
                d_replacement_index += 1
            if n_candidate_id == night_id:
                n_candidate_id = n_candidates[n_replacement_index]
                n_replacement_index += 1

        session = sm(bind=db)
        s = session()
        d_candidate: Employee = s.query(Employee).filter_by(id=d_candidate_id).first()
        n_candidate: Employee = s.query(Employee).filter_by(id=n_candidate_id).first()
        if date.weekday() > 3:
            d_candidate.score += 10
            n_candidate.score += 10
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


def toggle_schedule_state(year: int, month: int, activate: bool):
    session = sm(bind=db)
    s = session()
    query = schedule_id_query(year, month)
    s_ids = s.execute(query)
    for sid in s_ids:
        schedule: Schedule = s.query(Schedule).filter_by(id=sid[0]).first()
        schedule.activated = activate
    s.commit()
