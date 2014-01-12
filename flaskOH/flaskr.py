#imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for,\
                  abort, render_template, flash#What's flash?
from contextlib import closing

#configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True 
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#global variables
globalMode = 'time'

#creat the littlelelele application 
app = Flask(__name__)
app.config.from_object(__name__)#What does this line mean?

#connect database
def init_db():
    """Now it's possible to use a Python shell to call this funciton
    """
    with closing(connect_db()) as db:#db is a connection object
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()
    
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

#views

#def sort_cat(entries):
#    """A helper function to sort the entries according to category"""
#    for i in range(len(entries)):
#        for j in range(i + 1, len(entries)):
#            if entries[i]["category"]< entries[j]["category"]:
#                entries[i], entries[j] = entries[j], entries[i]
#    return entries
#

#@app.route('/')
#def show_entries():
#    cur = g.db.execute('select name, description, category, id from entries order by id\
#            desc')
#    entries = [dict(name = row[0], description = row[1], category = row[2], id = row[3]) for row in
#            cur.fetchall()][::-1]
#    if globalMode == "category":
#        entries = sort_cat(entries)
#    return render_template('show_entries.html', entries=entries)

@app.route('/')
def show_entries():
    print('Here is the show_entries')
    cur = g.db.execute('select name, description, category, id, position from entries order by position')
    #this select the columns of name, description, category and position from the table with the ascending position order
    entries = [dict(name = row[0], description = row[1], category = row[2],\
        id = row[3], position = row[4]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

#@app.route('/entries')
#def entries():
#    cur = g.db.execute('select name, description, category, id from entries order by id\
#            desc')
#    entries = [dict(name = row[0], description = row[1], category = row[2], id = row[3]) for row in
#            cur.fetchall()][::-1]
#    if globalMode == "category":
#        entries = sort_cat(entries)
#    return render_template('entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    countTable = g.db.execute('select count(*) from entries').fetchall()
    #count(*) gives a 1*1 table representing the total number of entries
    #fetchall() converts the database table to a tuple within list
    #Ex: when there are 3 entries, fetall get [(3,)]
    position = 1 + countTable[0][0]
    g.db.execute('insert into entries (name, description, category, position) values (?, ?, ?, ?)',
                [request.form['name'], request.form['description'],
                    request.form['category'], position])
    g.db.commit()
    flash('New entry was succesfully posted')
    return redirect(url_for('show_entries'))

@app.route('/delete')
def general_delete_entry():
    """
    deletes the first entry in the queue
    """
    if not session.get('logged_in'):
         abort(401)
    g.db.execute('delete from entries where position=1') 
    # this delete the entry with the position 1 in the queue, namely the first entry
    g.db.execute('update entries set position=position-1')
    g.db.commit()
    flash('The first entry was deleted')
    return redirect(url_for('show_entries'))

@app.route('/delete/<int:entry_id>')
def delete_entry(entry_id):
    if not session.get('logged_in'):
         abort(401)
    row = g.db.execute('select id, position from entries where id=?',[entry_id]).fetchall()[0]
    entry = dict(id = row[0], position = row[1])
    g.db.execute('delete from entries where id=?',[entry_id])
    g.db.execute('update entries set position=position-1 where position>?',\
        [entry['position']])
    g.db.commit()
    flash('The indicated entry was deleted')
    return redirect(url_for('show_entries'))

@app.route('/reorder', methods=['POST'])
def reorder_entry():
    if not session.get('logged_in'):
        abort(401)
    #form (id, current_position) pairs, preparing for changing the database
    pos, pairs = 0, []
    print('----------After reordering--------')
    for ele in request.json:
        pos += 1
        id = int(ele)#json stores the list of entries' ids in unicode
        pairs.append((id, pos))
        print(id, pos)
    #for every "id","pos" in pairs, select the entry with the "id" and update its position to the "pos"
    for id, pos in pairs:
        g.db.execute('update entries set position=? where id=?',[pos, id])
    g.db.commit()

    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/changemode/<mode>')
def changemode(mode):
    global globalMode
    globalMode = mode
    return redirect(url_for('show_entries'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
if __name__ == '__main__':
    app.run()#host='0.0.0.0'!!!debug mode False

