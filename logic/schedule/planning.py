import datetime

from sqlalchemy import create_engine as ce
from sqlalchemy.orm import sessionmaker as sm

import logic.schedule.filter_rules as fr
from logic.database import find_candidates, reset_scores, find_days_off, count_shifts
from logic.model import Schedule
from logic.queries import schedule_id_query
from views.base_functions import get_day_range

db = ce("sqlite:///shift.db")
session = sm(bind=db)


def create_schedule(month: int, year: int):
    print("Set up new schedule for {}/{}".format(month, year))
    reset_scores()
    day_range = get_day_range(month, year)

    s = session()
    for day in day_range:
        date = datetime.date(year, month, day)
        schedule: Schedule = Schedule(date=date)
        s.add(schedule)
    s.commit()


def fill_schedule(month: int, year: int):
    print("Fill open shifts for {}/{}".format(month, year))
    day_range = get_day_range(month, year)

    candidates: list = find_candidates()
    c_dict = init_candidate_dict(month, year, candidates)
    for day in day_range:
        s = session()
        date_of_day = datetime.date(year, month, day)
        schedule: Schedule = s.query(Schedule).filter_by(date=date_of_day).first()
        if schedule.day_id is None:
            c_id = find_candidate(c_dict, candidates, schedule, date_of_day)
            schedule.day_id = c_id

        if schedule.night_id is None:
            c_id = find_candidate(c_dict, candidates, schedule, date_of_day, True)
            schedule.night_id = c_id
        c_dict = sort_candidate_dict(c_dict)
        s.commit()


def find_candidate(c_dict: dict, candidates: list, schedule: Schedule, date_of_day: datetime.date,
                   nights: bool = False) -> int | None:
    for c in candidates:
        c_data: dict = c_dict[c.id]
        if fr.reference_value_violated(c_data) \
                or fr.day_shift_gap_violated(schedule, c_data) \
                or fr.night_shift_gap_violated(schedule, c_data) \
                or fr.days_off_violated(date_of_day, c_data, nights) \
                or fr.night_shifts_violated(c_data, nights):
            continue
        else:
            c_data["reference_value"] -= 1
            return c.id
    return None


def init_candidate_dict(month: int, year: int, candidates: list) -> dict:
    c_dict = {}
    for c in candidates:
        c_id = c.id
        shift_count = count_shifts(month, year, c_id)
        c_dict[c_id] = {
            "c_id": c_id,
            "reference_value": c.reference_value - shift_count,
            "night_shifts": c.night_shifts,
            "days_off": find_days_off(month, year, c_id),
            "weekends": {
                # TODO track all weekends,
                # TODO mark each weekend with a shift covered by this person
                # TODO keep 2 weekends free during planning -> filter rule!
            }
        }
    return c_dict


def sort_candidate_dict(c_dict) -> dict:
    items = c_dict.items()
    sorted_items = sorted(items, key=lambda x: x[1]["reference_value"], reverse=True)
    print(sorted_items)
    return dict(sorted_items)


def toggle_schedule_state(year: int, month: int, activate: bool):
    s = session()
    query = schedule_id_query(year, month)
    s_ids = s.execute(query)
    for sid in s_ids:
        schedule: Schedule = s.query(Schedule).filter_by(id=sid[0]).first()
        schedule.activated = activate
    s.commit()


def clear_schedule(year: int, month: int):
    s = session()
    query = schedule_id_query(year, month)
    s_ids = s.execute(query)
    for sid in s_ids:
        schedule: Schedule = s.query(Schedule).filter_by(id=sid[0]).first()
        s.delete(schedule)
    s.commit()
