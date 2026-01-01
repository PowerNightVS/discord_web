import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app, INVITE_LINK, SUPPORT_LINK, active_streams

with app.test_request_context('/'):
    print('rendering index...')
    tpl = app.jinja_env.get_template('index.html')
    rendered = tpl.render(joined_servers=[], active_streams=active_streams, invite_link=INVITE_LINK, support_link=SUPPORT_LINK)
    print('index length', len(rendered))

    print('rendering dashboard...')
    tpl = app.jinja_env.get_template('dashboard.html')
    rendered = tpl.render(user=None, commands=[], bot_online=True, bot_wake_up_time='08:00 AM', invite_link=INVITE_LINK, support_link=SUPPORT_LINK)
    print('dashboard length', len(rendered))

    print('rendering stream...')
    tpl = app.jinja_env.get_template('stream.html')
    rendered = tpl.render(streams=[])
    print('stream length', len(rendered))

    print('rendering leaderboard...')
    tpl = app.jinja_env.get_template('leaderboard.html')
    rendered = tpl.render(users=[])
    print('leaderboard length', len(rendered))

print('OK')