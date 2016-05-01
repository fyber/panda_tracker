from datetime import datetime, time
from flask import Blueprint, request
from flask_jwt import jwt_required, current_identity
from bson import ObjectId
from dateutil.parser import parse

from ..core import route, mongo

bp = Blueprint('events', __name__, url_prefix='/events')


def prepare_update(tick, prefix=''):
    keys = ('steps', 'distance', 'calories', 'active_time',)
    return {prefix+key: tick.get(key, 0) for key in keys}


@route(bp, '/', methods=('POST',))
@jwt_required()
def store_event():
    ticks = request.get_json()

    for tick in ticks:
        dt_utc = parse(tick['time_completed'])
        id_daily = dt_utc.strftime('%Y%m%d.') + str(current_identity)
        d = datetime.combine(dt_utc.date(), time.min)

        query = {
            '_id': id_daily,
            'metadata': {
                'date': d, 'userid': ObjectId(str(current_identity))
            }
        }
        activity_prefix = 'activities.{}.'.format(tick['activity_kind'])

        inc = {}
        # total among all activities
        inc.update(prepare_update(tick))
        # total for current activity
        inc.update(prepare_update(tick, activity_prefix))

        update = {'$inc': inc}
        mongo.db.event_data.update_one(query, update, upsert=True)

    return ''
