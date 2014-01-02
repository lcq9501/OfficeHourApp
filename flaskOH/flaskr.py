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
#g.mode = 'Time'
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

#view
def sort_cat(entries):
    """A helper function to sort the entries according to category"""
    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            if entries[i]["category"]< entries[j]["category"]:
                entries[i], entries[j] = entries[j], entries[i]
    return entries

@app.route('/')
def show_entries():
    cur = g.db.execute('select name, description, category, id from entries order by id\
            desc')
    entries = [dict(name = row[0], description = row[1], category = row[2], id = row[3]) for row in
            cur.fetchall()][::-1]
    if globalMode == "category":
        entries = sort_cat(entries)
    return render_template('show_entries.html', entries=entries)

@app.route('/entries')
def entries():
    cur = g.db.execute('select name, description, category, id from entries order by id\
            desc')
    entries = [dict(name = row[0], description = row[1], category = row[2], id = row[3]) for row in
            cur.fetchall()][::-1]
    if globalMode == "category":
        entries = sort_cat(entries)
    return render_template('entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (name, description, category) values (?, ?, ?)',
                [request.form['name'], request.form['description'],
                    request.form['category']])
    g.db.commit()
    flash('New entry was succesfully posted')
    return redirect(url_for('show_entries'))

@app.route('/delete')
def general_delete_entry():
    if not session.get('logged_in'):
         abort(401)
    g.db.execute('delete from entries where id=(select min(id)from entries)') 
    g.db.commit()
    flash('The entry was deleted')
    return redirect(url_for('show_entries'))

@app.route('/delete/<int:entry_id>')
def delete_entry(entry_id):
    if not session.get('logged_in'):
         abort(401)
    g.db.execute('delete from entries where id=' + str(entry_id))
    g.db.commit()
    flash('The entry was deleted')
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

