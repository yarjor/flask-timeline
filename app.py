#!usr/bin/python

from flask import (Flask, render_template, request,
    g, url_for, jsonify)
from schema import Event, Session, db_create
from sqlalchemy import desc
from consts import *
import os
from datetime import datetime
from string import digits
from flask_socketio import SocketIO
from copy import deepcopy
import json

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, DB_NAME),
    SECRET_KEY=APP_KEY,
    TICK=DEFAULT_TICK,
    ))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.debug = True
socketio = SocketIO(app) # BLACK MAGIC HERE

user_config = deepcopy(dict(EMPTY_CONFIG))


def connect_db():
    '''
    Returns a DB connection session
    '''
    return Session()


@app.cli.command('initdb')
def initdb_command():
    '''
    Initializes the database.
    '''
    db_create()
    print('Initialized the database')


def get_db():
    '''
    Opens a new database connection if there is none yet
    for the current application context.
    '''
    if 'sqlite_db' not in g:
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    '''
    Closes the database again at the end of the request.
    '''
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
    # if error:
        # return render_template('error.html', error=str(error))

##################################

@app.route("/")
def main():
    '''Displays the main interfaces'''
    return render_template('index.html')


@app.route('/getAllEvents')
def get_all_events():
    '''
    Returns a JSONified list of all the events matching the current
    user config, in dict form.
    '''
    db = get_db()
    event_list = apply_filters(db.query(Event).order_by(Event.time)).all()
    tick = user_config['tick']
    element_list = []
    if event_list:
        for prev, cur in zip([event_list[0]] + event_list, event_list + [None]):
            if cur:
                current = cur.to_dict()
                space = round((cur.time - prev.time).total_seconds() / tick.total_seconds(), 4)
                current['Space'] = space
                element_list.append(current)

    return jsonify(element_list)


@app.route('/getTags/<int:id>')
def get_tags(id: int):
    '''
    Returns all the tags used in the event with the given ID
    '''
    db = get_db()
    event = db.get(Event, id)
    return jsonify(event.tags if event else "")


@app.route('/updateTags/<int:id>', methods=['POST'])
def update_tags(id: int):
    '''
    Updates the list of tags of the event with the given ID
    '''
    db = get_db()
    event = db.get(Event, id)
    if not event:
        return jsonify({'Status' : f'Event ID {id} not found'})
    event.tags = request.form['tags']
    with open(ALL_TAGS, 'rb') as f:
        all_tags = json.load(f)
    all_tags.extend(event.tags.split(','))
    with open(ALL_TAGS, 'w') as f:
        json.dump(list(set(all_tags)), f)
    db.commit()
    return jsonify({'Status' : 'OKitten'})


@app.route('/updateConfig', methods=['POST'])
def update_config():
    '''
    Gets the user config form (basic side bar) and updates the user_config
    accordingly.
    '''
    new_config = {}
    fget = request.form.get
    start_date = fget('startDate')
    start_date = datetime.strptime(start_date, TIME_FORMAT) if start_date else datetime.min
    end_date = fget('endDate')
    end_date = datetime.strptime(end_date, TIME_FORMAT) if end_date else datetime.max
    new_config.update({'start' : start_date})
    new_config.update({"end" : end_date})
    ticks = fget('ticks')
    if ticks and all([i in digits for i in ticks]):
        ticks, unit = int(ticks), fget('unit') or "Day(s)"
        new_config.update({'tick' : ticks * UNIT_PICKER.get(unit, UNIT_PICKER['Day(s)'])})
        new_config.update({'textual_tick' : [ticks, unit]})
    tag_search = fget('tagSearch')
    if tag_search:
        new_config.update({'tags' : tag_search.split(',')})
    color_list = []
    new_config.update({'colors' : [i for i in COLORS if fget('color-{}'.format(i)) == 'on'] or COLORS})
    new_config.update({'filter' : fget('textFilter')})
    user_config.update(new_config)
    return jsonify({'Status' : 'OKitten'})


