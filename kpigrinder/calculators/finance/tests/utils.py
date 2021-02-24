import pytz
from datetime import datetime, timedelta
from faker import Faker


faker = Faker()


def random_datetime_for_date(dt: datetime, timezone=None):
    dt_from = datetime(dt.year, dt.month, dt.day)
    dt_to = dt_from + timedelta(minutes=24*60-1)
    _dt = faker.date_time_between(dt_from, dt_to)

    if timezone:
        _dt = pytz.timezone(timezone).localize(_dt)

    return _dt
