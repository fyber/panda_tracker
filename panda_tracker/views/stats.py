from flask import Blueprint
from flask_jwt import jwt_required, current_identity
from webargs import fields, missing
from webargs.flaskparser import use_kwargs
from datetime import datetime, date, time, timedelta
from marshmallow import ValidationError

from bson import ObjectId

from ..core import route, mongo

bp = Blueprint('stats', __name__, url_prefix='/stats')

stat_args = {
    'date_from': fields.Date(required=False, load_from='from'),
    'date_to': fields.Date(required=False, load_from='to'),

    'last_n_days': fields.Int(required=False),
}


def validate(args):
    if not args.get('date_from') and not args.get('last_n_days') is not None:
        raise ValidationError(
            'Either date_from or last_n_days fields are required.')


@route(bp, '/')
@jwt_required()
@use_kwargs(stat_args, locations=('query',), validate=validate)
def get_stats(date_from, date_to, last_n_days):
    """Returns statistics over specified period.
    That period can be defined in two ways:
        1. In the form of 'Last N days'
        2. More usual form with start date and end date. End date defaults to
        today.
    """
    if last_n_days is not missing:
        date_from = date.today() - timedelta(days=last_n_days)

    if date_to is missing:
        date_to = date.today()

    # convert dates to datetimes
    date_from = datetime.combine(date_from, time.min)
    date_to = datetime.combine(date_to, time.min)

    stats = mongo.db.event_data.find(
        {
            'metadata.userid': ObjectId(str(current_identity)),
            'metadata.date': {'$gte': date_from, '$lte': date_to},
        },
        # exclude meta fields from the output
        projection={'metadata.userid': 0, '_id': 0},
        sort=[('metadata.date', 1)]
    )

    return list(stats)
