import pytz
from datetime import datetime, timedelta
from django.utils import timezone


def time_in_minutes(time):
    time_unit = time[-1]
    time = int(time[:-1])

    if not time_unit == 'm':
        if time_unit == 'h':
            time = time * 60
        elif time_unit == 'd':
            time = time * 24 * 60
        else:
            print('ERROR')

    return time


def save_queue(queue, status, dividend):
    timezone.now()

    time = time_in_minutes(queue.time)

    time = round(time / dividend)
    if time <= 2:
        time = 2

    # time + 60 - Reason: time shift
    next_time = datetime.now(tz=pytz.UTC) + timedelta(minutes=time + 60)

    if time < 60:
        # unit = minutes
        time_unit = 'm'
    elif (time >= 60) and (time < 1440):
        # unit = hours
        time = round(time / 60)
        time_unit = 'h'
    else:
        # unit = days
        time = round((time / 60) / 24)
        time_unit = 'd'

    print(f'Next time: {next_time}')
    print(f'Time: {time}{time_unit}')

    queue.learn_status = status
    queue.next_time = next_time
    queue.time = str(time) + time_unit
    queue.save()


def get_next_times(time):
    current_time = time_in_minutes(time)
    times = []

    for time in [3, 0.5, 0.25]:
        time = round(current_time / time)

        if time <= 2:
            time = 2

        if time < 60:
            time_unit = 'm'
        elif (time >= 60) and (time < 1440):
            time = round(time / 60)
            time_unit = 'h'
        else:
            time = round((time / 60) / 24)
            time_unit = 'd'

        times.append(f'{time}{time_unit}')

    times = {
        'again': times[0],
        'okay': times[1],
        'easy': times[2]
    }

    return times