@app.route('/updateFilters', methods=['POST'])
def update_filters():
    '''
    Gets the user advanced filters form (filtering modal) and updates the user_config
    accordingly.
    '''
    fget = request.form.get
    user_config['required_filters'] = []
    user_config['advanced_filters'] = []
    user_config['text_filters'] = []
    filter_count = int(fget('count') or 0)
    for i in range(1, filter_count + 1):
        field = fget('eventField{}'.format(i)) or ''
        text = fget('filter{}'.format(i))
        is_required = fget('required{}'.format(i), False)
        is_included = fget('include{}'.format(i)) == 'true'
        if text:
            fltr = QUERY_MATCH[field].format(txt=text)
            if not is_included:
                fltr = NOT_QUERY_MATCH[field].format(txt=text)
            user_config['text_filters'].append({
                'is_required' : is_required,
                'is_included' : is_included,
                'text' : text,
                'field' : field,
                'id' : i
                })
            if is_required:
                user_config['required_filters'].append(fltr)
            else:
                user_config['advanced_filters'].append(fltr)

    user_config['text_filters'].sort(key=(lambda x: int(x['id'])))
    user_config['required_filters'] = list(set(user_config['required_filters']))
    user_config['advanced_filters'] = list(set(user_config['advanced_filters']))
    return jsonify({'Status' : 'OKitten'})


@app.route('/getFilters')
def get_filters():
    '''
    Returns a JSONified list of all the currently used advanced filters,
    in dict form.
    '''
    return jsonify(user_config.get('text_filters'))


@app.route('/getConfig')
def get_config():
    '''
    Returns the current user_config, JSONified.
    '''
    ret_dict = {i : j for i, j in user_config.items()}
    ret_dict['tick'] = str(ret_dict['tick'])
    ret_dict['start'] = ret_dict['start'].strftime(TIME_FORMAT) if ret_dict['start'] != datetime.min else ""
    ret_dict['end'] = ret_dict['end'].strftime(TIME_FORMAT) if ret_dict['end'] != datetime.max else ""
    print(ret_dict)
    print(jsonify(ret_dict))
    return jsonify(ret_dict)


@app.route('/clearConfig')
def clear_config():
    '''
    Resets the user_config to its basic default state, removing all filters
    and restrictions.
    '''
    user_config.update(EMPTY_CONFIG)
    return jsonify({'Status' : 'OKitten'})


@app.route('/echoFilter', methods=['POST'])
def echo_filter():
    '''
    Accepts the filter form, and returns the JSONified list of dict
    filters - in order to allow saving the current form contents
    in localStorage and comfortably parse and use it later.
    '''
    fget = request.form.get
    text_filters = []
    filter_count = int(fget('count') or 0)
    for i in range(1, filter_count + 1):
        field = fget('eventField{}'.format(i)) or ''
        text = fget('filter{}'.format(i))
        is_required = fget('required{}'.format(i), False)
        is_included = fget('include{}'.format(i)) == 'true'
        if text:
            fltr = QUERY_MATCH[field].format(txt=text)
            if not is_included:
                fltr = NOT_QUERY_MATCH[field].format(txt=text)
            text_filters.append({
                'is_required' : is_required,
                'is_included' : is_included,
                'text' : text,
                'field' : field,
                'id' : i
                })

    text_filters.sort(key=(lambda x: int(x['id'])))
    return jsonify(text_filters)


def apply_filters(query):
    '''
    Accepts an SQLAlchemy query for events, and applies the currently chosen
    filters and restriction specified in the user config.
    Returns the fully filtered query.
    '''
    query = query.filter(Event.time <= user_config.get('end'))
    query = query.filter(Event.time >= user_config.get('start'))
    if not user_config.get('advanced_filters'):
        like = '%{}%'.format(user_config.get('filter'))
        query = query.filter(Event.title.ilike(like) | Event.description.ilike(like))
    else:
        filter_list = user_config['advanced_filters']
        fltr = ' | '.join(['eval("{}")'.format(i) for i in filter_list])
        f = eval(fltr)
        query = query.filter(f)

    if user_config.get('required_filters'):
        filter_list = user_config['required_filters']
        fltr = ' & '.join(['eval("{}")'.format(i) for i in filter_list])
        f = eval(fltr)
        query = query.filter(f)

    if user_config.get('tags') and user_config['tags'][0]:
        filter_list = [TAG_QUERY.format(txt=i) for i in user_config['tags']]
        fltr = ' | '.join(['eval("{}")'.format(i) for i in filter_list])
        f = eval(fltr)
        query = query.filter(f)

    if user_config.get('colors'):
        query = query.filter(Event.color.in_(user_config['colors']))

    return query

if __name__ == '__main__':
    app.run(port=PORT)
