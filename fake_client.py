from __future__ import print_function

import random
import json
import requests
from time import time as timer
from argparse import ArgumentParser
from datetime import datetime, timedelta, date, time
from six.moves.urllib.parse import urljoin


# pseudoreal numbers
CALORIES_WALKING_PER_SECOND = 0.115
DISTANCE_WALKING_PER_SECOND = 1.77
STEPS_WALKING_PER_SECOND = 1.66

CALORIES_RUNNING_PER_SECOND = 0.23
DISTANCE_RUNNING_PER_SECOND = 3.54

# how many seconds to include in each tick
SECONDS_PER_TICK = 30


def random_date_from_last_year():
    start_date = (date.today() - timedelta(days=365)).toordinal()
    end_date = date.today().toordinal()
    return date.fromordinal(random.randint(start_date, end_date))


def generate_fake_walk_data_for_one_day(date):
    activity_start = datetime.combine(date, time(hour=8))  # start at 8:00 AM
    activity_end = activity_start + timedelta(hours=random.randint(1, 2))
    # send one tick every 30 seconds
    num_ticks = int(
        (activity_end - activity_start).total_seconds() // SECONDS_PER_TICK)

    tick_template = {
        'activity_kind': 'walk',
        'calories': int(CALORIES_WALKING_PER_SECOND * SECONDS_PER_TICK),
        'distance': int(DISTANCE_WALKING_PER_SECOND * SECONDS_PER_TICK),
        'steps': int(STEPS_WALKING_PER_SECOND * SECONDS_PER_TICK),
        'active_time': SECONDS_PER_TICK,
    }

    walk_data = []
    for tick in range(num_ticks):
        t = dict(tick_template)
        t['time_completed'] = (
            activity_start + timedelta(seconds=SECONDS_PER_TICK) * (tick + 1))

        walk_data.append(t)

    return walk_data


def generate_fake_run_data_for_one_day(date):
    activity_start = datetime.combine(date, time(hour=10))  # start at 10:00 AM
    activity_end = activity_start + timedelta(minutes=random.randint(10, 60))
    # send one tick every 30 seconds
    num_ticks = int(
        (activity_end - activity_start).total_seconds() // SECONDS_PER_TICK)

    tick_template = {
        'activity_kind': 'run',
        'calories': int(CALORIES_WALKING_PER_SECOND * SECONDS_PER_TICK),
        'distance': int(DISTANCE_WALKING_PER_SECOND * SECONDS_PER_TICK),
        'active_time': SECONDS_PER_TICK,
    }

    walk_data = []
    for tick in range(num_ticks):
        t = dict(tick_template)
        t['time_completed'] = (
            activity_start + timedelta(seconds=SECONDS_PER_TICK) * (tick + 1))

        walk_data.append(t)

    return walk_data


def generate_fake_data_for_one_day(date):
    data = []
    data.extend(generate_fake_walk_data_for_one_day(date))
    data.extend(generate_fake_run_data_for_one_day(date))
    return data


def create_fake_data():
    """Creates fake activity data for one user."""
    ticks = []

    days = random.randint(5, 100)
    start_date = random_date_from_last_year()

    for day in range(days):
        current_date = start_date + timedelta(days=day)
        ticks.extend(generate_fake_data_for_one_day(current_date))

    return ticks


def default(obj):
    """Helper function to dump datetimes to json."""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()


class TrackerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers[b'Authorization'] = b'JWT ' + self.token.encode('latin1')
        return r


def main():
    parser = ArgumentParser()

    parser.add_argument(
        '-s', '--host', default='http://127.0.0.1', help='tracker host')
    parser.add_argument(
        '-p', '--port', default=6000, help='tracker host port', type=int)
    parser.add_argument(
        '-n', '--users', default=1, help='how many users to create', type=int)

    options = parser.parse_args()

    urlbase = '{}:{}/'.format(options.host, options.port)

    session = requests.Session()

    for user in range(options.users):
        # username is just a random number
        new_username = str(random.randint(1e6, 1e7))
        # all new users have one password for simple debug
        new_password = '123'

        resp = session.post(urljoin(urlbase, 'auth/signup'),
                            json={'username': new_username,
                                  'password': new_password})

        resp.raise_for_status()

        token = resp.json()['access_token']
        session.auth = TrackerAuth(token)

        fake_data = create_fake_data()

        ts = timer()
        resp = session.post(
            urljoin(urlbase, 'events'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(fake_data, default=default))
        delta = timer() - ts

        resp.raise_for_status()

        print('{} events in {:.2f}s @ {:.2f} rps'
              .format(len(fake_data), delta, len(fake_data) / delta))


if __name__ == '__main__':
    main()
