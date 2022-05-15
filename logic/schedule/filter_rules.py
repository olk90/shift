from datetime import date, timedelta

from logic.database import find_surrounding_schedules
from logic.model import Schedule
from logic.schedule import logger


def reference_value_violated(c_data: dict, day: date) -> bool:
    violated = c_data["reference_value"] <= 0
    if violated:
        logger.info("Reference value of %s (id=%d) violated (day=%s)", c_data["name"], c_data["c_id"], day)
    return violated


def night_shifts_violated(c_data: dict, nights: bool, day: date) -> bool:
    violated = nights and not c_data["night_shifts"]
    if violated:
        logger.info("%s (id=%d) not available for night shifts (day=%s)", c_data["name"], c_data["c_id"], day)
    return violated


def shift_gap_violated(schedule: Schedule, c_data: dict, is_night_shift: bool = False) -> bool:
    c_id: int = c_data["c_id"]
    schedules: dict = find_surrounding_schedules(schedule)
    if is_night_shift:
        shift_type = "night"
        shift_ids = [
            schedules["n_before"],
            schedules["d_today"],
            schedules["d_after"],
            schedules["n_after"]
        ]
    else:
        shift_type = "day"
        shift_ids = [
            schedules["d_before"],
            schedules["n_before"],
            schedules["n_today"],
            schedules["d_after"]
        ]
    violated = c_id in shift_ids
    if violated:
        logger.info(
            "Cannot plan %s (id=%d) for %s shift (shift gap violated) (day=%s)",
            c_data["name"],
            c_data["c_id"],
            shift_type,
            schedule.date
        )
    return violated


def days_off_violated(day: date, c_data: dict, nights: bool) -> bool:
    violated: bool = day in c_data["days_off"]
    if violated:
        logger.info("%s (id=%d) has an off period", c_data["name"], c_data["c_id"])
    if nights:
        next_day = day + timedelta(days=1)
        next_day_violated = next_day in c_data["days_off"]
        if next_day_violated:
            logger.info(
                "%s (id=%d) has an off period starting the next day (day=%s)",
                c_data["name"],
                c_data["c_id"],
                day
            )
        violated |= next_day_violated
    return violated


def free_weekends_violated(day: date, c_data: dict, weekends: list) -> bool:
    if day.weekday() < 4:
        return False
    c_id: int = c_data["c_id"]
    free_weekends = filter(lambda x: c_id not in x[2], weekends)
    violated = len(list(free_weekends)) <= 2
    if violated:
        logger.info(
            "%s (id=%d) has already been planned for enough weekends (day=%s)",
            c_data["name"],
            c_data["c_id"],
            day
        )
    return violated
