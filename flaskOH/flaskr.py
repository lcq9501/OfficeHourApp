#imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for,\
                  abort, render_template, flash#What's flash?
from contextlib import closing

#configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True 
SECRET_KEY = 'development key'
USERNAME = 'lcq9501'
PASSWORD = 'Sundae1995'

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
@app.route('/')
def show_entries():
    cur = g.db.execute('select name, description, category from entries order by id\
            desc')
    entries = [dict(name = row[0], description = row[1], category = row[2]) for row in
            cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

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
def delete_entry():
    if not session.get('logged_in'):
         abort(401)
    g.db.execute('delete from entries where id=(select max(id)from entries)') 
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

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))
if __name__ == '__main__':
    app.run()#host='0.0.0.0'!!!debug mode False

