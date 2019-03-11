# coding:utf-8
import time
import datetime
from wuaiwow import app


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    _format = '%Y-%m-%d' if not fmt else fmt
    if isinstance(date, datetime.datetime):
        return date.strftime(_format)
    else:
        return 'Need datetime type provide %s' % type(date)


@app.template_filter('timespan')
def _jinja2_filter_timespan(date):
    now = datetime.datetime.fromtimestamp(time.time())
    if isinstance(date, datetime.datetime):
        days = (now-date).days
        return u"今天" if days == 0 else u"昨天" if days == 1 else u"前天" if days == 2 else str(days)+u" 天前"
    else:
        return u'时间未知'


@app.template_filter('struct')
def _jinja2_filter_struct(msg):
    if msg.is_read:
        return "openenvelope"
    else:
        return "closenvelope"


@app.template_filter('isread')
def _jinja2_filter_isread(msg):
    if msg.is_read:
        return "glyphicon glyphicon-eye-open"
    else:
        return "glyphicon glyphicon-eye-close"


@app.template_filter('summary')
def _jinja2_filter_summary(content):
    content_len = len(content)
    summary_len = 20 if content_len < 20 else content_len

    return content[:summary_len]