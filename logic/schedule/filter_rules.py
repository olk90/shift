from datetime import date, timedelta

from logic.database import find_surrounding_schedules
from logic.model import Schedule


def reference_value_violated(c_data: dict) -> bool:
    return c_data["reference_value"] <= 0


def night_shifts_violated(c_data: dict, nights: bool) -> bool:
    return nights and not c_data["night_shifts"]


def day_shift_gap_violated(schedule: Schedule, c_data: dict) -> bool:
    c_id: int = c_data["c_id"]
    schedules: dict = find_surrounding_schedules(schedule)
    shift_ids = [
        schedules["d_before"],
        schedules["n_before"],
        schedules["d_today"],
        schedules["n_today"],
        schedules["d_after"]
    ]
    return c_id in shift_ids


def night_shift_gap_violated(schedule: Schedule, c_data: dict) -> bool:
    c_id: int = c_data["c_id"]
    schedules: dict = find_surrounding_schedules(schedule)
    shift_ids = [
        schedules["n_before"],
        schedules["d_today"],
        schedules["n_today"],
        schedules["d_after"],
        schedules["n_after"]
    ]
    return c_id in shift_ids


def days_off_violated(day: date, c_data: dict, nights: bool) -> bool:
    violated: bool = day in c_data["days_off"]
    if nights:
        next_day = day + timedelta(days=1)
        violated |= next_day in c_data["days_off"]
    return violated


def free_weekends_violated(day: date, c_data: dict) -> bool:
    if day.weekday() < 4:
        return False

    return False
