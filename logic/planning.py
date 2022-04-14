import calendar
import datetime

from sqlalchemy import create_engine as ce
from sqlalchemy.orm import sessionmaker as sm

from logic.database import find_day_shift_candidate_ids, find_night_shift_candidate_ids, find_schedule_by_date, \
    reset_scores
from logic.model import Schedule, Employee
from logic.queries import schedule_id_query
from views.helpers import get_day_range

db = ce("sqlite:///shift.db")


def create_schedule(month: int, year: int):
    print("Set up new schedule for {}/{}".format(month, year))
    reset_scores()
    day_range = get_day_range(month, year)

    session = sm(bind=db)
    s = session()
    for day in day_range:
        date = datetime.date(year, month, day)
        schedule: Schedule = Schedule(date=date)
        s.add(schedule)
    s.commit()


def fill_schedule(month: int, year: int):
    print("Fill open shifts for {}/{}".format(month, year))
    start_day = datetime.date(year, month, 1).day
    end_day = calendar.monthrange(year, month)[1]
    day_range = range(start_day, end_day + 1)

    for day in day_range:
        date_of_day = datetime.date(year, month, day)
        d_candidates: list = find_day_shift_candidate_ids(date_of_day)
        n_candidates: list = find_night_shift_candidate_ids(date_of_day)
        date = datetime.date(year, month, day)
        day_before = date - datetime.timedelta(days=1)
        day_after = date + datetime.timedelta(days=1)
        d_replacement_index = 1
        n_replacement_index = 1
        d_candidate_id: int = d_candidates[0]
        n_candidate_id: int = n_candidates[0]
        if d_candidate_id == n_candidate_id:
            n_candidate_id = n_candidates[n_replacement_index]
            n_replacement_index += 1

        last_schedule: Schedule = find_schedule_by_date(day_before)
        if last_schedule:
            day_id: int = last_schedule.day_id
            night_id: int = last_schedule.night_id
            if d_candidate_id in [day_id, night_id]:
                d_candidate_id = d_candidates[d_replacement_index]
                d_replacement_index += 1
            if n_candidate_id == night_id:
                n_candidate_id = n_candidates[n_replacement_index]
                n_replacement_index += 1

        next_schedule: Schedule = find_schedule_by_date(day_after)
        if next_schedule:
            day_id = next_schedule.day_id
            night_id = next_schedule.night_id
            if n_candidate_id in [day_id, night_id]:
                n_candidate_id = n_candidates[n_replacement_index]
                n_replacement_index += 1
            if d_candidate_id == day_id:
                d_candidate_id = d_candidates[d_replacement_index]
                d_replacement_index += 1

        score_offset: int = 10 if date.weekday() > 3 else 1

        session = sm(bind=db)
        s = session()
        schedule: Schedule = s.query(Schedule).filter_by(date=date_of_day).first()
        if schedule.day_id is None:
            d_candidate: Employee = s.query(Employee).filter_by(id=d_candidate_id).first()
            d_candidate.score += score_offset
            schedule.day_id = d_candidate_id

        if schedule.night_id is None:
            n_candidate: Employee = s.query(Employee).filter_by(id=n_candidate_id).first()
            n_candidate.score += score_offset
            schedule.night_id = n_candidate_id
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
