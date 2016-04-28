# coding: utf-8
from __future__ import unicode_literals, absolute_import, division


from panda_tracker.factory import create_app

application = create_app()


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('127.0.0.1', 6000, application, use_reloader=True)
