import datetime as dt

import logic.schedule.filter_rules as fr
from logic.config import properties
from logic.database import find_candidates, find_days_off, count_shifts
from logic.model import Schedule
from logic.queries import schedule_id_query
from logic.schedule import logger
from views.base_functions import get_day_range


def create_schedule(month: int, year: int):
    logger.info("Set up new schedule for %d/%d", month, year)
    day_range = get_day_range(month, year)

    s = properties.open_session()
    for day in day_range:
        date = dt.date(year, month, day)
        schedule: Schedule = Schedule(date=date)
        s.add(schedule)
    s.commit()


def fill_schedule(month: int, year: int):
    logger.info("Fill open shifts of %d/%d", month, year)
    day_range = get_day_range(month, year)

    candidates: list = find_candidates()
    c_dict = init_candidate_dict(month, year, candidates)
    weekends = calculate_weekends(year, month)
    for day in day_range:
        s = properties.open_session()
        date_of_day = dt.date(year, month, day)
        schedule: Schedule = s.query(Schedule).filter_by(date=date_of_day).first()
        if schedule.day_id is None:
            c_id = find_candidate(c_dict, candidates, weekends, schedule, date_of_day)
            schedule.day_id = c_id

        if schedule.night_id is None:
            c_id = find_candidate(c_dict, candidates, weekends, schedule, date_of_day, True)
            schedule.night_id = c_id
        c_dict = sort_candidate_dict(c_dict)
        update_weekends(schedule, weekends)
        s.commit()


def find_candidate(c_dict: dict, candidates: list, weekends: list, schedule: Schedule, date_of_day: dt.date,
                   nights: bool = False) -> int | None:
    for c in candidates:
        c_data: dict = c_dict[c.id]
        if fr.reference_value_violated(c_data, date_of_day) \
                or fr.shift_gap_violated(schedule, c_data, nights) \
                or fr.days_off_violated(date_of_day, c_data, nights) \
                or fr.night_shifts_violated(c_data, nights, date_of_day) \
                or fr.free_weekends_violated(date_of_day, c_data, weekends):
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
            "name": c.get_full_name(),
            "score": c.score * -1,  # must be inverted to sort the dict correctly
            "reference_value": c.reference_value - shift_count,
            "night_shifts": c.night_shifts,
            "days_off": find_days_off(month, year, c_id),
        }
    return c_dict


def calculate_weekends(year: int, month: int) -> list | None:
    if month < 1:
        return None
    weekends = []  # element is a 3-tuple: (start, end, {<set of employee IDs>})
    day_range = get_day_range(month, year)
    last_day = day_range[-1]
    for d in day_range:
        day = dt.date(year, month, d)
        weekday = day.weekday()
        if weekday > 3:
            if d == 1 and weekday == 6:  # consider weekends starting in the last month
                start = day - dt.timedelta(days=2)
                end = day
                weekends.append((start, end, set()))
            if d == last_day and weekday == 4:  # consider weekends ending in the next month
                start = day
                end = day + dt.timedelta(days=2)
                weekends.append((start, end, set()))
                break
            if weekday == 5:  # "normal" weekends in the current month (weekday == 5)
                start = day - dt.timedelta(days=1)
                end = day + dt.timedelta(days=1)
                weekends.append((start, end, set()))

    return weekends


def sort_candidate_dict(c_dict) -> dict:
    items = c_dict.items()
    sorted_items = sorted(items, key=lambda x: (x[1]["reference_value"], x[1]["score"]), reverse=True)
    return dict(sorted_items)


def update_weekends(schedule: Schedule, weekends: list):
    day = schedule.date
    if day.weekday() > 3:
        for we in weekends:
            if we[0] <= day <= we[1]:
                we[2].add(schedule.day_id)
                we[2].add(schedule.night_id)


def toggle_schedule_state(year: int, month: int, activate: bool):
    s = properties.open_session()
    query = schedule_id_query(year, month)
    s_ids = s.execute(query)
    for sid in s_ids:
        schedule: Schedule = s.query(Schedule).filter_by(id=sid[0]).first()
        schedule.activated = activate
    s.commit()


def clear_schedule(year: int, month: int):
    s = properties.open_session()
    query = schedule_id_query(year, month)
    s_ids = s.execute(query)
    for sid in s_ids:
        schedule: Schedule = s.query(Schedule).filter_by(id=sid[0]).first()
        s.delete(schedule)
    s.commit()
