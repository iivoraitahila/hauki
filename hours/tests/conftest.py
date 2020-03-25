import pytest
from hours.models import Weekday, DataSource, Target, Period, Opening
from psycopg2.extras import DateRange
from random import randrange
from datetime import timedelta, date, time

def random_date(start, end):
    delta = end - start
    random_date = randrange(delta.days)
    return start + timedelta(days=random_date)

def random_hour(start, end):
    start_hour = start.hour
    end_hour = end.hour
    if end_hour < start_hour:
        end_hour = end_hour + 24
    delta = end_hour - start_hour
    random_time = randrange(delta)
    return time((start_hour+random_time) % 24)

@pytest.fixture
def data_source():
    return DataSource.objects.create(id='ds1')

@pytest.fixture
def target(data_source):
    def _target(origin_id):
        target_id = f'{data_source.id}:{origin_id}'
        return Target(id=target_id, data_source=data_source, origin_id=origin_id,
                      name='Kallion kirjasto')
    return _target

@pytest.fixture(scope='module')
def module_data_source():
    return DataSource.objects.create(id='sds1')

@pytest.fixture(scope='module')
def module_target(module_data_source):
    def _target(origin_id):
        target_id = f'{module_data_source.id}:{origin_id}'
        return Target(id=target_id, data_source=module_data_source, origin_id=origin_id,
                      name='Kallion kirjasto')
    return _target

@pytest.fixture(scope='module')
def targets(module_target):
    values = []
    for id in range(1,1000):
        values.append(module_target(id))
    return Target.objects.bulk_create(values)

@pytest.fixture(scope='module')
def long_period(module_data_source):
    def _long_period(module_target, origin_id):
        period_id = f'{module_data_source.id}:{origin_id}'
        start = random_date(date(2020,1,1), date(2020,12,31))
        end = random_date(date(2022,1,1), date(2022,12,31))
        return Period(id=period_id, data_source=module_data_source, origin_id=origin_id,
                      target=module_target, period=DateRange(lower=start, upper=end))
    return _long_period

@pytest.fixture(scope='module')
def medium_period(module_data_source):
    def _medium_period(module_target, origin_id):
        period_id = f'{module_data_source.id}:{origin_id}'
        start = random_date(date(2021,1,1), date(2021,5,31))
        end = random_date(date(2021,9,1), date(2021,12,31))
        return Period(id=period_id, data_source=module_data_source, origin_id=origin_id,
                      target=module_target, period=DateRange(lower=start, upper=end))
    return _medium_period

@pytest.fixture(scope='module')
def short_period(module_data_source):
    def _short_period(module_target, origin_id):
        period_id = f'{module_data_source.id}:{origin_id}'
        start = random_date(date(2021,7,10), date(2021,7,15))
        end = random_date(date(2021,7,16), date(2021,7,20))
        return Period(id=period_id, data_source=module_data_source, origin_id=origin_id,
                      target=module_target, period=DateRange(lower=start, upper=end))
    return _short_period

@pytest.fixture(scope='module')
def periods(targets, long_period, medium_period, short_period):
    values = []
    for target in targets:
        # each target should have long and medium range and some exceptions
        values.append(long_period(target, target.origin_id))
        values.append(medium_period(target, f'{target.origin_id}-medium'))
        values.append(short_period(target, f'{target.origin_id}-short1'))
        values.append(short_period(target, f'{target.origin_id}-short2'))
    return Period.objects.bulk_create(values)

@pytest.fixture(scope='module')
def first_opening():
    def _first_opening(period, weekday):
        opens = random_hour(time(7), time(8))
        closes = random_hour(time(10), time(13))
        return Opening(weekday=weekday, period=period, opens=opens, closes=closes)
    return _first_opening

@pytest.fixture(scope='module')
def second_opening():
    def _second_opening(period, weekday):
        opens = random_hour(time(14), time(16))
        closes = random_hour(time(18), time(20))
        return Opening(weekday=weekday, period=period, opens=opens, closes=closes)
    return _second_opening

@pytest.fixture(scope='module')
def third_opening():
    def _third_opening(period, weekday):
        opens = random_hour(time(21), time(23))
        closes = random_hour(time(1), time(4))
        return Opening(weekday=weekday, period=period, opens=opens, closes=closes)
    return _third_opening

@pytest.fixture(scope='module')
def openings(periods, first_opening, second_opening, third_opening):
    values = []
    for index, period in enumerate(periods):
        for weekday in Weekday.choices:
            values.append(first_opening(period, weekday[0]))
        if index % 10 == 0:
            values.append(second_opening(period, weekday[0]))
        if index % 100 == 0:
            values.append(third_opening(period, weekday[0]))
    return Opening.objects.bulk_create(values)